import pytest
import asyncio
from data.alert import Alert, AlertType, Condition
from alert_core.alert_enrichment_service import AlertEnrichmentService

class MockDataLocker:
    def __init__(self):
        self.positions = {
            "pos1": {
                "entry_price": 1000,
                "liquidation_price": 500,
                "position_type": "LONG",
                "asset_type": "BTC",
                "current_heat_index": 42.0,
                "pnl_after_fees_usd": 150.0,
                "wallet_name": "test-wallet",
            }
        }
        self.prices = {"BTC": {"current_price": 12000.0}}
        class DummyCursor:
            def execute(self, *args, **kwargs):
                class Res:
                    def fetchall(self):
                        return []
                return Res()

        class DummyDB:
            def get_cursor(self):
                return DummyCursor()

        self.db = DummyDB()

    def get_position_by_reference_id(self, ref_id):
        return self.positions.get(ref_id)

    def get_latest_price(self, asset):
        return self.prices.get(asset.upper())

    def get_wallet_by_name(self, name):
        return {"name": name}

def test_enrich_all_preserves_order():
    data_locker = MockDataLocker()
    service = AlertEnrichmentService(data_locker)

    alerts = [
        Alert(
            id="a1",
            alert_type=AlertType.Profit,
            alert_class="Position",
            position_reference_id="pos1",
            condition=Condition.ABOVE,
        ),
        Alert(
            id="a2",
            alert_type=AlertType.PriceThreshold,
            alert_class="Market",
            asset="BTC",
            condition=Condition.ABOVE,
        ),
        Alert(
            id="a3",
            alert_type=AlertType.TotalValue,
            alert_class="Portfolio",
            condition=Condition.ABOVE,
        ),
    ]

    enriched = asyncio.run(service.enrich_all(alerts))

    assert [a.id for a in enriched] == ["a1", "a2", "a3"]
    assert enriched[0].evaluated_value == 150.0
    assert enriched[1].evaluated_value == 12000.0
    assert enriched[2].evaluated_value == 0.0

