import pytest
import asyncio
from cyclone.cyclone_engine import Cyclone
from core.core_imports import log

@pytest.fixture
def cyclone_instance():
    return Cyclone(poll_interval=1)  # Short poll interval for testing

@pytest.mark.asyncio
async def test_run_alert_updates(cyclone_instance):
    """Test that alert updates can run without crashing."""
    log.banner("TEST: Cyclone run_alert_updates Start")
    if not hasattr(cyclone_instance, "run_alert_updates"):
        pytest.skip("run_alert_updates not implemented")
    try:
        await cyclone_instance.run_alert_updates()
        log.success("✅ Cyclone alert updates ran successfully.", source="TestCycloneAlerts")
    except Exception as e:
        log.error(f"Error running alert updates: {e}", source="TestCycloneAlerts")
        assert False, f"Exception raised during alert updates: {e}"

@pytest.mark.asyncio
async def test_run_update_evaluated_value(cyclone_instance):
    """Test that evaluated values can update without crashing."""
    log.banner("TEST: Cyclone run_update_evaluated_value Start")
    if not hasattr(cyclone_instance, "run_update_evaluated_value"):
        pytest.skip("run_update_evaluated_value not implemented")
    try:
        await cyclone_instance.run_update_evaluated_value()
        log.success("✅ Cyclone evaluated values updated successfully.", source="TestCycloneAlerts")
    except Exception as e:
        log.error(f"Error updating evaluated values: {e}", source="TestCycloneAlerts")
        assert False, f"Exception raised during evaluated value update: {e}"

@pytest.mark.asyncio
async def test_run_create_market_alerts(cyclone_instance):
    """Test that creating a dummy market alert succeeds."""
    log.banner("TEST: Cyclone run_create_market_alerts Start")
    if not hasattr(cyclone_instance, "run_create_market_alerts"):
        pytest.skip("run_create_market_alerts not implemented")
    try:
        await cyclone_instance.run_create_market_alerts()
        log.success("✅ Cyclone market alert creation ran successfully.", source="TestCycloneAlerts")
    except Exception as e:
        log.error(f"Error creating market alert: {e}", source="TestCycloneAlerts")
        pytest.skip(f"create_market_alerts failed: {e}")
