import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import random
from uuid import uuid4
from datetime import datetime
from data.data_locker import DataLocker
from core.constants import DB_PATH
from core.logging import log
import asyncio
from data.data_locker import DataLocker
from core.constants import DB_PATH
from cyclone.cyclone_engine import Cyclone
from core.logging import log


dl = DataLocker(str(DB_PATH))
cyclone = Cyclone()


def verify_prices_added():
    prices = dl.prices.get_all_prices()
    count = len(prices)
    if count > 0:
        log.success(f"{count} price entries found after market update ✅", source="Test")
    else:
        log.error("❌ No prices found after market update", source="Test")


def test_market_updates():
    log.banner("TEST #2: test_cyclone_step_market_updates")

    # Step 1: Clear price data
    log.info("Step 1: Clearing all price data...", source="Step1")
    dl.prices.clear_prices()
    if len(dl.prices.get_all_prices()) == 0:
        log.success("✅ Prices cleared successfully", source="Step1")
    else:
        log.error("❌ Failed to clear prices", source="Step1")

    # Step 2: Run market update
    log.info("Step 2: Running Cyclone Market Updates...", source="Step2")
    try:
        asyncio.run(cyclone.run_market_updates())
        log.success("✅ Market updates completed", source="Step2")
    except Exception as e:
        log.error(f"❌ Market update failed: {e}", source="Step2")

    # Step 3: Verify prices added
    log.info("Step 3: Verifying price entries...", source="Step3")
    verify_prices_added()

    log.banner("✅ TEST COMPLETE: test_cyclone_step_market_updates")


if __name__ == "__main__":
    test_market_updates()


dl = DataLocker(str(DB_PATH))


def generate_dummy_price(asset):
    return {
        "id": str(uuid4()),
        "asset_type": asset,
        "current_price": round(random.uniform(10, 1000), 2),
        "previous_price": round(random.uniform(5, 900), 2),
        "last_update_time": datetime.now().isoformat(),
        "previous_update_time": None,
        "source": "TestSuite"
    }


def generate_dummy_position(asset):
    return {
        "id": str(uuid4()),
        "asset_type": asset,
        "position_type": "long",
        "travel_percent": round(random.uniform(0, 100), 2),
        "entry_price": round(random.uniform(10, 1000), 2),
        "current_price": round(random.uniform(10, 1000), 2),
        "liquidation_price": round(random.uniform(5, 800), 2),
        "liquidation_distance": round(random.uniform(0, 1.0), 4),  # 🧠 ADD THIS LINE
        "collateral": round(random.uniform(100, 1000), 2),
        "size": round(random.uniform(1, 10), 2),
        "leverage": round(random.uniform(1, 5), 2),
        "value": round(random.uniform(1000, 5000), 2),
        "pnl_after_fees_usd": round(random.uniform(-100, 500), 2),
        "wallet_name": "test_wallet",
        "alert_reference_id": str(uuid4()),
        "hedge_buddy_id": None,
        "last_updated": datetime.now().isoformat(),
        "current_heat_index": round(random.uniform(0, 100), 2),
        "position_group_id": None,
        "is_active": True
    }




def generate_dummy_alert(position_id):
    return {
        "id": str(uuid4()),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "alert_type": "TEST_ALERT",
        "alert_class": "Position",
        "asset": "TEST_ASSET",
        "asset_type": "Crypto",
        "trigger_value": 123.45,
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
        "notes": "Dummy test alert",
        "description": "Test alert description",
        "position_reference_id": position_id,
        "evaluated_value": 100.0,
        "position_type": "long"
    }


def verify_count(entity, expected, actual):
    if actual == expected:
        log.success(f"{entity} count verified: {actual}", source="Test")
    else:
        log.error(f"{entity} count mismatch — Expected {expected}, Got {actual}", source="Test")


def test_clear_all_data():
    log.banner("TEST #1: test_cyclone_step_clear_all_data")

    # Clear previous state (optional pre-clean)
    dl.prices.clear_prices()
    dl.positions.delete_all_positions()
    dl.alerts.clear_all_alerts()

    # Step 1: Inject Data
    log.info("Injecting dummy prices...", source="Step1")
    for _ in range(5):
        dl.prices.insert_price(generate_dummy_price("BTC"))
    log.success("Inserted 5 dummy prices", source="Step1")

    log.info("Injecting dummy positions...", source="Step1")
    for _ in range(5):
        dl.positions.insert_position(generate_dummy_position("ETH"))
    log.success("Inserted 5 dummy positions", source="Step1")

    log.info("Injecting dummy alerts...", source="Step1")
    for _ in range(5):
        dl.alerts.create_alert(generate_dummy_alert(str(uuid4())))
    log.success("Inserted 5 dummy alerts", source="Step1")

    # Step 2: Verify Insertions
    log.info("Verifying database insertions...", source="Step2")
    verify_count("Prices", 5, len(dl.prices.get_all_prices()))
    verify_count("Positions", 5, len(dl.positions.get_all_positions()))
    verify_count("Alerts", 5, len(dl.alerts.get_all_alerts()))
    log.success("All insertions verified", source="Step2")

    # Step 3: Clear Prices
    log.info("Clearing prices...", source="Step3")
    dl.prices.clear_prices()
    verify_count("Prices", 0, len(dl.prices.get_all_prices()))

    # Step 4: Clear Alerts
    log.info("Clearing alerts...", source="Step4")
    dl.alerts.clear_all_alerts()
    verify_count("Alerts", 0, len(dl.alerts.get_all_alerts()))

    # Step 5: Clear Positions
    log.info("Clearing positions...", source="Step5")
    dl.positions.delete_all_positions()
    verify_count("Positions", 0, len(dl.positions.get_all_positions()))

    log.banner("✅ TEST COMPLETE: test_cyclone_step_clear_all_data")


if __name__ == "__main__":
    test_clear_all_data()
