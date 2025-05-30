# xcom/email_service.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import smtplib, ssl
from email.mime.text import MIMEText
from core.logging import log

class EmailService:
    def __init__(self, config: dict):
        self.config = config

    def send(self, to: str, subject: str, body: str) -> bool:
        if not self.config.get("enabled"):
            log.warning("Email provider disabled", source="EmailService")
            return False

        smtp_cfg = self.config.get("smtp", {})
        server, port, username, password = map(smtp_cfg.get, ["server", "port", "username", "password"])
        to = to or smtp_cfg.get("default_recipient")

        if not all([server, port, username, password, to]):
            log.error("Missing email configuration", source="EmailService")
            return False

        try:
            msg = MIMEText(body, "plain")
            msg["Subject"], msg["From"], msg["To"] = subject, username, to
            ctx = ssl.create_default_context()
            with smtplib.SMTP(server, port) as smtp:
                smtp.starttls(context=ctx)
                smtp.login(username, password)
                smtp.send_message(msg)
            log.success("Email sent", source="EmailService", payload={"to": to})
            return True
        except Exception as e:
            log.error(f"Email send failed: {e}", source="EmailService")
            return False
