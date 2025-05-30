import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data.data_locker import DataLocker
from core.constants import DB_PATH
from core.logging import log

dl = DataLocker(str(DB_PATH))

VALID_LEVELS = {"Normal", "Low", "Medium", "High", "Critical"}


def validate_alert_fields(alerts):
    passed = 0
    failed = 0

    for alert in alerts:
        alert_id = alert.get("id", "unknown")
        valid = True

        if alert.get("evaluated_value") is None:
            log.error(f"❌ [{alert_id}] missing evaluated_value", source="Test7")
            valid = False

        level = alert.get("level", "").strip().capitalize()
        if level not in VALID_LEVELS:
            log.error(f"❌ [{alert_id}] invalid level: {level}", source="Test7")
            valid = False

        if valid:
            passed += 1
        else:
            failed += 1

    return passed, failed


def test_alerts_have_valid_levels_and_values():
    log.banner("TEST #7: Validating Evaluated Alerts")

    alerts = dl.alerts.get_all_alerts()
    if not alerts:
        log.warning("⚠️ No alerts found in DB. Did evaluation run?", source="Test7")
        return

    log.info(f"🔍 Evaluating {len(alerts)} alerts for correctness...", source="Test7")
    passed, failed = validate_alert_fields(alerts)

    if failed == 0:
        log.success(f"✅ All {passed} alerts passed validation ✅", source="Test7")
    else:
        log.error(f"❌ {failed} alerts failed validation out of {passed + failed}", source="Test7")

    log.banner("✅ TEST COMPLETE: test_alerts_have_valid_levels_and_values")


if __name__ == "__main__":
    test_alerts_have_valid_levels_and_values()
