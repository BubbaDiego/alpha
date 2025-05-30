import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import asyncio
import logging
from datetime import datetime
from uuid import uuid4
import traceback  # PATCH: for full stack info

from data.data_locker import DataLocker
from core.constants import DB_PATH, ALERT_THRESHOLDS_PATH
from alert_core.alert_utils import load_alert_thresholds_from_file
from core.logging import log, configure_console_log

# PATCH: Import SystemCore for death screams
from system.system_core import SystemCore

# Cores and Services
from alert_core.alert_core import AlertCore
from monitor.monitor_core import MonitorCore
from positions.position_core import PositionCore
from prices.price_sync_service import PriceSyncService
from cyclone.cyclone_maintenance_service import CycloneMaintenanceService
from cyclone.cyclone_wallet_service import CycloneWalletService
from data.dl_monitor_ledger import DLMonitorLedgerManager
from hedge_core.hedge_core import HedgeCore


global_data_locker = DataLocker(str(DB_PATH))  # There can be only one

def configure_cyclone_console_log(debug: bool = False):
    """Centralized Cyclone Console Log Config

    Parameters
    ----------
    debug : bool, optional
        When ``True`` the underlying logger is configured for verbose output.
    """
    configure_console_log(debug=debug)
    log.silence_module("werkzeug")
    log.silence_module("fuzzy_wuzzy")

    # Hijack asyncio logger early
    log.hijack_logger("asyncio")

    # Optionally silence it altogether
    log.silence_module("asyncio")

    log.assign_group("cyclone_core", [
        # Core engine & service modules
        "cyclone_engine", "Cyclone",
        "CycloneHedgeService", "CyclonePortfolioService",
        "CycloneAlertService", "CyclonePositionService",

        # Deep services
        "PositionSyncService", "PositionCoreService", "PositionEnrichmentService",
        "AlertEvaluator", "AlertController", "AlertServiceManager",

        # Data & Utility modules
        "DataLocker", "PriceSyncService", "DBCore", "Logger", "AlertUtils",
        "CalcServices", "LockerFactory",

        # Experimental or custom
        "HedgeManager", "CycleRunner", "ConsoleHelper"
    ])

    log.enable_group("cyclone_core")
    log.init_status()


class Cyclone:
    def __init__(self, monitor_core=None, poll_interval=60, debug: bool = False):
        configure_cyclone_console_log(debug=debug)
        self.logger = logging.getLogger("Cyclone")
        self.poll_interval = poll_interval
        if debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)
        self.monitor_core = monitor_core or MonitorCore()

        self.data_locker = global_data_locker
        self.price_sync = PriceSyncService(self.data_locker)

        # PATCH: Create a system_core instance for death screams
        self.system_core = SystemCore(self.data_locker)

        self.config = self.data_locker.system.get_var("alert_thresholds")
        if not self.config:
            log.warning(
                "⚠️ alert_thresholds missing from DB. Loading from JSON...",
                source="Cyclone",
            )
            try:
                self.config = load_alert_thresholds_from_file(self.data_locker)
            except Exception as exc:
                self.system_core.death(
                    {
                        "message": "🛑 alert_thresholds missing and failed to load",
                        "level": "HIGH",
                        "payload": {"error": str(exc)},
                    }
                )
                raise RuntimeError(
                    "🛑 alert_thresholds missing from DB and file load failed"
                )

        self.position_core = PositionCore(self.data_locker)
        # Pass alert thresholds config to AlertCore so alert creation respects
        # the "enabled" flags defined in alert_thresholds.json
        self.alert_core = AlertCore(
            self.data_locker,
            config_loader=lambda: self.config,
        )
        self.wallet_service = CycloneWalletService(self.data_locker)
        self.maintenance_service = CycloneMaintenanceService(self.data_locker)
        self.hedge_core = HedgeCore(self.data_locker)

        log.banner("🌀  🌪️ CYCLONE ENGINE STARTUP 🌪️ 🌀")

    async def run_market_updates(self):
        log.info("Starting Market Updates", source="Cyclone")
        try:
            result = await asyncio.to_thread(self.price_sync.run_full_price_sync, source="Cyclone")
            if result.get("success"):
                log.success("📈 Prices updated successfully ✅", source="Cyclone")
            else:
                log.warning(f"⚠️ Price update failed: {result.get('error')}", source="Cyclone")
        except Exception as e:
            log.error(f"📉 Market Updates crashed: {e}", source="Cyclone")

    async def run_position_updates(self):
        """Sync positions from Jupiter wallets."""
        log.info("Starting Position Updates", source="Cyclone")
        try:
            await asyncio.to_thread(self.position_core.update_positions_from_jupiter)
            log.success("🪐 Position updates completed", source="Cyclone")
        except Exception as e:
            log.error(f"Position Updates crashed: {e}", source="Cyclone")

    async def run_composite_position_pipeline(self):
        await asyncio.to_thread(self.position_core.update_positions_from_jupiter)

    async def run_create_market_alerts(self):
        """Create global market alerts via AlertCore."""
        await asyncio.to_thread(self.alert_core.create_global_alerts)

    async def run_clear_all_data(self):
        log.warning("⚠️ Starting Clear All Data", source="Cyclone")
        try:
            await asyncio.to_thread(self._clear_all_data_core)
            log.success("All alerts, prices, and positions have been deleted.", source="Cyclone")
        except Exception as e:
            log.error(f"Clear All Data failed: {e}", source="Cyclone")

    def run_debug_position_update(self):
        print("💡 DEBUG: calling CyclonePositionService.update_positions_from_jupiter()")
        self.position_core.update_positions_from_jupiter()

    # PATCH: Wrap each run step in try/except and call death on terminal error
    async def run_cycle(self, steps=None):
        available_steps = {
           # "clear_all_data": self.run_clear_all_data,
            "update_operations": self.run_operations_update,
            "market_updates": self.run_market_updates,
            "check_jupiter_for_updates": self.run_check_jupiter_for_updates,
            "enrich_positions": self.run_enrich_positions,
            "enrich_alerts": self.run_alert_enrichment,
            "update_evaluated_value": self.run_update_evaluated_value,
            "create_market_alerts": self.run_create_market_alerts,
            "create_portfolio_alerts": self.run_create_portfolio_alerts,
            "create_position_alerts": self.run_create_position_alerts,
            "create_global_alerts": self.run_create_global_alerts,
            "evaluate_alerts": self.run_alert_evaluation,
            "cleanse_ids": self.run_cleanse_ids,
            "link_hedges": self.run_link_hedges,
            "update_hedges": self.run_update_hedges,
        }

        # Maintain the declared order as the standard run sequence
        default_steps = list(available_steps.keys())

        steps = steps or default_steps

        for step in steps:
            if step not in available_steps:
                log.warning(f"⚠️ Unknown step: '{step}'", source="Cyclone")
                continue
            log.info(f"▶️ Running step: {step}", source="Cyclone")
            try:
                await available_steps[step]()
            except Exception as e:
                log.error(f"💀 Terminal failure during step '{step}': {e}", source="Cyclone")
                self.system_core.death({
                    "message": f"💀 Cyclone terminal failure during step '{step}'",
                    "level": "HIGH",
                    "payload": {
                        "step": step,
                        "error": str(e),
                        "traceback": traceback.format_exc()
                    }
                })
                raise  # Optionally re-raise if you want to halt further steps

    def run_delete_all_data(self):
        log.warning("⚠️ Deletion requested via legacy method (run_delete_all_data)", source="Cyclone")
        asyncio.run(self.run_clear_all_data())


    async def run_link_hedges(self):
        self.hedge_core.link_hedges()

    async def run_update_hedges(self):
        await asyncio.to_thread(self.hedge_core.update_hedges)

    async def run_alert_evaluation(self):
        await self.alert_core.run_alert_evaluation()

    async def run_create_position_alerts(self):
        self.alert_core.create_position_alerts()

    async def run_create_portfolio_alerts(self):
        self.alert_core.create_portfolio_alerts()

    async def run_create_global_alerts(self):
        """Generate default global market alerts."""
        await asyncio.to_thread(self.alert_core.create_global_alerts)

    def clear_alerts_backend(self):
        """Clear all alerts using :class:`CycloneMaintenanceService`."""
        self.maintenance_service.clear_alerts()

    async def run_cleanse_ids(self):
        log.info("🧹 Running cleanse_ids: clearing stale alerts", source="Cyclone")
        self.alert_core.clear_stale_alerts()
        log.success("✅ Alert IDs cleansed", source="Cyclone")

    async def run_enrich_positions(self):
        await self.position_core.enrich_positions()
        log.success("✅ Position enrichment complete", source="Cyclone")

    async def run_alert_enrichment(self):
        await self.alert_core.enrich_all_alerts()
        log.success("✅ Alert enrichment complete", source="Cyclone")

    async def run_update_evaluated_value(self):
        await self.alert_core.update_evaluated_values()
        log.success("✅ Evaluated alert values updated", source="Cyclone")

    # ⚙️ Corrected clear helpers
    def clear_prices_backend(self):
        self.maintenance_service.clear_prices()

    def clear_wallets_backend(self):
        self.maintenance_service.clear_wallets()

    def add_wallet_backend(self):
        """Interactively add a wallet via :class:`CycloneWalletService`."""
        self.wallet_service.add_wallet_interactive()

    def view_wallets_backend(self):
        """Display all wallets using :class:`CycloneWalletService`."""
        self.wallet_service.view_wallets()

    def clear_positions_backend(self):
        self.maintenance_service.clear_positions()

    def _clear_all_data_core(self):
        self.maintenance_service.clear_all_tables()

    async def run_check_jupiter_for_updates(self):
        log.info("Checking Jupiter/Positions via MonitorCore", source="Cyclone")
        await asyncio.to_thread(self.monitor_core.run_by_name, "position_monitor")

    async def run_operations_update(self):
        log.info("Starting Operations Monitor via MonitorCore", source="Cyclone")
        await asyncio.to_thread(self.monitor_core.run_by_name, "operations_monitor")

        # Refresh alert limits configuration from the database each cycle. The
        # OperationsMonitor will update the DB entry when the source file
        # changes. Reloading here keeps ``self.config`` in sync for AlertCore.
        new_config = self.data_locker.system.get_var("alert_thresholds") or {}
        if new_config:
            self.config = new_config

    async def run_system_updates(self):
        """Run system-level update tasks."""
        log.info("Starting system updates", source="Cyclone")
        try:
            await self.run_operations_update()
            log.success("✅ System updates completed", source="Cyclone")
        except Exception as e:
            log.error(f"System updates failed: {e}", source="Cyclone")

    async def enrich_positions(self):
        log.info("🚀 Enriching All Positions via PositionCore...", "Cyclone")
        await self.position_core.enrich_positions()
        log.success("✅ Position enrichment complete.", "Cyclone")
