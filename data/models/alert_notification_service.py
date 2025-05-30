"""Simple asynchronous alert notification helper."""

from ..models_core import Alert, AlertLevel


class NotificationService:
    def __init__(self, sms_client, email_client):
        self.sms_client = sms_client
        self.email_client = email_client

    async def send_alert(self, alert: Alert):
        if alert.level in [AlertLevel.MEDIUM, AlertLevel.HIGH]:
            await self.sms_client.send(f"Alert triggered: {alert}")
        else:
            await self.email_client.send(f"Alert triggered: {alert}")
