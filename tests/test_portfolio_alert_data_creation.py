import pytest
import asyncio
import types
from data.alert import Alert, AlertType, Condition
from alert_core.alert_enrichment_service import AlertEnrichmentService
from core.core_imports import log

# --- Mock DataLocker for Portfolio Alert Creation ---

class MockDataLockerPortfolio:
    def __init__(self):
        self.positions = {
            "pos1": {
                "entry_price": 100,
                "liquidation_price": 50,
                "position_type": "LONG",
                "asset_type": "BTC",
                "current_heat_index": 75,
                "pnl_after_fees_usd": 1200
            }
        }
        self.prices = {"BTC": {"current_price": 150}}
        self.db = types.SimpleNamespace(
            get_cursor=lambda: types.SimpleNamespace(
                execute=lambda *a, **k: types.SimpleNamespace(fetchall=lambda: [])
            )
        )

    def get_position_by_reference_id(self, ref_id):
        return self.positions.get(ref_id)

    def get_latest_price(self, asset_type):
        return self.prices.get(asset_type.upper())

@pytest.mark.asyncio
async def test_portfolio_alert_data_creation():
    """Test creating and enriching Heat Index, Profit, and Travel Percent alerts."""
    data_locker = MockDataLockerPortfolio()
    enrichment_service = AlertEnrichmentService(data_locker)

    alerts = [
        Alert(
            id="heat-index-001",
            alert_type=AlertType.HeatIndex,
            asset="BTC",
            trigger_value=50,
            condition=Condition.ABOVE,
            evaluated_value=0.0,
            position_reference_id="pos1",
            position_type="LONG"
        ),
        Alert(
            id="profit-001",
            alert_type=AlertType.Profit,
            asset="BTC",
            trigger_value=1000,
            condition=Condition.ABOVE,
            evaluated_value=0.0,
            position_reference_id="pos1",
            position_type="LONG"
        ),
        Alert(
            id="travel-percent-001",
            alert_type=AlertType.TravelPercentLiquid,
            asset="BTC",
            trigger_value=-25,
            condition=Condition.BELOW,
            evaluated_value=0.0,
            position_reference_id="pos1",
            position_type="LONG"
        )
    ]

    enriched_alerts = []
    for alert in alerts:
        enriched = await enrichment_service.enrich(alert)
        enriched_alerts.append(enriched)

    # Validate enriched alerts
    for enriched in enriched_alerts:
        log.success(f"✅ Enriched Alert {enriched.id}: {enriched.evaluated_value}", source="PortfolioAlertTest")
        assert enriched.evaluated_value is not None, f"Evaluated value missing for {enriched.id}"
        assert enriched.asset, f"Asset missing in {enriched.id}"
        assert enriched.position_reference_id, f"Position reference ID missing in {enriched.id}"
        assert hasattr(enriched, "position_type"), f"Position type field missing in {enriched.id}"
        assert enriched.position_type, f"Position type value missing in {enriched.id}"

    log.success("✅ All portfolio alerts created and enriched correctly.", source="PortfolioAlertTest")
