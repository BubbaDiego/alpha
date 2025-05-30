import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import asyncio
from data.data_locker import DataLocker
from core.constants import DB_PATH
from cyclone.cyclone_engine import Cyclone
from core.logging import log

dl = DataLocker(str(DB_PATH))
cyclone = Cyclone()


def test_create_portfolio_alerts():
    log.banner("TEST #4: test_cyclone_step_create_portfolio_alerts")

    # Step 1: Clear alerts
    log.info("Step 1: Clearing alerts...", source="Step1")
    dl.alerts.clear_all_alerts()
    if len(dl.alerts.get_all_alerts()) == 0:
        log.success("✅ Alerts cleared successfully", source="Step1")
    else:
        log.error("❌ Failed to clear alerts", source="Step1")

    # Step 2: Run portfolio alert creation
    log.info("Step 2: Creating portfolio alerts via Cyclone...", source="Step2")
    try:
        asyncio.run(cyclone.run_create_portfolio_alerts())  # ✅ Await coroutine properly
        log.success("✅ Portfolio alert creation step executed", source="Step2")
    except Exception as e:
        log.error(f"❌ Failed to run create_portfolio_alerts: {e}", source="Step2")

    # Step 3: Verify
    log.info("Step 3: Verifying portfolio alerts...", source="Step3")
    alerts = dl.alerts.get_all_alerts()
    expected_count = 6  # Based on 6 metric alerts

    if len(alerts) >= expected_count:
        log.success(f"✅ {len(alerts)} portfolio alerts created (expected ≥ {expected_count})", source="Test")
    else:
        log.error(f"❌ Alert count too low: found {len(alerts)}, expected at least {expected_count}", source="Test")

    log.banner("✅ TEST COMPLETE: test_cyclone_step_create_portfolio_alerts")


if __name__ == "__main__":
    test_create_portfolio_alerts()
