# cyclone/services/system_maintenance_service.py

from core.logging import log

class CycloneMaintenanceService:
    def __init__(self, data_locker):
        self.dl = data_locker

    def clear_alerts(self):
        try:
            self.dl.alerts.clear_all_alerts()
            log.success("🧹 All alerts cleared", source="SystemMaintenanceService")
        except Exception as e:
            log.error(f"❌ Failed to clear alerts: {e}", source="SystemMaintenanceService")

    def clear_prices(self):
        try:
            self.dl.prices.clear_prices()
            log.success("🧹 All prices cleared", source="SystemMaintenanceService")
        except Exception as e:
            log.error(f"❌ Failed to clear prices: {e}", source="SystemMaintenanceService")

    def clear_positions(self):
        try:
            self.dl.positions.clear_positions()
            log.success("🧹 All positions cleared", source="SystemMaintenanceService")
        except Exception as e:
            log.error(f"❌ Failed to clear positions: {e}", source="SystemMaintenanceService")

    def clear_wallets(self):
        try:
            self.dl.wallets.clear_wallets()
            log.success("🧹 All wallets cleared", source="SystemMaintenanceService")
        except Exception as e:
            log.error(f"❌ Failed to clear wallets: {e}", source="SystemMaintenanceService")

    def clear_all_tables(self):
        success = {
            "alerts": False,
            "prices": False,
            "positions": False,
            # "wallets": False  # Add if needed
        }

        try:
            self.clear_alerts()
            success["alerts"] = True
        except Exception as e:
            log.error(f"❌ Alerts clear failed: {e}", source="SystemMaintenanceService")

        try:
            self.clear_prices()
            success["prices"] = True
        except Exception as e:
            log.error(f"❌ Prices clear failed: {e}", source="SystemMaintenanceService")

        try:
            self.clear_positions()
            success["positions"] = True
        except Exception as e:
            log.error(f"❌ Positions clear failed: {e}", source="SystemMaintenanceService")

        # Final summary
        if all(success.values()):
            log.success("✅ Full system wipe complete.", source="SystemMaintenanceService")
        else:
            failed = [k for k, v in success.items() if not v]
            log.warning(f"⚠️ Partial wipe — failed to clear: {', '.join(failed)}", source="SystemMaintenanceService")
