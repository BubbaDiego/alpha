
import asyncio
import random
from datetime import datetime

from alert_core.alert_service import AlertService
from alert_core.alert_repository import AlertRepository
from alert_core.alert_enrichment_service import AlertEnrichmentService
from xcom.notification_service import NotificationService
from data.alert import Alert, AlertType
from config.config_loader import load_config
from core.core_imports import log, retry_on_locked

# Mock DataLocker with Live Price Updates
class LiveMockDataLocker:
    @retry_on_locked()
    def __init__(self):
        self.alerts = []
        self.prices = {
            "BTC": {"current_price": 60000},
            "ETH": {"current_price": 1900},
            "SOL": {"current_price": 130},
        }

    def get_alerts(self):
        return [a.__dict__ for a in self.alerts]

    def get_latest_price(self, asset_type):
        return self.prices.get(asset_type.upper())

    def read_positions(self):
        # Simulate positions for travel percent, profit, heat index alerts
        return [
            {
                "id": "pos1",
                "travel_percent": random.uniform(-90, 0),
                "pnl_after_fees_usd": random.uniform(-1000, 5000),
                "current_heat_index": random.uniform(0, 100)
            }
        ]

    def update_alert_conditions(self, alert_id, fields: dict):
        for a in self.alerts:
            if a.id == alert_id:
                for key, val in fields.items():
                    setattr(a, key, val)

    def get_current_timestamp(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def simulate_price_tick(self):
        # Randomly update BTC, ETH, SOL prices slightly
        for asset in self.prices:
            change = random.uniform(-100, 100) if asset == "BTC" else random.uniform(-5, 5)
            self.prices[asset]["current_price"] += change
            if self.prices[asset]["current_price"] < 0:
                self.prices[asset]["current_price"] = 10  # Prevent negative prices

# Create alerts
def create_test_alerts(data_locker):
    assets = ["BTC", "ETH", "SOL"]
    alert_types = [AlertType.PRICE_THRESHOLD, AlertType.PROFIT, AlertType.TRAVEL_PERCENT_LIQUID, AlertType.HEAT_INDEX]

    for i in range(10):
        asset = random.choice(assets)
        alert_type = random.choice(alert_types)

        if alert_type == AlertType.PRICE_THRESHOLD:
            trigger = random.uniform(55000, 65000) if asset == "BTC" else random.uniform(1700, 2100)
            condition = "ABOVE"
        elif alert_type == AlertType.PROFIT:
            trigger = 1000
            condition = "ABOVE"
        elif alert_type == AlertType.TRAVEL_PERCENT_LIQUID:
            trigger = -25
            condition = "BELOW"
        elif alert_type == AlertType.HEAT_INDEX:
            trigger = 50
            condition = "ABOVE"

        alert = Alert(
            id=f"alert-{i+1:03d}",
            alert_type=alert_type,
            asset=asset,
            trigger_value=trigger,
            evaluated_value=0.0,
            condition=condition
        )
        data_locker.alerts.append(alert)

# Main runner
async def live_price_ticker_simulation():
    data_locker = LiveMockDataLocker()

    repo = AlertRepository(data_locker)
    enrichment = AlertEnrichmentService(data_locker)
    config_loader = lambda: load_config("alert_thresholds.json") or {}
    notification_service = NotificationService(config_loader)

    service = AlertService(repo, enrichment, config_loader)
    service.notification_service = notification_service

    create_test_alerts(data_locker)

    log.banner("🚀 LIVE Price Ticker Simulation Started")

    try:
        while True:
            data_locker.simulate_price_tick()
            log.info("💹 Simulated price tick updated.", source="PriceTicker")

            await service.process_all_alerts()

            await asyncio.sleep(5)  # Wait 5 seconds for next price tick
    except KeyboardInterrupt:
        log.warning("Simulation manually stopped.", source="PriceTicker")
        log.banner("🚀 LIVE Price Ticker Simulation Ended")

if __name__ == "__main__":
    asyncio.run(live_price_ticker_simulation())
