# xcom/voice_service.py
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests  # noqa: F401  # retained for backward compatibility
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse

from core.logging import log
from flask import current_app



class VoiceService:
    def __init__(self, config: dict):
        self.config = config

    def call(self, recipient: str, message: str) -> bool:
        """Initiate a Twilio voice call using ``message`` as spoken text."""
        try:
            account_sid = self.config.get("account_sid") or os.getenv("TWILIO_ACCOUNT_SID")
            auth_token = self.config.get("auth_token") or os.getenv("TWILIO_AUTH_TOKEN")
            from_phone = self.config.get("default_from_phone") or os.getenv("TWILIO_FROM_PHONE")
            to_phone = recipient or self.config.get("default_to_phone") or os.getenv("TWILIO_TO_PHONE")

            if not all([account_sid, auth_token, from_phone, to_phone]):
                log.error("Missing Twilio voice configuration", source="VoiceService")
                return False

            client = Client(account_sid, auth_token)
            vr = VoiceResponse()
            vr.say(message or "Hello from XCom.", voice="alice")

            call = client.calls.create(twiml=str(vr), to=to_phone, from_=from_phone)

            log.info(
                "🔍 Twilio Voice request debug",
                payload={"sid": call.sid, "to": to_phone, "from": from_phone},
                source="VoiceService",
            )

            return True

        except Exception as e:
            log.error(f"Voice call failed: {e}", source="VoiceService")
            if hasattr(current_app, "system_core"):
                current_app.system_core.death(
                    {
                        "message": f"Twilio Voice Call failed: {e}",
                        "payload": {"provider": "twilio", "to": to_phone, "from": from_phone},
                        "level": "HIGH",
                    }
                )
            return False

