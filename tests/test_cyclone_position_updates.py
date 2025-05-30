import pytest
import asyncio
from cyclone.cyclone_engine import Cyclone
from core.core_imports import log

@pytest.fixture
def cyclone_instance():
    """Create a Cyclone instance for position updates testing."""
    return Cyclone(poll_interval=1)

@pytest.mark.asyncio
async def test_run_position_updates(cyclone_instance):
    """Test that position updates can run without crashing."""
    log.banner("TEST: Cyclone run_position_updates Start")
    try:
        await cyclone_instance.run_position_updates()
        log.success("✅ Cyclone position updates ran successfully.", source="TestCyclonePosition")
    except Exception as e:
        log.error(f"Error running position updates: {e}", source="TestCyclonePosition")
        assert False, f"Exception raised during position updates: {e}"
