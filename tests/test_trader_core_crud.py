import types
import pytest

from trader_core.trader_core import TraderCore, Trader


class DummyLocker:
    def __init__(self):
        self.wallets = types.SimpleNamespace(
            get_wallet_by_name=lambda name: {"name": name}
        )
        self.positions = types.SimpleNamespace(get_all_positions=lambda: [])
        self.portfolio = types.SimpleNamespace(get_latest_snapshot=lambda: {})

    def get_last_update_times(self):
        return {}


class DummyPersonaManager:
    def __init__(self):
        self.persona = types.SimpleNamespace(
            name="TestBot",
            avatar="",
            profile="TestBot",
            origin_story="",
            risk_profile="",
            moods={"stable": "neutral"},
            strategy_weights={},
        )

    def get(self, name):
        return self.persona

    def list_personas(self):
        return [self.persona.name]


class DummyStrategyManager:
    pass


@pytest.fixture
def core():
    return TraderCore(
        data_locker=DummyLocker(),
        persona_manager=DummyPersonaManager(),
        strategy_manager=DummyStrategyManager(),
    )


def test_create_trader(core):
    trader = core.create_trader("TestBot")
    assert isinstance(trader, Trader)
    assert trader.name == "TestBot"
    assert trader.wallet == "TestBotVault"


def test_save_and_get_trader(core):
    trader = core.create_trader("TestBot")
    assert core.save_trader(trader)
    loaded = core.get_trader("TestBot")
    assert loaded == trader


def test_update_trader(core):
    trader = core.create_trader("TestBot")
    core.save_trader(trader)
    trader.mood = "excited"
    core.save_trader(trader)
    updated = core.get_trader("TestBot")
    assert updated.mood == "excited"


def test_list_traders(core):
    trader = core.create_trader("TestBot")
    core.save_trader(trader)
    traders = core.list_traders()
    assert len(traders) == 1
    assert traders[0].name == "TestBot"


def test_delete_trader(core):
    trader = core.create_trader("TestBot")
    core.save_trader(trader)
    assert core.delete_trader("TestBot")
    assert core.store.get("TestBot") is None
