import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from uuid import uuid4
from datetime import datetime
from data.alert import AlertType, Condition
from alert_core.alert_utils import log_alert_summary

def test_alert_logging():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sample_alerts = [
        {
            "id": str(uuid4()),
            "created_at": now,
            "alert_type": AlertType.HeatIndex.value,
            "alert_class": "Position",
            "asset": "ETH",
            "asset_type": "ETH",
            "trigger_value": 50,
            "condition": Condition.ABOVE.value,
        },
        {
            "id": str(uuid4()),
            "created_at": now,
            "alert_type": AlertType.PriceThreshold.value,
            "alert_class": "Market",
            "asset": "BTC",
            "asset_type": "BTC",
            "trigger_value": 75000,
            "condition": Condition.ABOVE.value,
        },
        {
            "id": str(uuid4()),
            "created_at": now,
            "alert_type": AlertType.TotalHeat.value,
            "alert_class": "Portfolio",
            "asset": "PORTFOLIO",
            "asset_type": "ALL",
            "trigger_value": 30,
            "condition": Condition.ABOVE.value,
        },
    ]

    for alert in sample_alerts:
        alert.update({
            "notification_type": "SMS",
            "level": "Normal",
            "last_triggered": None,
            "status": "Active",
            "frequency": 1,
            "counter": 0,
            "liquidation_distance": 0.0,
            "travel_percent": 0.0,
            "liquidation_price": 0.0,
            "notes": "Unit test alert",
            "description": f"{alert['alert_class']} test",
            "position_reference_id": None,
            "evaluated_value": 0.0,
            "position_type": None
        })
        log_alert_summary(alert)
