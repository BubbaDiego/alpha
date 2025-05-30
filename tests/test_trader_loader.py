import importlib
import types

from trader.trader_loader import TraderLoader
from trader.trader import Trader


class DummyWallets:
    def get_wallet_by_name(self, name):
        return {"name": name, "balance": 100}


class DummyLocker:
    def __init__(self, positions):
        self.wallets = DummyWallets()
        self.positions = types.SimpleNamespace(get_all_positions=lambda: positions)
        self.portfolio = types.SimpleNamespace(get_latest_snapshot=lambda: {"id": "snap"})

    def get_last_update_times(self):
        return {}


def test_trader_loader_builds_trader():
    positions = [{"heat_index": 10}, {"heat_index": 50}]
    loader = TraderLoader(data_locker=DummyLocker(positions))
    trader = loader.load_trader("Angie")
    assert isinstance(trader, Trader)
    assert trader.name == "Angie"
    assert trader.heat_index == 30
    assert trader.mood
