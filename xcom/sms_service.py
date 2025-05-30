# xcom/sms_service.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from xcom.email_service import EmailService
from core.logging import log

class SMSService:
    def __init__(self, config: dict):
        self.config = config
        self.email_service = EmailService(config)  # reuse email transport

    def send(self, to: str, body: str) -> bool:
        if not self.config.get("enabled"):
            log.warning("SMS provider disabled", source="SMSService")
            return False

        gateway = self.config.get("carrier_gateway")
        to = to or self.config.get("default_recipient")
        if not (gateway and to):
            log.error("Missing SMS config", source="SMSService")
            return False

        sms_email = f"{to}@{gateway}"
        return self.email_service.send(sms_email, "", body)
