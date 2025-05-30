import os
import importlib
import pytest

from utils import startup_service as ss


def test_startup_fails_without_openai_api_key(monkeypatch):
    # Reload module to ensure environment variables are checked with our settings
    importlib.reload(ss)
    required = [
        "SMTP_SERVER",
        "SMTP_PORT",
        "SMTP_USERNAME",
        "SMTP_PASSWORD",
        "SMTP_DEFAULT_RECIPIENT",
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
        "TWILIO_FROM_PHONE",
        "TWILIO_TO_PHONE",
    ]
    for var in required:
        monkeypatch.setenv(var, "1")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPEN_AI_KEY", raising=False)
    with pytest.raises(SystemExit):
        ss.StartUpService.check_env_vars()
