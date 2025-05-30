import importlib
import pytest
from utils import startup_service as ss
from data.data_locker import DataLocker


def setup_db(tmp_path):
    db_path = tmp_path / "wallet.db"
    return db_path


def disable_seeding(monkeypatch):
    monkeypatch.setattr(DataLocker, "_seed_modifiers_if_empty", lambda self: None)
    monkeypatch.setattr(DataLocker, "_seed_wallets_if_empty", lambda self: None)
    monkeypatch.setattr(DataLocker, "_seed_thresholds_if_empty", lambda self: None)
    monkeypatch.setattr(DataLocker, "_seed_alerts_if_empty", lambda self: None)


def test_startup_fails_without_wallet(tmp_path, monkeypatch):
    db_path = setup_db(tmp_path)
    disable_seeding(monkeypatch)
    importlib.reload(ss)
    ss.DB_PATH = str(db_path)
    with pytest.raises(SystemExit):
        ss.StartUpService.ensure_wallet_exists()

    # Insert a wallet then reload to use same path
    dl = DataLocker(str(db_path))
    dl.create_wallet({"name": "test", "public_address": "x", "private_address": "y"})
    dl.close()

    ss.StartUpService.ensure_wallet_exists()
