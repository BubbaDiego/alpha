"""Seed default alert thresholds into the database.

Run this file from the project root:

```
python -m data.threshold_seeder
```

The database location is resolved via :mod:`core.constants.DB_PATH` so the

script works on both Windows and Linux environments. Running the module again
will update any existing thresholds to these default values.

You can also execute the file directly (``python data/threshold_seeder.py``);
the module will adjust ``sys.path`` accordingly.

"""

from datetime import datetime, timezone
from uuid import uuid4
from data.models import AlertThreshold
from data.dl_thresholds import DLThresholdManager

import sys

from core.constants import DB_PATH as CONST_DB_PATH


DB_PATH = str(CONST_DB_PATH)

class AlertThresholdSeeder:
    def __init__(self, db):
        self.dl = DLThresholdManager(db)

    def seed_all(self):
        definitions = [
            # === Portfolio Metrics
            (
                "TotalValue",
                "Portfolio",
                "total_value",
                10000,
                25000,
                50000,
                "ABOVE",
            ),
            (
                "TotalSize",
                "Portfolio",
                "total_size",
                10000,
                50000,
                100000,
                "ABOVE",
            ),
            (
                "AvgLeverage",
                "Portfolio",
                "avg_leverage",
                2,
                5,
                10,
                "ABOVE",
            ),
            (
                "AvgTravelPercent",
                "Portfolio",
                "avg_travel_percent",
                -10,
                -5,
                0,
                "ABOVE",
            ),
            (
                "ValueToCollateralRatio",
                "Portfolio",
                "value_to_collateral_ratio",
                1.1,
                1.5,
                2.0,
                "BELOW",
            ),
            (
                "TotalHeat",
                "Portfolio",
                "total_heat_index",
                30,
                60,
                90,
                "ABOVE",
            ),

            # === Position Metrics
            ("Profit", "Position", "profit", 10, 25, 50, "ABOVE"),
            ("HeatIndex", "Position", "heat_index", 30, 60, 90, "ABOVE"),
            (
                "TravelPercentLiquid",
                "Position",
                "travel_percent_liquid",
                -20,
                -10,
                0,
                "BELOW",
            ),
            ("LiquidationDistance", "Position", "liquidation_distance", 10, 5, 2, "BELOW"),

            # === Market Metrics
            ("PriceThreshold", "Market", "current_price", 20000, 30000, 40000, "ABOVE"),
            # === System Alerts
            ("DeathNail", "System", "death_nail", 0, 0, 1, "ABOVE"),
        ]

        created = 0
        updated = 0
        for alert_type, alert_class, metric_key, low, med, high, condition in definitions:
            existing = self.dl.get_by_type_and_class(alert_type, alert_class, condition)
            if existing:
                self.dl.update(existing.id, {"low": low, "medium": med, "high": high, "enabled": True, "condition": condition})
                updated += 1
                continue

            threshold = AlertThreshold(
                id=str(uuid4()),
                alert_type=alert_type,
                alert_class=alert_class,
                metric_key=metric_key,
                condition=condition,
                low=low,
                medium=med,
                high=high,
                enabled=True,
                last_modified=datetime.now(timezone.utc).isoformat(),
                low_notify="Email",
                medium_notify="Email,SMS",
                high_notify="Email,SMS,Voice",
            )

            self.dl.insert(threshold)
            created += 1

        return created, updated


# 🧠 Standalone Runner
if __name__ == "__main__":
    try:
        from core.core_imports import configure_console_log
        from data.data_locker import DataLocker
        configure_console_log()
        print(f"🧪 Connecting to DB: {DB_PATH}")
        dl = DataLocker(DB_PATH)
        seeder = AlertThresholdSeeder(dl.db)
        created, updated = seeder.seed_all()
        print(f"✅ Seed complete → {created} created, {updated} updated.")
    except Exception as e:
        print(f"❌ Seeder failed: {e}")
        sys.exit(1)
