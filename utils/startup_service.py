import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath(Path(__file__).resolve().parent.parent))

from core.constants import (
    DB_PATH,
    CONFIG_PATH,
    ALERT_THRESHOLDS_PATH,
    BASE_DIR,
    SONIC_SAUCE_PATH,
    COM_CONFIG_PATH,
    THEME_CONFIG_PATH,
    CONFIG_DIR,
    MONITOR_DIR,
    IMAGE_DIR,
    DATA_DIR,
    LOG_DIR,
)
from utils.schema_validation_service import SchemaValidationService
from data.data_locker import DataLocker
from monitor.operations_monitor import OperationsMonitor
from xcom.check_twilio_heartbeat_service import CheckTwilioHeartbeatService
from utils.path_audit import run_audit
from xcom.sound_service import SoundService
from scripts.verify_all_tables_exist import verify_all_tables_exist
from typing import Optional
try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover - optional dependency
    def load_dotenv(*_a, **_k):
        return False
import sqlite3
import time
import threading

# Automatically load environment variables
dotenv_file = BASE_DIR / ".env"
_loaded_env: Optional[str] = None
if load_dotenv(dotenv_file):
    _loaded_env = ".env"
else:
    example_file = BASE_DIR / ".env.example"
    if load_dotenv(example_file):
        _loaded_env = ".env.example"



class DotSpinner:
    """Simple spinner that prints dots while running."""

    def __init__(self, interval: float = 0.2):
        self.interval = interval
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._spin)
        self._thread.daemon = True

    def _spin(self):
        while not self._stop.is_set():
            sys.stdout.write(".")
            sys.stdout.flush()
            time.sleep(self.interval)

    def __enter__(self):
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._stop.set()
        self._thread.join()
        sys.stdout.write("\n")
        sys.stdout.flush()

from utils.config_loader import save_config
from core.core_imports import log

if _loaded_env:
    log.info(f"Loaded environment from {_loaded_env}", source="StartUpService")
else:
    log.warning(
        "No .env or .env.example file found; proceeding with system env only",
        source="StartUpService",
    )


def maybe_create_mother_brain(db_path: str) -> None:
    """Ensure the SQLite database file exists."""
    if not os.path.exists(db_path):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        conn = sqlite3.connect(db_path)
        conn.close()
        log.info(f"📄 Created database: {db_path}", source="StartUpService")

class StartUpService:

    @staticmethod
    def run_all(play_sound: bool = True):
        """Run all startup checks with a simple progress spinner."""
        log.banner("🧠 STARTUP CHECK")

        steps = [
            StartUpService.check_for_mother_brain,
            StartUpService.verify_required_paths,
            StartUpService.ensure_alert_thresholds,
            StartUpService.check_env_vars,
            StartUpService.initialize_database,
            StartUpService.verify_required_tables,
            StartUpService.ensure_wallet_exists,
            StartUpService.ensure_required_directories,
            StartUpService.run_path_audit,
            StartUpService.run_operations_tests,
            StartUpService.run_twilio_heartbeat,
        ]

        sounder = SoundService()

        try:
            for step in steps:
                with DotSpinner():
                    step()
            log.success("✅ All startup checks passed.\n", source="StartUpService")
            if play_sound:
                sounder.play("static/sounds/web_station_startup.mp3")
        except SystemExit:
            if play_sound:
                sounder.play("static/sounds/death_spiral.mp3")
            raise
        except Exception as exc:
            log.critical(f"❌ Startup failed: {exc}", source="StartUpService")
            if play_sound:
                sounder.play("static/sounds/death_spiral.mp3")
            raise

    @staticmethod
    def check_for_mother_brain():
        maybe_create_mother_brain(DB_PATH)

    @staticmethod
    def verify_required_paths():
        missing = []
        required = [
            DB_PATH,
            CONFIG_PATH,
            ALERT_THRESHOLDS_PATH,
            SONIC_SAUCE_PATH,
            COM_CONFIG_PATH,
            THEME_CONFIG_PATH,
        ]
        for path in required:
            if not os.path.exists(path):
                missing.append(path)

        if missing:
            log.critical("❌ Missing required file paths:")
            for p in missing:
                log.error(f"  - {p}", source="StartUpService")
            raise SystemExit("Startup check failed due to missing critical files.")
        else:
            log.info("✅ All required file paths present.", source="StartUpService")

    @staticmethod
    def ensure_alert_thresholds():
        if not os.path.exists(ALERT_THRESHOLDS_PATH):
            log.warning("⚠️ alert_thresholds.json not found. Creating default template...")
            default = {
                "source": "fallback",
                "alert_ranges": {},
                "global_alert_config": {
                    "enabled": True,
                    "data_fields": {},
                    "thresholds": {}
                }
            }
            save_config("alert_thresholds.json", default)
            log.success("✅ Default alert_thresholds.json created.", source="StartUpService")
        else:
            log.info("✅ alert_thresholds.json found.", source="StartUpService")
            valid = SchemaValidationService.validate_schema(
                str(ALERT_THRESHOLDS_PATH),
                SchemaValidationService.ALERT_THRESHOLDS_SCHEMA,
                name="Alert Ranges",
            )
            if not valid:
                raise SystemExit(
                    "Startup check failed: alert_thresholds.json schema invalid"
                )

    @staticmethod
    def ensure_required_directories():
        required_dirs = [
            LOG_DIR,
            DATA_DIR,
            CONFIG_DIR,
            MONITOR_DIR,
            IMAGE_DIR,
        ]
        for d in required_dirs:
            Path(d).mkdir(parents=True, exist_ok=True)
            log.info(f"📁 Ensured directory exists: {d}", source="StartUpService")

    @staticmethod
    def check_env_vars():
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

        missing = [var for var in required if not os.getenv(var)]

        if not (os.getenv("OPENAI_API_KEY") or os.getenv("OPEN_AI_KEY")):
            missing.append("OPENAI_API_KEY")
        if missing:
            log.critical("❌ Missing required environment variables:")
            for var in missing:
                log.error(f"  - {var}", source="StartUpService")
            raise SystemExit("Startup failed due to missing environment variables.")
        log.info("✅ Required environment variables present.", source="StartUpService")

    @staticmethod
    def initialize_database():
        try:
            dl = DataLocker(str(DB_PATH))
            dl.close()
            log.info(
                "✅ Database initialized and connectivity verified.",
                source="StartUpService",
            )
        except Exception as exc:
            log.critical(f"❌ Database initialization failed: {exc}", source="StartUpService")
            raise SystemExit("Startup failed during database initialization.")

    @staticmethod
    def verify_required_tables():
        """Ensure all required tables exist."""
        code = verify_all_tables_exist(str(DB_PATH))
        if code != 0:
            raise SystemExit("Startup failed due to missing database tables.")

    @staticmethod
    def ensure_wallet_exists():
        """Verify at least one wallet record is present."""
        try:
            dl = DataLocker(str(DB_PATH))
            wallets = dl.read_wallets()
            dl.close()
            if not wallets:
                log.critical("❌ No wallets found in the database.", source="StartUpService")
                raise SystemExit("Startup failed: at least one wallet is required.")
            log.info(f"✅ {len(wallets)} wallet(s) found.", source="StartUpService")
        except SystemExit:
            raise
        except Exception as exc:
            log.critical(f"❌ Wallet check failed: {exc}", source="StartUpService")
            raise SystemExit("Startup failed during wallet check.")

    @staticmethod
    def run_operations_tests():
        try:
            monitor = OperationsMonitor()
            monitor.run_startup_post()
        except Exception as exc:
            log.error(f"Operations POST tests failed: {exc}", source="StartUpService")

    @staticmethod
    def run_twilio_heartbeat():
        try:
            result = CheckTwilioHeartbeatService({}).check(dry_run=True)
            if not result.get("success"):
                log.error(
                    f"Twilio heartbeat check failed: {result.get('error')}",
                    source="StartUpService",
                )
            else:
                log.info("✅ Twilio credentials verified.", source="StartUpService")
        except Exception as exc:
            log.error(f"Twilio heartbeat error: {exc}", source="StartUpService")

    @staticmethod
    def run_path_audit():
        try:
            run_audit()
        except Exception as exc:
            log.error(f"Path audit failed: {exc}", source="StartUpService")

# --- Allow Standalone Run ---
if __name__ == "__main__":
    StartUpService.run_all()
