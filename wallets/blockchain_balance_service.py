"""BlockchainBalanceService
==========================
Service to fetch wallet balances from popular blockchains.

This consolidates simple helpers for Ethereum and Solana. The service
can be expanded with additional networks as needed.
"""
from __future__ import annotations

from typing import Optional

from core.logging import log

try:
    from web3 import Web3
except Exception:  # pragma: no cover - optional dependency
    Web3 = None  # type: ignore

try:
    from solana.rpc.api import Client
    from solana.rpc.commitment import Confirmed
    from solders.pubkey import Pubkey
except ImportError as e:  # pragma: no cover - optional dependency
    log.warning("Failed to import solana/solders: %s", e)
    Client = None  # type: ignore
    Confirmed = None  # type: ignore
    Pubkey = object  # type: ignore

LAMPORTS_PER_SOL = 1_000_000_000


class BlockchainBalanceService:
    """Retrieve balances for public addresses on supported chains."""

    def __init__(self, eth_rpc_url: Optional[str] = None, sol_rpc_url: Optional[str] = None) -> None:
        self.eth_rpc_url = eth_rpc_url or "https://cloudflare-eth.com"
        self.sol_rpc_url = sol_rpc_url or "https://api.mainnet-beta.solana.com"
        self._eth = Web3(Web3.HTTPProvider(self.eth_rpc_url)) if Web3 else None
        self._sol = Client(self.sol_rpc_url) if Client else None
        log.debug(
            "BlockchainBalanceService initialized", source="BlockchainBalanceService"
        )

    # --------------------------------------------------------------
    def get_balance(self, address: str) -> Optional[float]:
        """Return the balance for ``address`` in its native unit."""
        if address.startswith("0x"):
            if not self._eth:
                log.error("web3 library unavailable", source="BlockchainBalanceService")
                return None
            try:
                wei = self._eth.eth.get_balance(address)
                return float(self._eth.from_wei(wei, "ether"))
            except Exception as exc:  # pragma: no cover - network failures
                log.error(
                    f"ETH balance fetch failed for {address}: {exc}",
                    source="BlockchainBalanceService",
                )
                return None
        if not self._sol:
            log.error("solana library unavailable", source="BlockchainBalanceService")
            return None
        try:
            kwargs = {}
            if Confirmed:
                kwargs["commitment"] = Confirmed
            clean_address = address.strip()
            resp = self._sol.get_balance(Pubkey.from_string(clean_address), **kwargs)
            lamports = resp.value
            if lamports is not None:
                return lamports / LAMPORTS_PER_SOL
        except Exception as exc:  # pragma: no cover - network failures
            log.error(
                f"SOL balance fetch failed for {address}: {exc}",
                source="BlockchainBalanceService",
            )
        return None
