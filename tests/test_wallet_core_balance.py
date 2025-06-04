import os
from data.data_locker import DataLocker
import core.constants as const
import core.core_imports as ci
from wallets.wallet_core import WalletCore
from wallets.wallet_service import WalletService

SEED_PATCHES = [
    "_seed_modifiers_if_empty",
    "_seed_wallets_if_empty",
    "_seed_thresholds_if_empty",
    "_seed_alerts_if_empty",
]

def setup_db(tmp_path, monkeypatch):
    db_path = tmp_path / "wallet_core.db"
    os.environ["DB_PATH"] = str(db_path)
    const.DB_PATH = db_path
    ci.DB_PATH = db_path
    for name in SEED_PATCHES:
        monkeypatch.setattr(DataLocker, name, lambda self: None)
    return db_path


def init_locker(db_path):
    # Ensure singleton uses this path
    return DataLocker.get_instance(str(db_path))


def test_fetch_positions_balance_basic(tmp_path, monkeypatch):
    db = setup_db(tmp_path, monkeypatch)
    dl = init_locker(db)
    dl.create_wallet({"name": "w1", "public_address": "x", "private_address": ""})
    dl.positions.create_position({"wallet_name": "w1", "value": 1.234, "status": "ACTIVE"})
    dl.positions.create_position({"wallet_name": "w1", "value": 1.235, "status": "ACTIVE"})

    wc = WalletCore()
    monkeypatch.setattr(DataLocker, "get_instance", classmethod(lambda cls, db_path=str(db): dl))

    bal = wc.fetch_positions_balance("w1")
    assert bal == 2.47


def test_fetch_positions_balance_other_wallets(tmp_path, monkeypatch):
    db = setup_db(tmp_path, monkeypatch)
    dl = init_locker(db)
    dl.create_wallet({"name": "w1", "public_address": "x", "private_address": ""})
    dl.positions.create_position({"wallet_name": "w1", "value": 5, "status": "ACTIVE"})
    dl.positions.create_position({"wallet_name": "w2", "value": 7, "status": "ACTIVE"})

    wc = WalletCore()
    monkeypatch.setattr(DataLocker, "get_instance", classmethod(lambda cls, db_path=str(db): dl))

    bal = wc.fetch_positions_balance("w1")
    assert bal == 5


def test_fetch_positions_balance_empty(tmp_path, monkeypatch):
    db = setup_db(tmp_path, monkeypatch)
    dl = init_locker(db)
    dl.create_wallet({"name": "w1", "public_address": "x", "private_address": ""})

    wc = WalletCore()
    monkeypatch.setattr(DataLocker, "get_instance", classmethod(lambda cls, db_path=str(db): dl))

    assert wc.fetch_positions_balance("w1") == 0


def test_load_wallets_uses_positions_balance(tmp_path, monkeypatch):
    db = setup_db(tmp_path, monkeypatch)
    dl = init_locker(db)
    service = WalletService()
    from wallets.wallet_schema import WalletIn
    service.create_wallet(
        WalletIn(
            name="w1",
            public_address="x",
            private_address="",
            balance=0,
            image_path=None,
            tags=[],
            is_active=True,
            type="personal",
        )
    )
    dl.positions.create_position({"wallet_name": "w1", "value": 10, "status": "ACTIVE"})
    monkeypatch.setattr(DataLocker, "get_instance", classmethod(lambda cls, db_path=str(db): dl))

    wc = WalletCore()
    wallets = wc.load_wallets()
    assert wallets[0].balance == 10


def test_refresh_wallet_balances_updates_db(tmp_path, monkeypatch):
    db = setup_db(tmp_path, monkeypatch)
    dl = init_locker(db)
    dl.create_wallet({"name": "w1", "public_address": "x", "private_address": ""})
    dl.create_wallet({"name": "w2", "public_address": "y", "private_address": ""})
    dl.positions.create_position({"wallet_name": "w1", "value": 3, "status": "ACTIVE"})
    dl.positions.create_position({"wallet_name": "w2", "value": 7, "status": "ACTIVE"})

    monkeypatch.setattr(DataLocker, "get_instance", classmethod(lambda cls, db_path=str(db): dl))

    wc = WalletCore()
    count = wc.refresh_wallet_balances()
    assert count == 2
    assert dl.get_wallet_by_name("w1")["balance"] == 3
    assert dl.get_wallet_by_name("w2")["balance"] == 7

