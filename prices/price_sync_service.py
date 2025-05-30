# services/price_sync_service.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.logging import log
from monitor.monitor_service import MonitorService
from data.dl_monitor_ledger import DLMonitorLedgerManager
from datetime import datetime, timezone


class PriceSyncService:
    def __init__(self, data_locker):
        self.dl = data_locker
        self.service = MonitorService()

    def run_full_price_sync(self, source="user") -> dict:
        from datetime import datetime, timezone
        from data.dl_monitor_ledger import DLMonitorLedgerManager

        log.banner("📈 Starting Price Sync")
        log.info("Initiating sync workflow...", source="PriceSyncService")

        try:
            now = datetime.now(timezone.utc)
            prices = self.service.fetch_prices()

            if not prices:
                log.warning("⚠️ No prices fetched", source="PriceSyncService")
                result = {
                    "fetched_count": 0,
                    "assets": [],
                    "success": False,
                    "error": "No prices returned from service",
                    "timestamp": now.isoformat()
                }
                self._write_ledger(result, "Error")
                return result

            asset_list = []
            for asset, price in prices.items():
                self.dl.insert_or_update_price(asset, price, source=source)
                log.info(f"💾 Saved {asset} = ${price:,.4f}", source="PriceSyncService")
                asset_list.append(asset)

            result = {
                "fetched_count": len(prices),
                "assets": asset_list,
                "success": True,
                "timestamp": now.isoformat()
            }

            log.success("✅ Price sync complete", source="PriceSyncService", payload={
                "count": len(prices),
                "assets": asset_list
            })

            self._write_ledger(result, "Success")
            log.banner("✅ Price Sync Completed")
            return result

        except Exception as e:
            error_message = str(e)
            log.error(f"❌ Price sync failed: {error_message}", source="PriceSyncService")

            result = {
                "fetched_count": 0,
                "assets": [],
                "success": False,
                "error": error_message,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            self._write_ledger(result, "Error")
            return result

    def _write_ledger(self, result: dict, status: str):
        try:
            ledger = DLMonitorLedgerManager(self.dl.db)
            ledger.insert_ledger_entry("price_monitor", status, metadata=result)
            log.info("🧾 Price ledger updated", source="PriceSyncService")
        except Exception as e:
            log.warning(f"⚠️ Ledger write failed: {e}", source="PriceSyncService")

