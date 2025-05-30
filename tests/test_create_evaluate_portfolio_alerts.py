import sys
import os
from uuid import uuid4
from datetime import datetime

# Ensure Cyclone project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from data.alert import AlertType, Condition, Status
from data.data_locker import DataLocker

try:
    from alert_core.alert_service_manager import AlertServiceManager
    from core.core_imports import get_locker
except Exception:
    pytest.skip("Missing alert_service_manager dependency", allow_module_level=True)


def test_create_evaluate_portfolio_alerts():
    """
    Integration test:
    ✅ Creates portfolio alerts for each type
    ✅ Inserts into DB
    ✅ Enriches + evaluates
    ✅ Logs results to console
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    dl = get_locker()
    dl.delete_all_alerts()

    metrics = [
        (AlertType.TotalValue, "total_value", 50.0, Condition.ABOVE),
        (AlertType.TotalSize, "total_size", 1.0, Condition.ABOVE),
        (AlertType.AvgLeverage, "avg_leverage", 2.0, Condition.ABOVE),
        (AlertType.AvgTravelPercent, "avg_travel_percent", 10.0, Condition.ABOVE),
        (AlertType.ValueToCollateralRatio, "value_to_collateral_ratio", 1.2, Condition.BELOW),
        (AlertType.TotalHeat, "total_heat", 25.0, Condition.ABOVE),
    ]

    print("🚀 Creating Portfolio Alerts")
    for alert_type, desc, trigger, condition in metrics:
        alert = {
            "id": str(uuid4()),
            "created_at": now,
            "alert_type": alert_type.value,
            "alert_class": "Portfolio",
            "asset": "PORTFOLIO",
            "asset_type": "ALL",
            "trigger_value": trigger,
            "condition": condition.value,
            "notification_type": "SMS",
            "level": "Normal",
            "last_triggered": None,
            "status": Status.ACTIVE.value,
            "frequency": 1,
            "counter": 0,
            "liquidation_distance": 0.0,
            "travel_percent": 0.0,
            "liquidation_price": 0.0,
            "notes": "Test alert",
            "description": desc,
            "position_reference_id": None,
            "evaluated_value": 0.0,
            "position_type": None
        }
        dl.create_alert(alert)
        print(f"📦 Created → 🧭 {alert['alert_class']} | 🏷️ {alert['alert_type']} | 🎯 {alert['trigger_value']}")

    print("\n✨ Running enrichment + evaluation...")
    service = AlertServiceManager.get_instance().alert_service
    service.refresh_alerts()

    alerts = dl.get_alerts()
    print("\n📊 Evaluation Results")
    for a in alerts:
        print(f"✅ {a['alert_type']} → value={a['evaluated_value']}, trigger={a['trigger_value']} → level={a['level']}")


if __name__ == "__main__":
    test_create_evaluate_portfolio_alerts()
