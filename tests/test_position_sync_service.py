import sys
import types
import importlib
import json

from data.data_locker import DataLocker


class DummyResponse:
    def __init__(self, data, status=200):
        self._data = data
        self.status_code = status
        self.text = json.dumps(data)

    def json(self):
        return self._data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception("error")


def load_service(monkeypatch, mock_get):
    requests_stub = types.SimpleNamespace(
        get=mock_get, RequestException=Exception, HTTPError=Exception
    )
    monkeypatch.setitem(sys.modules, "requests", requests_stub)
    import positions.position_sync_service as svc
    importlib.reload(svc)
    return svc


def setup_datalocker(tmp_path, monkeypatch):
    monkeypatch.setattr(DataLocker, "_seed_modifiers_if_empty", lambda self: None)
    monkeypatch.setattr(DataLocker, "_seed_wallets_if_empty", lambda self: None)
    monkeypatch.setattr(DataLocker, "_seed_thresholds_if_empty", lambda self: None)
    monkeypatch.setattr(DataLocker, "_seed_alerts_if_empty", lambda self: None)

    dl = DataLocker(str(tmp_path / "sync.db"))
    wallet = {"name": "TestWallet", "public_address": "ADDR1", "private_address": "priv"}
    dl.create_wallet(wallet)
    return dl


def test_update_jupiter_positions_inserts_and_retries(monkeypatch, tmp_path):
    dummy_data = {
        "dataList": [
            {
                "positionPubkey": "pos123",
                "marketMint": "3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh",
                "side": "long",
                "entryPrice": 100,
                "liquidationPrice": 80,
                "collateral": 10,
                "size": 1,
                "leverage": 5,
                "value": 20,
                "updatedTime": 1700000000,
                "pnlAfterFeesUsd": 0,
                "pnlChangePctAfterFees": 0.1,
                "markPrice": 90,
            }
        ]
    }
    calls = {"n": 0}

    def mock_get(url, headers=None, timeout=None):
        calls["n"] += 1
        if calls["n"] == 1:
            raise Exception("fail")
        return DummyResponse(dummy_data)

    svc_module = load_service(monkeypatch, mock_get)
    monkeypatch.setattr(svc_module.time, "sleep", lambda *a, **k: None)
    monkeypatch.setattr(svc_module.PositionEnrichmentService, "enrich", lambda self, p: p)

    dl = setup_datalocker(tmp_path, monkeypatch)
    service = svc_module.PositionSyncService(dl)
    result = service.update_jupiter_positions()

    assert result["imported"] == 1
    assert calls["n"] == 2

    positions = dl.positions.get_all_positions()
    assert len(positions) == 1
    assert positions[0]["id"] == "pos123"
    assert positions[0]["asset_type"] == "BTC"

    dl.db.close()


def test_update_jupiter_positions_handles_failure(monkeypatch, tmp_path):
    """API failures should increment the error count without raising."""

    def mock_get(url, headers=None, timeout=None):
        raise Exception("fail")

    svc_module = load_service(monkeypatch, mock_get)
    monkeypatch.setattr(svc_module.time, "sleep", lambda *a, **k: None)
    monkeypatch.setattr(svc_module.PositionEnrichmentService, "enrich", lambda self, p: p)

    dl = setup_datalocker(tmp_path, monkeypatch)
    service = svc_module.PositionSyncService(dl)
    result = service.update_jupiter_positions()

    assert result["imported"] == 0
    assert result["errors"] >= 1
    dl.db.close()
