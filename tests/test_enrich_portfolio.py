import asyncio
from unittest.mock import MagicMock

from alert_core.alert_enrichment_service import AlertEnrichmentService
from data.alert import Alert, AlertType, Condition


def test_enrich_portfolio_sets_default_value():
    locker = MagicMock()
    service = AlertEnrichmentService(locker)
    alert = Alert(
        id="port1",
        alert_type=AlertType.TotalValue,
        alert_class="Portfolio",
        asset="PORTFOLIO",
        trigger_value=100.0,
        condition=Condition.ABOVE,
        evaluated_value=10.5,
    )

    original = alert.dict()

    enriched = asyncio.run(service._enrich_portfolio(alert))

    assert enriched.evaluated_value == 0.0
    original["evaluated_value"] = 0.0
    assert enriched.dict() == original
