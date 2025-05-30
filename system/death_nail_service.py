import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import os
import asyncio
from datetime import datetime
from xcom.sound_service import SoundService
from core.logging import log
import asyncio


class DeathNailService:
    def __init__(self, logger, xcom_core=None, log_path="death_log.txt", default_level="HIGH", default_recipient="admin@example.com"):
        self.logger = logger
        self.xcom = xcom_core
        self.log_path = log_path
        self.level = default_level
        self.recipient = default_recipient
        self._death_active = False

    def trigger(self, metadata: dict):
        if self._death_active:
            self.logger.warning("⚠️ Death nail suppressed to prevent recursion", source="DeathNail")
            return

        self._death_active = True

        try:
            message = metadata.get("message", "💀 Fatal error")
            level = metadata.get("level", self.level)
            recipient = metadata.get("recipient", self.recipient)
            payload = metadata.get("payload", {})

            timestamp = datetime.now().isoformat()
            entry = {
                "timestamp": timestamp,
                "message": message,
                "payload": payload,
                "level": level
            }

            # 💀 1. Console log
            self.logger.death(message, payload=payload)

            # 🔊 2. Play death spiral sound
            try:
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                abs_path = os.path.join(base_dir, "static", "sounds", "death_spiral.mp3")
                SoundService().play(abs_path)
            except Exception as e:
                self.logger.warning(f"⚠️ Death spiral sound failed: {e}", source="DeathNail")

            # 📁 3. Log to file
            try:
                with open(self.log_path, "a") as f:
                    f.write(json.dumps(entry) + "\n")
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to write death log: {e}", source="DeathNail")

            # 📡 4. Optional escalation
            if self.xcom and hasattr(self.xcom, "send_notification"):
                try:
                    api_cfg = self.xcom.config_service.get_provider("api") or {}
                    if not api_cfg.get("account_sid"):
                        raise Exception("API config missing or incomplete")

                    self.xcom.send_notification(
                        level=level,
                        subject="💀 Fatal Error Triggered",
                        body=message,
                        recipient=recipient,
                        initiator="SystemCore"
                    )

                except Exception as e:
                    self.logger.warning(f"⚠️ XCom escalation failed: {e}", source="DeathNail")


            # 🚨 5. Create system alert via AlertCore
            if self.xcom and hasattr(self.xcom, "alert_core"):
                try:
                    alert_payload = {
                        "alert_type": "DeathNail",
                        "alert_class": "System",
                        "evaluated_value": 1.0,
                        "trigger_value": 1.0,
                        "condition": "ABOVE",
                    }
                    created = asyncio.run(self.xcom.alert_core.create_alert(alert_payload))
                    if not created:
                        self.logger.warning("⚠️ Failed to create DeathNail alert", source="DeathNail")
                except Exception as e:
                    self.logger.warning(f"⚠️ Alert creation failed: {e}", source="DeathNail")


        finally:
            self._death_active = False


# 🔥 RUNNABLE ENTRYPOINT
if __name__ == "__main__":
    service = DeathNailService(logger=log)
    service.trigger({
        "message": "💀 CLI death nail test",
        "payload": {
            "trigger": "manual CLI",
            "reason": "you ran the file directly"
        },
        "level": "HIGH"
    })
