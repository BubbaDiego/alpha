import sys
import os
# Ensure repository root is on the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import asyncio
from datetime import datetime
from uuid import uuid4
from data.verify_alert_db_schema import verify_and_patch_schema
from data.data_locker import DataLocker
from alert_core.alert_core import AlertCore
from core.logging import log

# Ensure schema exists BEFORE DataLocker instantiates
from data.database import DatabaseManager

# 🔧 Point to real DB file (or use ":memory:")
DB_PATH = ":memory:"

# 1. Bootstrap schema BEFORE creating DataLocker
db = DatabaseManager(DB_PATH)
conn = db.connect()
verify_and_patch_schema(conn)

# 2. NOW safely create DataLocker
dl = DataLocker(DB_PATH)
dl.get_current_value = lambda asset: 9999.0  # patch to avoid price errors

# 3. Setup AlertCore
alert_core = AlertCore(dl, lambda: {
    "alert_ranges": {
        "profit": {"low": 10, "medium": 100, "high": 500},
        "heatindex": {"low": 2, "medium": 5, "high": 9},
        "travelpercentliquid": {"low": 10, "medium": 25, "high": 50},
        "profit_ranges": {"low": 10, "medium": 100, "high": 500, "enabled": True},
        "heat_index_ranges": {"low": 2, "medium": 5, "high": 9, "enabled": True},
        "travel_percent_liquid_ranges": {"low": 10, "medium": 25, "high": 50, "enabled": True}
    }
})

# 4. Sample Position to Test
TEST_POSITION = {
    "id": "test_pos_001",
    "asset_type": "BTC",
    "entry_price": 10000,
    "liquidation_price": 8000,
    "position_type": "LONG",
    "wallet_name": "TestWallet1",
    "current_heat_index": 6,
    "pnl_after_fees_usd": 200,
    "travel_percent": 0.0,
    "liquidation_distance": 0.0,
}
dl.positions.insert_position(TEST_POSITION)

# 5. Alert generator
def generate_test_alert(alert_type, trigger_value, value_override=None):
    return {
        "id": str(uuid4()),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "alert_type": alert_type,
        "alert_class": "Position",
        "asset": "BTC",
        "asset_type": "BTC",
        "trigger_value": trigger_value,
        "condition": "ABOVE",
        "notification_type": "SMS",
        "level": "Normal",
        "last_triggered": None,
        "status": "Active",
        "frequency": 1,
        "counter": 0,
        "liquidation_distance": 0.0,
        "travel_percent": 0.0,
        "liquidation_price": 0.0,
        "notes": f"Test alert {alert_type}",
        "description": alert_type,
        "position_reference_id": "test_pos_001",
        "evaluated_value": value_override if value_override is not None else 0.0,
        "position_type": "LONG"
    }

# 6. Barrage Execution
async def run_barrage():
    log.banner("🔥 E2E ALERT BARRAGE TEST BEGIN")

    # Create test alerts
    test_alerts = [
        generate_test_alert("profit", 10, 0),
        generate_test_alert("profit", 10, 50),
        generate_test_alert("profit", 10, 150),
        generate_test_alert("profit", 10, 600),
        generate_test_alert("heatindex", 2, 1),
        generate_test_alert("heatindex", 2, 4),
        generate_test_alert("heatindex", 2, 6),
        generate_test_alert("travelpercentliquid", 10, 5),
        generate_test_alert("travelpercentliquid", 10, 30),
    ]

    created = 0
    for a in test_alerts:
        if await alert_core.create_alert(a):
            created += 1

    log.success("🛠 All test alerts created", payload={"count": created})

    # Run full evaluation
    await alert_core.evaluate_all_alerts()

if __name__ == "__main__":
    asyncio.run(run_barrage())

import pytest


def test_alert_core_barrage():
    asyncio.run(run_barrage())

