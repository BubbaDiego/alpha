"""
WalletCore module
=================

High-level orchestrator for wallet operations.

This class loads wallets through ``WalletService`` and provides helper
methods for interacting with the Solana blockchain via ``solana-py``.
It does not replace existing services or repositories but delegates
persistence to them while offering convenience methods like
``fetch_balance`` and ``send_transaction``.
"""

from __future__ import annotations

from typing import List, Optional

from core.logging import log

try:
    from solana.rpc.api import Client
    from solana.transaction import Transaction
    from solana.keypair import Keypair
    from solders.pubkey import Pubkey
    from solana.rpc.commitment import Confirmed
    from solana.rpc.types import TxOpts
except ImportError as e:  # pragma: no cover - optional dependency
    log.warning("Failed to import solana/solders: %s", e)
    Client = None
    Transaction = object
    Keypair = object
    Pubkey = object
    Confirmed = None
    TxOpts = object

from wallets.blockchain_balance_service import BlockchainBalanceService
from wallets.jupiter_service import JupiterService
from wallets.jupiter_trigger_service import JupiterTriggerService
from data.data_locker import DataLocker

from wallets.wallet_service import WalletService
from wallets.wallet import Wallet

LAMPORTS_PER_SOL = 1_000_000_000


class WalletCore:
    """Central access point for wallet + blockchain operations."""

    def __init__(self, rpc_endpoint: str = "https://api.mainnet-beta.solana.com"):
        self.service = WalletService()
        self.rpc_endpoint = rpc_endpoint
        self.client = Client(rpc_endpoint) if Client else None
        # Instantiate BlockchainBalanceService regardless of solana availability
        # so ``load_wallets`` can gracefully attempt balance lookups.
        self.balance_service = BlockchainBalanceService()
        self.jupiter = JupiterService() if Client else None
        self.jupiter_trigger = JupiterTriggerService() if Client else None
        log.debug(
            f"WalletCore initialized with RPC {rpc_endpoint}" + (" (stubbed)" if Client is None else ""),
            source="WalletCore",
        )

    # ------------------------------------------------------------------
    # Data access helpers
    # ------------------------------------------------------------------
    def load_wallets(self) -> List[Wallet]:
        """Return all wallets from the repository as ``Wallet`` objects."""
        wallets_out = self.service.list_wallets()
        wallets = [Wallet(**w.dict()) for w in wallets_out]
        for w in wallets:
            bal = self.fetch_positions_balance(w.name)
            if bal is not None:
                w.balance = bal
        return wallets

    def set_rpc_endpoint(self, endpoint: str) -> None:
        """Switch to a different Solana RPC endpoint."""
        self.rpc_endpoint = endpoint
        if Client:
            self.client = Client(endpoint)
        log.debug(f"RPC endpoint switched to {endpoint}", source="WalletCore")

    # ------------------------------------------------------------------
    # Blockchain interaction helpers
    # ------------------------------------------------------------------
    def fetch_balance(self, wallet: Wallet) -> Optional[float]:
        """Fetch the SOL balance for ``wallet`` using the active client."""
        if not Client or not self.client:
            log.debug("fetch_balance skipped; solana client unavailable", source="WalletCore")
            return None
        try:
            resp = self.client.get_balance(
                Pubkey.from_string(wallet.public_address.strip()), commitment=Confirmed
            )
            lamports = resp.value
            if lamports is not None:
                return lamports / LAMPORTS_PER_SOL
        except Exception as e:
            log.error(f"Failed to fetch balance for {wallet.name}: {e}", source="WalletCore")
        return None

    def fetch_positions_balance(self, wallet_id: str) -> Optional[float]:
        """Return the total value of active positions for ``wallet_id``."""
        try:
            dl = DataLocker.get_instance()
            positions = dl.positions.get_active_positions()
            total = 0.0
            for pos in positions:
                if str(pos.get("wallet_name")) == str(wallet_id):
                    try:
                        total += float(pos.get("value") or 0.0)
                    except Exception:
                        continue
            return round(total, 2)
        except Exception as e:
            log.error(f"Failed to fetch positions balance for {wallet_id}: {e}", source="WalletCore")
            return None

    def refresh_wallet_balances(self) -> int:
        """Recalculate wallet balances from active positions and persist to the DB.

        Returns the number of wallets updated.
        """
        try:
            dl = DataLocker.get_instance()
        except Exception as exc:  # pragma: no cover - best effort
            log.error(f"Failed to obtain DataLocker: {exc}", source="WalletCore")
            return 0

        wallets = dl.read_wallets() if hasattr(dl, "read_wallets") else []
        updated = 0
        for w in wallets:
            bal = self.fetch_positions_balance(w.get("name"))
            if bal is None:
                continue
            try:
                w["balance"] = bal
                dl.update_wallet(w["name"], w)
                updated += 1
            except Exception as exc:  # pragma: no cover - database errors
                log.error(f"Failed to refresh balance for {w.get('name')}: {exc}", source="WalletCore")

        log.info(f"Refreshed balances for {updated} wallets", source="WalletCore")
        return updated

    def _keypair_from_wallet(self, wallet: Wallet) -> Keypair:
        if not Client or not wallet.private_address:
            raise ValueError("Wallet has no private key")
        try:
            import base58
            secret = base58.b58decode(wallet.private_address)
            return Keypair.from_secret_key(secret)
        except Exception:
            import base64
            secret = base64.b64decode(wallet.private_address)
            return Keypair.from_secret_key(secret)

    def send_transaction(self, wallet: Wallet, tx: Transaction) -> Optional[str]:
        """Sign and submit ``tx`` using ``wallet``'s keypair."""
        if not Client or not self.client:
            log.debug("send_transaction skipped; solana client unavailable", source="WalletCore")
            return None
        try:
            kp = self._keypair_from_wallet(wallet)
            recent = self.client.get_recent_blockhash()["result"]["value"]["blockhash"]
            tx.recent_blockhash = recent
            tx.sign(kp)
            resp = self.client.send_transaction(tx, kp, opts=TxOpts(preflight_commitment=Confirmed))
            sig = resp.get("result")
            if sig:
                log.success(f"Transaction sent: {sig}", source="WalletCore")
            return sig
        except Exception as e:
            log.error(f"Failed to send transaction from {wallet.name}: {e}", source="WalletCore")
            return None

    # ------------------------------------------------------------------
    # Jupiter collateral helpers
    # ------------------------------------------------------------------
    def deposit_collateral(self, wallet: Wallet, market: str, amount: float) -> Optional[dict]:
        """Deposit collateral into a Jupiter perpetual position."""
        if not Client or not self.jupiter:
            log.debug("deposit_collateral skipped; solana client unavailable", source="WalletCore")
            return None
        try:
            result = self.jupiter.increase_position(wallet.public_address, market, amount)
            log.info(
                f"Deposited {amount} to {market} for {wallet.name}",
                source="WalletCore",
            )
            return result
        except Exception as e:  # pragma: no cover - network failures
            log.error(f"Deposit failed for {wallet.name}: {e}", source="WalletCore")
            return None

    def withdraw_collateral(self, wallet: Wallet, market: str, amount: float) -> Optional[dict]:
        """Withdraw collateral from a Jupiter perpetual position."""
        if not Client or not self.jupiter:
            log.debug("withdraw_collateral skipped; solana client unavailable", source="WalletCore")
            return None
        try:
            result = self.jupiter.decrease_position(wallet.public_address, market, amount)
            log.info(
                f"Withdrew {amount} from {market} for {wallet.name}",
                source="WalletCore",
            )
            return result
        except Exception as e:  # pragma: no cover - network failures
            log.error(f"Withdraw failed for {wallet.name}: {e}", source="WalletCore")
            return None

    def place_trigger_order(
        self,
        wallet: Wallet,
        market: str,
        trigger_price: float,
        size: float,
        is_long: bool,
    ) -> Optional[str]:
        """Create a trigger order and send the resulting transaction."""
        if not Client or not self.jupiter_trigger:
            log.debug("place_trigger_order skipped; solana client unavailable", source="WalletCore")
            return None
        try:
            resp = self.jupiter_trigger.create_trigger_order(
                wallet.public_address,
                market,
                trigger_price,
                size,
                is_long,
            )
            tx_data = resp.get("transaction")
            if not tx_data:
                log.error("Trigger order response missing transaction", source="WalletCore")
                return None
            tx_obj = None
            if isinstance(tx_data, Transaction):
                tx_obj = tx_data
            else:
                try:
                    import base64
                    tx_obj = Transaction.deserialize(base64.b64decode(tx_data))
                except Exception as exc:
                    log.error(f"Failed to decode trigger transaction: {exc}", source="WalletCore")
                    return None
            return self.send_transaction(wallet, tx_obj)
        except Exception as e:  # pragma: no cover - network failures
            log.error(f"Trigger order failed for {wallet.name}: {e}", source="WalletCore")
            return None

    def insert_star_wars_wallets(self) -> int:
        """Load Star Wars themed wallets via the helper script."""
        try:
            from scripts.insert_star_wars_wallets import insert_star_wars_wallets

            return insert_star_wars_wallets()
        except Exception as e:  # pragma: no cover - best effort
            log.error(f"Failed to inject Star Wars wallets: {e}", source="WalletCore")
            return 0

    def delete_all_wallets(self) -> None:
        """Remove all wallets from persistent storage."""
        try:
            self.service.delete_all_wallets()
            log.success("All wallets deleted via WalletCore", source="WalletCore")
        except Exception as e:
            log.error(f"Failed to delete all wallets: {e}", source="WalletCore")

