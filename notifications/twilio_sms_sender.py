import os
from core.logging import log

try:  # pragma: no cover - optional dependency
    from twilio.rest import Client  # type: ignore
except Exception as e:  # pragma: no cover - import may fail
    Client = None  # type: ignore
    log.warning(
        f"Twilio client unavailable: {e}", source="TwilioSMSSender"
    )

class TwilioSMSSender:
    """Simple wrapper around the Twilio REST client for SMS."""

    def __init__(self, account_sid=None, auth_token=None, from_phone=None):
        self.account_sid = account_sid or os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = auth_token or os.getenv("TWILIO_AUTH_TOKEN")
        self.from_phone = (
            from_phone
            or os.getenv("TWILIO_FROM_PHONE")
            or os.getenv("TWILIO_FROM_NUMBER")
        )

        if Client:
            self.client = Client(self.account_sid, self.auth_token)
        else:  # pragma: no cover - if optional dependency missing
            self.client = None

    def send_sms(self, to_number: str, message: str) -> bool:
        """Send an SMS message via Twilio."""
        if not self.client:
            log.error("Twilio Client not initialized", source="TwilioSMSSender")
            return False
        try:
            if not all([self.account_sid, self.auth_token, self.from_phone, to_number]):
                log.error("Missing Twilio SMS configuration", source="TwilioSMSSender")
                return False

            msg = self.client.messages.create(body=message, from_=self.from_phone, to=to_number)
            log.info(
                "✅ SMS sent",
                source="TwilioSMSSender",
                payload={"sid": getattr(msg, "sid", None)}
            )
            return True
        except Exception as e:
            log.error(f"❌ Failed to send SMS: {e}", source="TwilioSMSSender")
            return False

