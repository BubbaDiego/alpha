import asyncio
import random
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.logging import log
from data.alert import AlertType, Alert, Condition
from alert_core.alert_enrichment_service import AlertEnrichmentService
from alert_core.alert_evaluation_service import AlertEvaluationService


class MockDataLockerFullPipeline:
    def __init__(self):
        self.positions = {}
        self.prices = {"BTC": {"current_price": 125}}

        for i in range(1, 201):
            pos_id = f"pos{i:03d}"
            self.positions[pos_id] = {
                "entry_price": 100,
                "liquidation_price": 50,
                "pnl_after_fees_usd": random.uniform(100, 5000),
                "current_heat_index": random.uniform(10, 100),
                "position_type": random.choice(["LONG", "SHORT"]),
                "wallet_name": "dev-wallet",
                "asset_type": "BTC"
            }

    def get_position_by_reference_id(self, ref_id):
        return self.positions.get(ref_id)

    def get_latest_price(self, asset_type):
        return self.prices.get(asset_type.upper())

    def get_wallet_by_name(self, name):
        return {"name": name, "meta": "injected"} if name else None


async def run_pipeline():
    log.banner("🧪 SYSTEM TEST: Batch Enrich + Evaluate Pipeline")

    data_locker = MockDataLockerFullPipeline()
    enrichment_service = AlertEnrichmentService(data_locker)
    evaluation_service = AlertEvaluationService()

    evaluation_service.thresholds = {
        "PriceThreshold": {"LOW": 5000, "MEDIUM": 10000, "HIGH": 15000},
        "TravelPercentLiquid": {"LOW": -10, "MEDIUM": -25, "HIGH": -50},
        "Profit": {"LOW": 500, "MEDIUM": 1000, "HIGH": 2000},
        "HeatIndex": {"LOW": 30, "MEDIUM": 60, "HIGH": 90},
    }

    alerts = []
    types = [AlertType.PriceThreshold, AlertType.TravelPercentLiquid, AlertType.Profit, AlertType.HeatIndex]
    conditions = [Condition.ABOVE, Condition.BELOW]

    for i in range(200):
        alert_type = random.choice(types)
        position_ref = f"pos{i+1:03d}" if alert_type != AlertType.PriceThreshold else None

        alert = Alert(
            id=f"pipeline-alert-{i:03d}",
            alert_type=alert_type,
            asset="BTC",
            trigger_value=random.uniform(100, 10000),
            condition=random.choice(conditions),
            evaluated_value=0.0,
            position_reference_id=position_ref
        )
        alerts.append(alert)

    log.start_timer("enrichment-phase")
    enriched_alerts = []
    for i, alert in enumerate(alerts):
        log.debug(f"🧬 Enriching alert {i+1}/200 → {alert.id}", source="DevPipeline")
        enriched = await enrichment_service.enrich(alert)
        enriched_alerts.append(enriched)
    log.end_timer("enrichment-phase", source="DevPipeline")

    log.start_timer("evaluation-phase")
    evaluated_alerts = []
    for i, alert in enumerate(enriched_alerts):
        log.debug(f"📊 Evaluating alert {i+1}/200 → {alert.id}", source="DevPipeline")
        evaluated = evaluation_service.evaluate(alert)
        evaluated_alerts.append(evaluated)
    log.end_timer("evaluation-phase", source="DevPipeline")

    log.banner("📈 Summary of Evaluated Alerts")
    counts = {}
    for alert in evaluated_alerts:
        level = alert.level
        counts[level] = counts.get(level, 0) + 1
        log.success(f"✅ {alert.id}: {alert.alert_type.name} evaluated_value={alert.evaluated_value:.2f} → {level}", source="DevPipeline")

    log.info("🔢 Distribution Summary", source="DevPipeline", payload=counts)
    log.success("✅ Standalone pipeline test completed", source="DevPipeline")


if __name__ == "__main__":
    asyncio.run(run_pipeline())
