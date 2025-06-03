import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from prices.price_sync_service import PriceSyncService
from data.data_locker import DataLocker
from monitor.base_monitor import BaseMonitor
from monitor.monitor_service import MonitorService
from core.core_imports import DB_PATH

from datetime import datetime, timezone
from core.logging import log


class PriceMonitor(BaseMonitor):
    """
    Fetches prices from external APIs and stores them in DB.
    Uses CoinGecko via MonitorService.
    """

    def __init__(self):
        super().__init__(
            name="price_monitor",
            ledger_filename="price_ledger.json",  # still optional, safe to retain
            timer_config_path=None  # leave in for compatibility
        )
        self.dl = DataLocker(str(DB_PATH))
        self.service = MonitorService()



    def _do_work(self):
        return PriceSyncService(self.dl).run_full_price_sync(source="price_monitor")


if __name__ == "__main__":
    log.banner("🚀 SELF-RUN: PriceMonitor")

    monitor = PriceMonitor()
    result = monitor.run_cycle()

    log.success("🧾 PriceMonitor Run Complete", source="SelfTest", payload=result)
