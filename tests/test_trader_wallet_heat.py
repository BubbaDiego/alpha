import pytest
from data.data_locker import DataLocker
from trader_core.trader_core import TraderCore


def _disable_seeding(monkeypatch):
    monkeypatch.setattr(DataLocker, "_seed_modifiers_if_empty", lambda self: None)
    monkeypatch.setattr(DataLocker, "_seed_wallets_if_empty", lambda self: None)
    monkeypatch.setattr(DataLocker, "_seed_thresholds_if_empty", lambda self: None)
    monkeypatch.setattr(DataLocker, "_seed_alerts_if_empty", lambda self: None)
    monkeypatch.setattr(DataLocker, "_seed_alert_config_if_empty", lambda self: None)


class DummyPersonaManager:
    def __init__(self, name="TestBot"):
        self.persona = type(
            "Persona",
            (),
            {
                "name": name,
                "avatar": "",
                "profile": name,
                "origin_story": "",
                "risk_profile": "",
                "moods": {"stable": "neutral"},
                "strategy_weights": {},
            },
        )()

    def get(self, name):
        return self.persona

    def list_personas(self):
        return [self.persona.name]


class DummyStrategyManager:
    pass


@pytest.fixture
def dl(tmp_path, monkeypatch):
    _disable_seeding(monkeypatch)
    locker = DataLocker(str(tmp_path / "wallet_heat.db"))
    yield locker
    locker.db.close()


def test_trader_heat_and_refresh(dl):
    # Setup wallet and positions
    wallet_name = "TestBotVault"
    dl.create_wallet({"name": wallet_name, "public_address": "x", "private_address": ""})
    dl.positions.create_position({"id": "p1", "wallet_name": wallet_name, "size": 2, "heat_index": 10, "status": "ACTIVE"})
    dl.positions.create_position({"id": "p2", "wallet_name": wallet_name, "size": 1, "heat_index": 40, "status": "ACTIVE"})
    dl.positions.create_position({"id": "p3", "wallet_name": "OtherVault", "size": 3, "heat_index": 80, "status": "ACTIVE"})

    core = TraderCore(dl, DummyPersonaManager(), DummyStrategyManager())
    trader = core.create_trader("TestBot")
    core.save_trader(trader)
    assert trader.heat_index == pytest.approx(20.0)
    assert trader.performance_score == 80

    # Add another position and refresh
    dl.positions.create_position({"id": "p4", "wallet_name": wallet_name, "size": 1, "heat_index": 100, "status": "ACTIVE"})
    refreshed = core.refresh_trader("TestBot")
    assert refreshed.heat_index == pytest.approx(40.0)
    assert refreshed.performance_score == 60
