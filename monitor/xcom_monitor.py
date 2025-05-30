import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from monitor.base_monitor import BaseMonitor
from data.data_locker import DataLocker
from xcom.xcom_core import XComCore
from core.core_imports import DB_PATH
from core.logging import log


class XComMonitor(BaseMonitor):
    """Simple monitor to send a lightweight XCom notification."""

    def __init__(self):
        super().__init__(name="xcom_monitor", ledger_filename="xcom_ledger.json")
        self.dl = DataLocker(str(DB_PATH))
        self.xcom = XComCore(self.dl)

    def _do_work(self):
        log.info("📡 Sending XCom monitor ping", source="XComMonitor")
        result = self.xcom.send_notification(
            level="LOW",
            subject="XCom Monitor Ping",
            body="XCom monitor cycle notification",
            initiator="monitor"
        )
        return result
