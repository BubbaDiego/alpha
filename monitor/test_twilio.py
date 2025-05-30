__test__ = False
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.data_locker import DataLocker
from xcom.xcom_core import XComCore
from core.constants import DB_PATH
from core.logging import log

# ---- NEW: Import your Flask app ----
try:
    from sonic_app import app   # Adjust import if needed
except Exception:  # pragma: no cover - optional dependency
    app = None

def run_test_call():
    # 📦 Load DataLocker + XComCore
    dl = DataLocker(DB_PATH)
    xcom = XComCore(dl.system)

    # 🧪 Send test HIGH-level notification (Voice + SMS + Sound)
    level = "HIGH"
    subject = "Test Voice Notification"
    body = "📞 This is a test voice call via Sonic XComCore."

    log.info("🔁 Dispatching XCom test via send_notification()", source="TestScript")
    result = xcom.send_notification(level, subject, body)

    print("Dispatch Result:", result)

if __name__ == "__main__":
    with app.app_context():
        run_test_call()
