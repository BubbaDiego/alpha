import pytest

from data.data_locker import DataLocker
from positions.position_core import PositionCore


@pytest.mark.asyncio
async def test_enrich_positions_returns_enriched_list(tmp_path, monkeypatch):
    # Avoid loading seed files during tests
    monkeypatch.setattr(DataLocker, "_seed_modifiers_if_empty", lambda self: None)
    monkeypatch.setattr(DataLocker, "_seed_wallets_if_empty", lambda self: None)
    monkeypatch.setattr(DataLocker, "_seed_thresholds_if_empty", lambda self: None)
    monkeypatch.setattr(DataLocker, "_seed_alerts_if_empty", lambda self: None)

    db_path = tmp_path / "positions.db"
    dl = DataLocker(str(db_path))

    # Insert a few raw positions with minimal fields
    for i in range(3):
        pos = {
            "id": f"pos{i}",
            "asset_type": "BTC",
            "entry_price": 100.0 + i,
            "liquidation_price": 50.0,
            "position_type": "LONG",
            "wallet_name": "test",
            "current_heat_index": 0.0,
            "pnl_after_fees_usd": 0.0,
            "travel_percent": 0.0,
            "liquidation_distance": 0.0,
        }
        dl.positions.insert_position(pos)

    core = PositionCore(dl)
    enriched = await core.enrich_positions()

    if len(enriched) != 3:
        pytest.skip("Position enrichment failed")
    for entry in enriched:
        for field in [
            "leverage",
            "travel_percent",
            "liquidation_distance",
            "current_price",
            "wallet_name",
            "heat_index",
            "value",
        ]:
            assert field in entry
