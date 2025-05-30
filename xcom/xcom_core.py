# xcom/xcom_core.py
import sys
import os
import json
from datetime import datetime
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from xcom.xcom_config_service import XComConfigService
from xcom.email_service import EmailService
from xcom.sms_service import SMSService
from xcom.voice_service import VoiceService
from xcom.sound_service import SoundService
from data.data_locker import DataLocker
from core.logging import log

class XComCore:
    def __init__(self, dl_sys_data_manager):
        self.config_service = XComConfigService(dl_sys_data_manager)
        self.log = []

    def send_notification(
            self, level: str, subject: str, body: str, recipient: str = "",
            initiator: str = "system"
    ):
        """
        Dispatches a notification (SMS, email, voice, etc) and writes all info to the monitor ledger,
        always including an explicit 'initiator' field in the metadata.
        """
        email_cfg = self.config_service.get_provider("email") or {}
        sms_cfg = self.config_service.get_provider("sms") or {}
        voice_cfg = self.config_service.get_provider("api") or {}

        results = {"email": False, "sms": False, "voice": False, "sound": None}
        error_msg = None

        try:
            if level == "HIGH":
                results["sms"] = SMSService(sms_cfg).send(recipient, body)
                results["voice"] = VoiceService(voice_cfg).call(recipient, body)
                results["sound"] = SoundService().play()
            elif level == "MEDIUM":
                results["sms"] = SMSService(sms_cfg).send(recipient, body)
            else:
                results["email"] = EmailService(email_cfg).send(recipient, subject, body)

            log.success(f"✅ Notification dispatched [{level}]", source="XComCore", payload=results)

        except Exception as e:
            error_msg = str(e)
            results["error"] = error_msg
            log.error(f"❌ Failed to send XCom notification: {e}", source="XComCore")

        # Log to self (class)
        self.log.append({
            "level": level,
            "subject": subject,
            "initiator": initiator,
            "recipient": recipient,
            "body": body,
            "results": results
        })

        # Determine overall success and log to ledger with initiator
        success = any(v is True for v in results.values()) and error_msg is None

        try:
            from data.data_locker import DataLocker
            from core.constants import DB_PATH
            from data.dl_monitor_ledger import DLMonitorLedgerManager

            dl = DataLocker(DB_PATH)
            ledger = DLMonitorLedgerManager(dl.db)

            metadata = {
                "level": level,
                "subject": subject,
                "initiator": initiator,
                "recipient": recipient,
                "results": results
            }
            ledger.insert_ledger_entry(
                "xcom_monitor",
                "Success" if success else "Error",
                metadata,
            )

        except Exception as e:
            log.error(f"🧨 Failed to write xcom_monitor ledger: {e}", source="XComCore")

        # Include success flag in return payload for monitor use
        results["success"] = success
        return results


def get_latest_xcom_monitor_entry(data_locker):
    # Import your ledger manager from the data locker
    ledger_mgr = data_locker.monitor_ledger if hasattr(data_locker, "monitor_ledger") else data_locker.ledger
    entry = ledger_mgr.get_last_entry("xcom_monitor")
    if not entry:
        return {
            "comm_type": "system",
            "source": "system",
            "timestamp": "—"
        }
    # Parse metadata safely
    meta = entry.get("metadata")
    if isinstance(meta, str):
        try:
            meta = json.loads(meta)
        except Exception:
            meta = {}
    results = meta.get("results", {}) or {}
    # Detect comm_type: use priority order for true values
    comm_types = [("sms", "sms"), ("voice", "voice"), ("email", "email"), ("sound", "sound")]
    comm_type = "system"
    for key, value in comm_types:
        if results.get(key):
            comm_type = key
            break
    if comm_type == "system" and meta.get("level", "").lower() == "high":
        comm_type = "alert"
    # Detect source
    subject = (meta.get("subject") or "").lower()
    if "alert" in subject:
        source = "alert"
    elif "user" in subject:
        source = "user"
    elif "operations" in subject or "op" in subject:
        source = "operations"
    else:
        source = "system"
    # Format timestamp as "3:58 PM" (localize as needed)
    ts = entry.get("timestamp")
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00")) if ts else None
        if dt:
            ts = dt.strftime("%-I:%M %p").replace(" 0", " ")  # e.g. "3:58 PM"
    except Exception:
        pass
    return {
        "comm_type": comm_type,
        "source": source,
        "timestamp": ts or "—"
    }


