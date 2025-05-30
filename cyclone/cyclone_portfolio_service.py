# cyclone/cyclone_portfolio_service.py

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from datetime import datetime
from uuid import uuid4
from data.data_locker import DataLocker
from data.alert import AlertType, Condition
from alert_core.alert_utils import log_alert_summary
from core.core_imports import DB_PATH
from core.logging import log


class CyclonePortfolioService:
    def __init__(self, data_locker):
        self.dl = data_locker


async def create_portfolio_alerts(self):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log.info("Creating portfolio alerts", source="CyclonePortfolio")

    metrics = [
        (AlertType.TotalValue, "total_value", 50000, Condition.ABOVE),
        (AlertType.TotalSize, "total_size", 1.0, Condition.ABOVE),
        (AlertType.AvgLeverage, "avg_leverage", 2.0, Condition.ABOVE),
        (AlertType.AvgTravelPercent, "avg_travel_percent", 10.0, Condition.ABOVE),
        (AlertType.ValueToCollateralRatio, "value_to_collateral_ratio", 1.2, Condition.BELOW),
        (AlertType.TotalHeat, "total_heat", 25.0, Condition.ABOVE),
    ]

    created = 0
    for alert_type, metric_desc, trigger_value, condition in metrics:
        try:
            log.debug(f"⏳ Preparing alert for: {metric_desc}", source="CyclonePortfolio")

            alert = {
                "id": str(uuid4()),
                "created_at": now,
                "alert_type": alert_type.value,
                "alert_class": "Portfolio",
                "asset": "PORTFOLIO",
                "asset_type": "ALL",
                "trigger_value": trigger_value,
                "condition": condition.value,
                "notification_type": "SMS",
                "level": "Normal",
                "last_triggered": None,
                "status": "Active",
                "frequency": 1,
                "counter": 0,
                "liquidation_distance": 0.0,
                "travel_percent": 0.0,
                "liquidation_price": 0.0,
                "notes": "Auto-generated portfolio alert",
                "description": metric_desc,
                "position_reference_id": None,
                "evaluated_value": 0.0,
                "position_type": "N/A"
            }

            log.debug(f"📦 Alert draft: {alert}", source="CyclonePortfolio")

            success = self.dl.alerts.create_alert(alert)
            if success:
                log.success(f"✅ Alert created: {alert['id']}", source="DLAlertManager")
                log.success(
                    f"📦 Alert Created → 🧭 Class: {alert['alert_class']} | 🏷️ Type: {alert['alert_type']} | 🎯 Trigger: {alert['trigger_value']}")
                log_alert_summary(alert)
                created += 1
            else:
                log.warning("⚠️ create_alert() returned False!", source="CyclonePortfolio")

        except Exception as e:
            console_fallback = str(e)
            log.error(f"💣 Exception creating portfolio alert for {metric_desc}: {console_fallback}",
                      source="CyclonePortfolio")
            log.debug(f"🧾 Alert payload at failure:\n{alert}", source="CyclonePortfolio")

    log.success(f"✅ Created {created} portfolio alerts.", source="CyclonePortfolio")


