import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from datetime import datetime
import logging
import subprocess
import threading
import itertools
import time

from monitor.base_monitor import BaseMonitor
from data.data_locker import DataLocker
from core.logging import log
from core.constants import DB_PATH, ALERT_THRESHOLDS_PATH
from config.config_loader import load_config
from utils.schema_validation_service import SchemaValidationService
from jsonschema import validate


class OperationsMonitor(BaseMonitor):
    """Monitor responsible for basic operations health checks.

    The monitor currently validates the alert limits configuration and can run
    a lightweight POST suite. Additional operational checks can be added over
    time to expand its responsibilities.
    """
    def __init__(self, timer_config_path=None, ledger_filename=None, monitor_interval=300, continuous_mode=False, notifications_enabled=False):
        super().__init__(
            name="operations_monitor",
            timer_config_path=timer_config_path,
            ledger_filename=ledger_filename or "operations_ledger.json"
        )
        self.data_locker = DataLocker(str(DB_PATH))
        self.monitor_interval = monitor_interval
        self.continuous_mode = continuous_mode
        self.notifications_enabled = notifications_enabled
        self.logger = logging.getLogger("OperationsMonitor")

    def check_for_config_updates(self) -> bool:
        """Reload ``alert_thresholds`` from disk and update the DB entry if changed.

        Returns ``True`` when an update was detected and persisted.
        """
        config_path = str(ALERT_THRESHOLDS_PATH)
        if not os.path.exists(config_path):
            return False

        file_config = load_config(config_path)
        if not file_config:
            log.warning("Config file empty or invalid", source=self.name)
            return False

        current = self.data_locker.system.get_var("alert_thresholds") or {}
        if current != file_config:
            self.data_locker.system.set_var("alert_thresholds", file_config)
            log.info("🔄 alert_thresholds config updated", source=self.name)
            return True
        return False


    def _do_work(self):
        """Perform startup tests and log to the ledger.

        This also checks for configuration changes each cycle so the Cyclone
        engine can reload ``alert_thresholds`` when updated externally.
        """

        self.check_for_config_updates()
        startup = self.run_startup_post()
        api_status = self.check_api_status()

        overall_success = (
            startup.get("config_success")
            and startup.get("post_success")
            and api_status.get("chatgpt_success")
            and api_status.get("api_success")
        )

        payload = {"startup": startup, "api_status": api_status, "success": overall_success}

        self.data_locker.ledger.insert_ledger_entry(
            monitor_name=self.name,
            status="Success" if overall_success else "Failed",
            metadata=payload,
        )
        return payload

    def run_startup_post(self) -> dict:
        """Run configuration validation and POST tests."""
        log.banner("🧪 Operations Startup Tests")

        config_result = self.run_configuration_test()

        test_path = os.path.join(os.getcwd(), "tests", "test_alert_controller.py")

        if not os.path.exists(test_path):
            log.warning("Skipping POST: test file not found.", source=self.name)
            return {"post_success": True, "skipped": True}

        start_time = datetime.now()

        stop_event = threading.Event()

        def spin(msg: str):
            spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
            while not stop_event.is_set():
                sys.stdout.write('\r' + next(spinner) + ' ' + msg)
                sys.stdout.flush()
                time.sleep(1.75)

        t = threading.Thread(target=spin, args=("Running POST tests...",))
        t.start()
        result = subprocess.run(
            [sys.executable, "-m", "pytest", test_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stop_event.set()
        t.join()
        sys.stdout.write('\r')
        sys.stdout.flush()
        success = (result.returncode == 0)
        duration = (datetime.now() - start_time).total_seconds()

        stdout_text = result.stdout.decode()
        if not success:
            log.error("Startup POST tests failed!", source=self.name)
            log.error(stdout_text, source=self.name)
            log.error(result.stderr.decode(), source=self.name)
        else:
            log.success("Startup POST tests passed.", source=self.name)

        passed = 0
        failed = 0
        import re
        m = re.search(r"(\d+) passed", stdout_text)
        if m:
            passed = int(m.group(1))
        m = re.search(r"(\d+) failed", stdout_text)
        if m:
            failed = int(m.group(1))
        total = passed + failed
        if total:
            if failed == 0:
                log.success(f"🎉 {passed} of {total} passed 100%", source=self.name)
            else:
                pct = int(passed / total * 100)
                log.error(f"💥 {passed} of {total} passed ({pct}%)", source=self.name)

        return {
            "config_success": config_result.get("config_success"),
            "config_duration_seconds": config_result.get("duration_seconds"),
            "post_success": success,
            "post_duration_seconds": duration,
        }

    def check_api_status(self) -> dict:
        """Check ChatGPT and API (Twilio) connectivity and log to XCom ledger."""
        log.info("🔌 Checking API status", source=self.name)

        chatgpt_success = False
        chatgpt_error = None
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPEN_AI_KEY")
        if not api_key:
            log.warning("OPENAI_API_KEY not configured", source=self.name)
            chatgpt_error = "missing api key"
        else:
            try:  # pragma: no cover - openai optional
                from openai import OpenAI

                client = OpenAI(api_key=api_key)
                client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "ping"}],
                )
                chatgpt_success = True
                log.success("ChatGPT API reachable", source=self.name)
            except Exception as exc:  # pragma: no cover - network dependent
                chatgpt_error = str(exc)
                log.error(f"ChatGPT check failed: {exc}", source=self.name)

        api_success = False
        api_error = None
        try:
            from xcom.check_twilio_heartbeat_service import CheckTwilioHeartbeatService

            result = CheckTwilioHeartbeatService({}).check(dry_run=True)
            api_success = bool(result.get("success"))
            if api_success:
                log.success("Twilio credentials valid", source=self.name)
            else:
                api_error = result.get("error")
                log.error(f"Twilio check failed: {api_error}", source=self.name)
        except Exception as exc:  # pragma: no cover - network dependent
            api_error = str(exc)
            log.error(f"Twilio check failed: {exc}", source=self.name)

        status = "Success" if chatgpt_success and api_success else "Failed"
        metadata = {
            "chatgpt_success": chatgpt_success,
            "api_success": api_success,
        }
        if chatgpt_error:
            metadata["chatgpt_error"] = chatgpt_error
        if api_error:
            metadata["api_error"] = api_error

        # Update xcom ledger for dashboard
        self.data_locker.ledger.insert_ledger_entry(
            monitor_name="xcom_monitor",
            status=status,
            metadata=metadata,
        )

        return metadata

    def run_configuration_test(self) -> dict:
        """Validate alert thresholds configuration."""
        log.info("🔧 Validating alert thresholds configuration...")
        start_time = datetime.now()

        config_path = str(ALERT_THRESHOLDS_PATH)
        file_exists = os.path.exists(config_path)
        config_data = load_config(config_path if file_exists else None)

        success = False

        if not file_exists:
            # No config file present; skip validation
            success = False
        elif not config_data:
            log.error("Config data empty", source=self.name)
        else:
            try:
                validate(instance=config_data, schema=SchemaValidationService.ALERT_THRESHOLDS_SCHEMA)
                success = True
                log.success(
                    "Alert thresholds configuration valid.", source=self.name
                )
            except Exception as exc:
                log.error(
                    f"Alert thresholds configuration invalid: {exc}", source=self.name
                )

        duration = (datetime.now() - start_time).total_seconds()
        return {"config_success": success, "duration_seconds": duration}

if __name__ == "__main__":
    from core.core_imports import configure_console_log
    log.banner("🚀 SELF-RUN: OperationsMonitor")
    configure_console_log()

    monitor = OperationsMonitor()
    result = monitor._do_work()

    log.success("🧾 OperationsMonitor Run Complete", source="SelfTest", payload=result)
    log.banner("✅ Operations POST Finished")
