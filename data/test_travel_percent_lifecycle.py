__test__ = False

import asyncio
from datetime import datetime
from uuid import uuid4
try:
    from data_locker import DataLocker
except Exception:  # pragma: no cover - optional dependency
    DataLocker = None
from alert_core.alert_core import AlertCore
try:
    from verify_alert_db_schema import verify_and_patch_schema
except Exception:  # pragma: no cover - optional dependency
    verify_and_patch_schema = lambda *_a, **_k: None
from core.logging import log


DB_PATH = "test_alerts.db"

# === Position Fixture ===
POSITION_ID = "travel_pos_001"
TEST_POSITION = {
    "id": POSITION_ID,
    "asset_type": "SOL",
    "entry_price": 100.0,
    "liquidation_price": 50.0,
    "position_type": "LONG",
    "wallet_name": "test_wallet",
    "current_heat_index": 5.0,
    "pnl_after_fees_usd": 0.0,
    "travel_percent": 0.0,
    "liquidation_distance": 0.0
}

# === Alert Generator ===
def make_travel_percent_alert(position_id, trigger_value=10.0):
    return {
        "id": str(uuid4()),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "alert_type": "travelpercentliquid",
        "alert_class": "Position",
        "asset": "SOL",
        "asset_type": "SOL",
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
        "liquidation_price": 50.0,
        "notes": "Travel test alert",
        "description": "travelpercentliquid",
        "position_reference_id": position_id,
        "evaluated_value": 0.0,
        "position_type": "LONG"
    }

# === Price Setter ===
def set_price(dl, asset, price):
    log.info(f"Injecting price for {asset}: {price}", source="TEST")
    dl.insert_or_update_price(asset, price)

# === AlertCore Config Loader ===
def config_loader():
    return {
        "alert_ranges": {
            "travelpercentliquid": {"low": 10, "medium": 25, "high": 50},
            "travel_percent_liquid_ranges": {
                "low": 10,
                "medium": 25,
                "high": 50,
                "enabled": True
            }
        }
    }

# === Lifecycle Runner ===
async def run_lifecycle():
    log.banner("🚦 Travel Percent Alert Lifecycle Test")

    # Setup
    dl = DataLocker(DB_PATH)
    verify_and_patch_schema(dl.db.connect())
    alert_core = AlertCore(dl, config_loader)

    # Position
    try:
        dl.positions.insert_position(TEST_POSITION)
        log.success(f"✅ Inserted test position {POSITION_ID}")
    except Exception:
        log.warning(f"⚠️ Position already exists: {POSITION_ID}")

    # Step 1: Set initial price toward liquidation (75 → expect -50%)
    set_price(dl, "SOL", 75.0)

    # Step 2: Create and evaluate alert
    alert = make_travel_percent_alert(POSITION_ID, trigger_value=10.0)
    await alert_core.create_alert(alert)
    await alert_core.evaluate_all_alerts()

    # Step 3: Update price toward profit (125 → expect +50%)
    set_price(dl, "SOL", 125.0)
    await alert_core.evaluate_all_alerts()

    # Step 4: Update price above profit (200 → expect +200%)
    set_price(dl, "SOL", 200.0)
    await alert_core.evaluate_all_alerts()


if __name__ == "__main__":
    asyncio.run(run_lifecycle())
