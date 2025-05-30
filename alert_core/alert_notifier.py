from data.alert import NotificationType
from notifications.twilio_sms_sender import TwilioSMSSender
from core.logging import log
import os


class AlertNotifier:
    """Dispatch notifications for evaluated alerts."""

    def __init__(self, data_locker):
        self.data_locker = data_locker
        self.sms_sender = TwilioSMSSender()

    def notify(self, alert):
        """Send notifications based on alert configuration."""
        if alert.notification_type == NotificationType.SMS:
            phone_number = (
                self.data_locker.system.get_var("alert_sms_number")
                or os.getenv("ALERT_SMS_NUMBER")
            )
            message = (
                f"🚨 Alert Triggered: {alert.description}\n"
                f"Level: {alert.level}\n"
                f"Value: {alert.evaluated_value}"
            )
            if not phone_number:
                log.error("No alert_sms_number configured", source="AlertNotifier")
                return False
            return self.sms_sender.send_sms(str(phone_number), message)
        return False
