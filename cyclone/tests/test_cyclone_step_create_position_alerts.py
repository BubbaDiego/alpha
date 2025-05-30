from uuid import uuid4
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import asyncio
import random

from datetime import datetime
from data.data_locker import DataLocker
from core.constants import DB_PATH
from data.alert import AlertType, Condition
from cyclone.cyclone_engine import Cyclone
from core.logging import log


dl = DataLocker(str(DB_PATH))
cyclone = Cyclone()


def generate_dummy_position(asset):
    return {
        "id": str(uuid4()),
        "asset_type": asset,
        "position_type": "long",
        "entry_price": 100,
        "current_price": 150,  # will trigger heat index due to movement
        "liquidation_price": 50,
        "liquidation_distance": 0.2,
        "collateral": 1000,
        "size": 2.0,
        "leverage": 2.0,
        "value": 2000,
        "pnl_after_fees_usd": 1200,  # exceeds $1000 profit alert
        "wallet_name": "test_wallet",
        "alert_reference_id": str(uuid4()),
        "hedge_buddy_id": None,
        "last_updated": datetime.now().isoformat(),
        "current_heat_index": 60,  # exceeds threshold
        "travel_percent": 12,
        "position_group_id": None,
        "is_active": True
    }



def test_create_position_alerts():
    log.banner("TEST #3: test_cyclone_step_create_position_alerts")

    # Step 1: Clear alerts & positions
    log.info("Step 1: Clearing alerts and positions...", source="Step1")
    dl.alerts.clear_all_alerts()
    dl.positions.delete_all_positions()
    log.success("✅ Cleared alerts and positions", source="Step1")

    # Step 2: Add dummy positions
    log.info("Step 2: Inserting dummy positions...", source="Step2")
    for _ in range(5):
        dl.positions.insert_position(generate_dummy_position("ETH"))
    log.success("✅ Inserted 5 dummy positions", source="Step2")

    # Step 3: Run alert generation
    log.info("Step 3: Running create_position_alerts...", source="Step3")
    try:
        asyncio.run(cyclone.run_create_position_alerts())
        log.success("✅ Position alerts created", source="Step3")
    except Exception as e:
        log.error(f"❌ Failed to create position alerts: {e}", source="Step3")

    # Step 4: Verify alert count
    alerts = dl.alerts.get_all_alerts()
    expected_alerts = 5 * 2  # 2 alerts per position
    if len(alerts) >= expected_alerts:
        log.success(f"✅ {len(alerts)} alerts generated (expected ≥ {expected_alerts})", source="Test")
    else:
        log.error(f"❌ Alert count too low: found {len(alerts)}, expected at least {expected_alerts}", source="Test")

    log.banner("✅ TEST COMPLETE: test_cyclone_step_create_position_alerts")


if __name__ == "__main__":
    test_create_position_alerts()
