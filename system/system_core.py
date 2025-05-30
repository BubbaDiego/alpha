# 🧠 SystemCore — updated for theme profile support

import os

from alert_core.threshold_service import ThresholdService
from wallets.wallet_service import WalletService
from wallets.wallet_core import WalletCore
from system.theme_service import ThemeService
from xcom.xcom_core import XComCore
from system.death_nail_service import DeathNailService
from core.logging import log
from core.constants import JUPITER_API_BASE

try:  # Optional dependency
    import requests
except Exception:  # pragma: no cover - requests may be missing
    requests = None

class SystemCore:
    def __init__(self, data_locker):
        self.log = log
        self.wallets = WalletService()
        self.wallet_core = WalletCore()
        self.theme = ThemeService(data_locker)
        self.xcom = XComCore(data_locker)
        self.death_nail_service = DeathNailService(self.log, self.xcom)

        self.log.success("SystemCore initialized with Wallet, WalletCore and Theme services.")

    def death(self, metadata: dict):
        self.death_nail_service.trigger(metadata)

    # --- Summary + Meta ---
    def get_system_summary(self):
        try:
            summary = {
                "wallet_count": len(self.wallets.list_wallets()),
                "theme_mode": self.theme.get_theme_mode()
            }
            self.log.debug(f"System summary: {summary}")
            return summary
        except Exception as e:
            self.log.error(f"Error generating system summary: {e}")
            return {}

    def get_portfolio_thresholds(self) -> dict:
        svc = ThresholdService(self.theme.dl.db)

        metrics = {
            "avg_leverage": "AvgLeverage",
            "total_value": "TotalValue",
            "total_size": "TotalSize",
            "avg_travel_percent": "AvgTravelPercent",
            "value_to_collateral_ratio": "ValueToCollateralRatio",
            "total_heat": "TotalHeat",
        }

        result = {}
        for key, atype in metrics.items():
            # Attempt to fetch thresholds for ABOVE first then BELOW
            th = svc.get_thresholds(atype, "Portfolio", "ABOVE")
            if not th:
                th = svc.get_thresholds(atype, "Portfolio", "BELOW")

            result[key] = {
                "low": th.low if th else None,
                "medium": th.medium if th else None,
                "high": th.high if th else None,
                "condition": th.condition if th else "ABOVE",
            }

        return result
    def get_strategy_metadata(self):
        try:
            return self.theme.dl.system.get_last_update_times()
        except Exception as e:
            self.log.error(f"Failed to get strategy metadata: {e}", source="SystemCore")
            return {}

    # --- Theme Mode ---
    def get_theme_mode(self):
        return self.theme.get_theme_mode()

    def set_theme_mode(self, mode: str):
        self.theme.set_theme_mode(mode)

    # --- Theme Config (legacy JSON) ---
    def load_theme_config(self):
        return self.theme.load_theme_config()

    def save_theme_config(self, config: dict):
        self.theme.save_theme_config(config)

    # === 🚀 New: Theme Profile APIs ===

    def get_all_profiles(self) -> dict:
        return self.theme.get_all_profiles()

    def save_profile(self, name: str, config: dict):
        self.theme.save_profile(name, config)

    def delete_profile(self, name: str):
        self.theme.delete_profile(name)

    def set_active_profile(self, name: str):
        self.theme.set_active_profile(name)

    def get_active_profile(self) -> dict:
        return self.theme.get_active_profile()

    def save_theme_profile(self, name: str, config: dict) -> bool:
        """
        Persist a theme profile into the system's theme storage.
        """
        try:
            self.theme.dl.insert_or_update_theme_profile(name, config)
            return True
        except Exception as e:
            self.log.error(f"❌ Failed to save theme profile '{name}': {e}", source="SystemCore")
            return False

    def get_theme_profile(self, name: str) -> dict:
        """
        Retrieve a saved theme profile by name (if implemented).
        """
        try:
            return self.theme.dl.get_theme_profile(name)  # You can define this accessor in the DL
        except Exception as e:
            self.log.error(f"❌ Failed to fetch theme profile '{name}': {e}", source="SystemCore")
            return {}

    def get_active_profile_name(self) -> str:
        try:
            cursor = self.theme.dl.db.get_cursor()
            row = cursor.execute("SELECT theme_active_profile FROM system_vars WHERE id = 1").fetchone()
            return row["theme_active_profile"] if row else ""
        except Exception as e:
            self.log.error(f"Failed to get active profile name: {e}", source="SystemCore")
            return ""

    # --- Connectivity Checks ---
    def check_twilio_api(self) -> str:
        """Return 'ok' if Twilio credentials are valid, otherwise error text."""
        try:
            from xcom.check_twilio_heartbeat_service import CheckTwilioHeartbeatService

            result = CheckTwilioHeartbeatService({}).check(dry_run=True)
            if result.get("success"):
                return "ok"
            return result.get("error", "unknown error")
        except Exception as exc:  # pragma: no cover - optional dependency
            self.log.error(f"Twilio heartbeat check failed: {exc}", source="SystemCore")
            return str(exc)

    def check_chatgpt(self) -> str:
        """Return 'ok' if ChatGPT API is reachable, else an error message."""
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPEN_AI_KEY")
        if not api_key:
            return "missing api key"
        try:
            from openai import OpenAI  # type: ignore

            client = OpenAI(api_key=api_key)
            client.chat.completions.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": "ping"}])
            return "ok"
        except Exception as exc:  # pragma: no cover - network dependent
            self.log.error(f"ChatGPT check failed: {exc}", source="SystemCore")
            return str(exc)

    def check_jupiter(self) -> str:
        """Return 'ok' if the Jupiter API endpoint is reachable."""
        if not requests:  # pragma: no cover - optional dependency
            return "requests_unavailable"
        try:
            resp = requests.get(f"{JUPITER_API_BASE}/v1/perp_markets", timeout=5)
            resp.raise_for_status()
            return "ok"
        except Exception as exc:  # pragma: no cover - network dependent
            self.log.error(f"Jupiter API check failed: {exc}", source="SystemCore")
            return str(exc)

    def check_github(self) -> str:
        """Return 'ok' if the GitHub API is reachable."""
        if not requests:  # pragma: no cover - optional dependency
            return "requests_unavailable"
        try:
            resp = requests.get("https://api.github.com", timeout=5)
            resp.raise_for_status()
            return "ok"
        except Exception as exc:  # pragma: no cover - network dependent
            self.log.error(f"GitHub API check failed: {exc}", source="SystemCore")
            return str(exc)

    def check_api(self, api_name: str) -> dict:
        """Dispatch to the appropriate API check based on ``api_name``."""
        checks = {
            "twilio": self.check_twilio_api,
            "chatgpt": self.check_chatgpt,
            "jupiter": self.check_jupiter,
            "github": self.check_github,
        }

        check_func = checks.get(api_name.lower())
        if not check_func:
            return {"status": "unknown api"}

        result = check_func()
        return {"status": result}
