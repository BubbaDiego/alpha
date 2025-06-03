import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from monitor.base_monitor import BaseMonitor
from data.data_locker import DataLocker
from positions.position_core import PositionCore
from core.core_imports import DB_PATH
from datetime import datetime, timezone
from core.logging import log

class PositionMonitor(BaseMonitor):
    """
    Actively syncs positions from Jupiter and logs summary.
    """
    def __init__(self):
        super().__init__(name="position_monitor", ledger_filename="position_ledger.json")
        self.dl = DataLocker(str(DB_PATH))
        self.core = PositionCore(self.dl)

    def _do_work(self):
        log.info("🔄 Starting position sync", source="PositionMonitor")
        sync_result = self.core.update_positions_from_jupiter(source="position_monitor")

        # 📦 Return key sync info for display/logging
        return {
            "imported": sync_result.get("imported", 0),
            "skipped": sync_result.get("skipped", 0),
            "errors": sync_result.get("errors", 0),
            "hedges": sync_result.get("hedges", 0),
            "timestamp": sync_result.get("timestamp", datetime.now(timezone.utc).isoformat())
        }

# ✅ Self-execute entrypoint
if __name__ == "__main__":
    log.banner("🚀 SELF-RUN: PositionMonitor")
    monitor = PositionMonitor()
    result = monitor.run_cycle()
    log.success("🧾 PositionMonitor Run Complete", source="SelfTest", payload=result)
    log.banner("✅ Position Sync Finished")
