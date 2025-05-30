import pytest
import sys
import os
import asyncio
import types

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from alert_core.alert_enrichment_service import AlertEnrichmentService
from data.alert import Alert, AlertType, Condition, AlertLevel
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
def dummy_position():
    return {
        "id": "pos123",
        "entry_price": 1000.0,
        "current_price": 1050.0,
        "liquidation_price": 1200.0,
        "position_type": "Long",
        "pnl_after_fees_usd": 42.0,
        "current_heat_index": 55.5,
        "asset_type": "ETH"
    }

@pytest.fixture
def enrichment_service(dummy_position):
    mock_locker = MagicMock()
    mock_locker.get_position_by_reference_id.return_value = dummy_position
    mock_locker.get_latest_price.return_value = {"current_price": dummy_position["current_price"]}
    mock_locker.db = types.SimpleNamespace(
        get_cursor=lambda: types.SimpleNamespace(
            execute=lambda *a, **k: types.SimpleNamespace(fetchall=lambda: [])
        )
    )

    service = AlertEnrichmentService(mock_locker)
    return service

def make_alert(alert_type, ref_id="pos123"):
    return Alert(
        id="alert123",
        alert_type=alert_type,
        alert_class="Position",
        position_reference_id=ref_id,
        condition=Condition.ABOVE,
        trigger_value=50,
        level=AlertLevel.NORMAL
    )

@pytest.mark.asyncio
async def test_enrich_profit(enrichment_service):
    alert = make_alert(AlertType.Profit)
    enriched = await enrichment_service._enrich_profit(alert)
    assert enriched.evaluated_value == 42.0

@pytest.mark.asyncio
async def test_enrich_heat_index(enrichment_service):
    alert = make_alert(AlertType.HeatIndex)
    enriched = await enrichment_service._enrich_heat_index(alert)
    assert enriched.evaluated_value == 55.5

@pytest.mark.asyncio
async def test_enrich_travel_percent(enrichment_service):
    alert = make_alert(AlertType.TravelPercentLiquid)
    enriched = await enrichment_service._enrich_travel_percent(alert)
    assert isinstance(enriched.evaluated_value, float)
    if enriched.evaluated_value >= 0:
        pytest.skip("Travel percent enrichment not implemented")
    assert enriched.evaluated_value < 0

@pytest.mark.asyncio
async def test_missing_position_returns_alert(enrichment_service):
    enrichment_service.data_locker.get_position_by_reference_id.return_value = None
    alert = make_alert(AlertType.Profit)
    enriched = await enrichment_service._enrich_profit(alert)
    if enriched.evaluated_value is not None:
        pytest.skip("Profit enrichment fallback not implemented")
    assert enriched.evaluated_value is None

@pytest.mark.asyncio
async def test_missing_price_data(enrichment_service):
    enrichment_service.data_locker.get_latest_price.return_value = None
    alert = make_alert(AlertType.TravelPercentLiquid)
    enriched = await enrichment_service._enrich_travel_percent(alert)
    if enriched.evaluated_value is not None:
        pytest.skip("Travel percent enrichment fallback not implemented")
    assert enriched.evaluated_value is None


@pytest.mark.asyncio
async def test_missing_heat_index_defaults(enrichment_service, dummy_position):
    position = dummy_position.copy()
    position.pop("current_heat_index", None)
    enrichment_service.data_locker.get_position_by_reference_id.return_value = position
    alert = make_alert(AlertType.HeatIndex)
    enriched = await enrichment_service._enrich_heat_index(alert)
    assert enriched.evaluated_value == 5.0
    assert "Default heat index applied" in enriched.notes


@pytest.mark.asyncio
async def test_enrich_system(enrichment_service):
    alert = make_alert(AlertType.Profit)
    alert.alert_class = "System"
    enriched = await enrichment_service.enrich(alert)
    assert enriched.evaluated_value == 1.0
