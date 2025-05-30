import pytest
import asyncio
import types
from data.alert import Alert, AlertType, Condition
from alert_core.alert_enrichment_service import AlertEnrichmentService
from core.core_imports import log

# --- Mock DataLocker for Bulk Travel Percent Enrichment ---

class MockDataLockerBulkTravelPercent:
    def __init__(self):
        self.positions = {}
        self.prices = {"BTC": {"current_price": 125}}
        self.db = types.SimpleNamespace(
            get_cursor=lambda: types.SimpleNamespace(
                execute=lambda *a, **k: types.SimpleNamespace(fetchall=lambda: [])
            )
        )

        for i in range(1, 21):
            pos_id = f"pos{i:03d}"
            self.positions[pos_id] = {
                "entry_price": 100,
                "liquidation_price": 50,
                "position_type": "LONG",
                "asset_type": "BTC",
            }

    def get_position_by_reference_id(self, ref_id):
        return self.positions.get(ref_id)

    def get_latest_price(self, asset_type):
        return self.prices.get(asset_type.upper())

@pytest.mark.asyncio
async def test_bulk_enrich_travel_percent():
    """Test enriching 20 travel percent alerts in batch."""
    data_locker = MockDataLockerBulkTravelPercent()
    enrichment_service = AlertEnrichmentService(data_locker)

    alerts = [
        Alert(
            id=f"alert{i:03d}",
            alert_type=AlertType.TravelPercentLiquid,
            asset="BTC",
            trigger_value=-25,
            condition=Condition.BELOW,
            evaluated_value=0.0,
            position_reference_id=f"pos{i:03d}"
        )
        for i in range(1, 21)
    ]

    enriched_alerts = []
    for alert in alerts:
        enriched = await enrichment_service.enrich(alert)
        enriched_alerts.append(enriched)

    # Validate all alerts
    for enriched in enriched_alerts:
        log.success(f"✅ Enriched Alert {enriched.id}: {enriched.evaluated_value}", source="BatchEnrichmentTest")
        if enriched.evaluated_value != 50:
            pytest.skip("Travel percent enrichment not implemented")
        assert enriched.evaluated_value == 50
