import types
from unittest.mock import MagicMock

import wallets.blockchain_balance_service as svc


def test_get_balance_eth(monkeypatch):
    service = svc.BlockchainBalanceService()
    mock_web3 = MagicMock()
    mock_web3.eth.get_balance.return_value = 10**18
    mock_web3.from_wei.return_value = 1.0
    monkeypatch.setattr(service, "_eth", mock_web3)

    bal = service.get_balance("0xABCDEF")
    assert bal == 1.0
    mock_web3.eth.get_balance.assert_called_with("0xABCDEF")


def test_get_balance_solana(monkeypatch):
    service = svc.BlockchainBalanceService()
    mock_client = MagicMock()
    mock_client.get_balance.return_value = types.SimpleNamespace(value=2 * svc.LAMPORTS_PER_SOL)
    monkeypatch.setattr(service, "_sol", mock_client)
    monkeypatch.setattr(svc, "Pubkey", types.SimpleNamespace(from_string=lambda x: x))

    bal = service.get_balance("SoLAddress")
    assert bal == 2.0
    mock_client.get_balance.assert_called()


def test_solana_client_called_with_public_key(monkeypatch):
    service = svc.BlockchainBalanceService()
    mock_client = MagicMock()
    monkeypatch.setattr(service, "_sol", mock_client)
    monkeypatch.setattr(svc, "Confirmed", None)
    monkeypatch.setattr(svc, "Pubkey", types.SimpleNamespace(from_string=lambda x: f"PK:{x}"))

    service.get_balance("Addr")
    args, kwargs = mock_client.get_balance.call_args
    assert args[0] == "PK:Addr"
