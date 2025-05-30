import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import asyncio
import random
from datetime import datetime
from uuid import uuid4
from data.data_locker import DataLocker
from core.constants import DB_PATH
from cyclone.cyclone_engine import Cyclone
from core.logging import log

dl = DataLocker(str(DB_PATH))
cyclone = Cyclone()

def generate_position(asset):
    return {
        "id": str(uuid4()),
        "asset_type": asset,
        "position_type": "long",
        "entry_price": 100,
        "current_price": 150,
        "liquidation_price": 60,
        "liquidation_distance": 0.2,
        "collateral": 1000,
        "size": 2,
        "leverage": 2.0,
        "value": 2000,
        "pnl_after_fees_usd": 1200,
        "wallet_name": "test_wallet",
        "alert_reference_id": str(uuid4()),
        "hedge_buddy_id": None,
        "last_updated": datetime.now().isoformat(),
        "current_heat_index": 75,
        "travel_percent": 12,
        "position_group_id": None,
        "is_active": True
    }

def verify_alerts_evaluated(alerts):
    all_passed = True
    for a in alerts:
        if a.get("evaluated_value") is None:
            log.error(f"❌ Alert {a['id']} has no evaluated_value", source="Test")
            all_passed = False
        if a.get("level") not in {"Normal", "Low", "Medium", "High", "Critical"}:
            log.error(f"❌ Alert {a['id']} has bad level: {a.get('level')}", source="Test")
            all_passed = False
    return all_passed

def test_alert_evaluation_pipeline():
    log.banner("TEST #6: test_cyclone_step_evaluate_alerts")

    # Step 1: Clear All Data
    log.info("Clearing all alerts, positions, prices", source="Step1")
    dl.alerts.clear_all_alerts()
    dl.positions.delete_all_positions()
    dl.prices.clear_prices()
    log.success("✅ DB state wiped clean", source="Step1")

    # Step 2: Inject 5 positions
    log.info("Injecting dummy positions", source="Step2")
    for _ in range(5):
        dl.positions.insert_position(generate_position("ETH"))
    log.success("✅ 5 dummy positions inserted", source="Step2")

    # Step 3: Create alerts (position, portfolio, global)
    log.info("Creating position + portfolio + global alerts", source="Step3")
    asyncio.run(cyclone.run_create_position_alerts())
    asyncio.run(cyclone.run_create_portfolio_alerts())
    dl.alerts.create_alert({
        "id": str(uuid4()),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "alert_type": "PRICE_THRESHOLD",
        "alert_class": "Market",
        "asset": "BTC",
        "asset_type": "Crypto",
        "trigger_value": 60000,
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
        "notes": "Global alert",
        "description": "BTC global trigger",
        "position_reference_id": None,
        "evaluated_value": 59000,
        "position_type": "N/A"
    })
    log.success("✅ Alerts created", source="Step3")

    # Step 4: Enrich alerts
    log.info("Enriching alerts...", source="Step4")
    asyncio.run(cyclone.run_alert_enrichment())
    log.success("✅ Enrichment done", source="Step4")

    # Step 5: Evaluate alerts
    log.info("Evaluating alerts...", source="Step5")
    asyncio.run(cyclone.run_alert_evaluation())
    log.success("✅ Evaluation complete", source="Step5")

    # Step 6: Validation
    log.info("Verifying evaluation results...", source="Step6")
    alerts = dl.alerts.get_all_alerts()
    if verify_alerts_evaluated(alerts):
        log.success(f"✅ All {len(alerts)} alerts evaluated and valid", source="Test")
    else:
        log.error("❌ Some alerts failed validation", source="Test")

    log.banner("✅ TEST COMPLETE: test_cyclone_step_evaluate_alerts")

if __name__ == "__main__":
    test_alert_evaluation_pipeline()
