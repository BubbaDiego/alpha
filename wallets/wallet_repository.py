"""
📁 Module: wallet_repository.py
📌 Purpose: Handles wallet data persistence to DB and fallback to JSON backup.
"""

import json
import os
from typing import List, Optional

from data.data_locker import DataLocker
from wallets.wallet import Wallet
from wallets.wallet_schema import WalletIn

# 📁 Fallback JSON path (ensure file exists or can be written)
WALLETS_JSON_PATH = "wallets.json"

from core.core_imports import DB_PATH

class WalletRepository:
    def __init__(self):
        self.dl = DataLocker(str(DB_PATH))


    # 🧾 Get all wallets from DB
    def get_all_wallets(self) -> List[Wallet]:
        rows = self.dl.read_wallets()
        return [
            Wallet(**{**row, "chrome_profile": row.get("chrome_profile", "Default")})
            for row in rows
        ]

    # 🔍 Get a wallet by its unique name
    def get_wallet_by_name(self, name: str) -> Optional[Wallet]:
        row = self.dl.get_wallet_by_name(name)
        if row:
            data = {**row, "chrome_profile": row.get("chrome_profile", "Default")}
            return Wallet(**data)
        return None

    # ➕ Insert new wallet into DB
    def add_wallet(self, wallet: WalletIn) -> None:
        """Persist ``wallet`` to the database."""

        # ``WalletIn`` is a Pydantic model (or stub fallback) so we rely on
        # its ``dict()`` method rather than ``dataclasses.asdict``.
        self.dl.create_wallet(wallet.dict())

    # 🗑️ Delete wallet by name
    def delete_wallet(self, name: str) -> bool:
        wallet = self.get_wallet_by_name(name)
        if not wallet:
            return False
        self.dl.delete_positions_for_wallet(wallet.name)  # 🔥 Optional: delete linked positions
        cursor = self.dl.db.get_cursor()
        cursor.execute("DELETE FROM wallets WHERE name = ?", (name,))
        self.dl.db.commit()
        return True

    # 🔁 Update wallet by name
    def update_wallet(self, name: str, wallet: WalletIn) -> bool:
        self.dl.update_wallet(name, wallet.dict())
        return True

    # 💾 Backup all wallets to JSON
    def export_to_json(self, path: str = WALLETS_JSON_PATH) -> None:
        wallets = self.get_all_wallets()
        with open(path, "w") as f:
            json.dump(
                [
                    {**w.__dict__, "chrome_profile": w.chrome_profile or "Default"}
                    for w in wallets
                ],
                f,
                indent=2,
            )

    # ♻️ Restore from wallets.json
    def load_from_json(self, path: str = WALLETS_JSON_PATH) -> List[Wallet]:
        if not os.path.exists(path):
            return []
        with open(path, "r") as f:
            data = json.load(f)
        return [
            Wallet(**{**item, "chrome_profile": item.get("chrome_profile", "Default")})
            for item in data
        ]

    def delete_all_wallets(self) -> None:
        """Remove all wallets from the database."""
        self.dl.wallets.delete_all_wallets()
