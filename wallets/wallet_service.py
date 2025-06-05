"""
🧠 Module: wallet_service.py
📌 Purpose: Encapsulates business logic for managing wallets:
    - Creation / Deletion
    - Validation
    - Sync operations
"""

from typing import List
from wallets.wallet_schema import WalletIn, WalletOut
from wallets.wallet import Wallet
from wallets.wallet_repository import WalletRepository

class WalletService:
    def __init__(self):
        self.repo = WalletRepository()

    # ➕ Create a new wallet (with validation)
    def create_wallet(self, data: WalletIn) -> bool:
        existing = self.repo.get_wallet_by_name(data.name)
        if existing:
            raise ValueError(f"❌ Wallet '{data.name}' already exists.")
        self.repo.add_wallet(data)
        return True

    # 🗑️ Delete wallet by name
    def delete_wallet(self, name: str) -> bool:
        return self.repo.delete_wallet(name)

    # 🔁 Update wallet (overwrite with new fields)
    def update_wallet(self, name: str, data: WalletIn) -> bool:
        existing = self.repo.get_wallet_by_name(name)
        if not existing:
            raise ValueError(f"❌ Cannot update: wallet '{name}' not found.")
        self.repo.update_wallet(name, data)
        return True

    # 📋 List all wallets in output-safe form
    def list_wallets(self) -> List[WalletOut]:
        wallets = self.repo.get_all_wallets()
        return [
            WalletOut(**{**w.__dict__, "chrome_profile": w.chrome_profile or "Default"})
            for w in wallets
        ]

    # 🧾 Get one wallet
    def get_wallet(self, name: str) -> WalletOut:
        wallet = self.repo.get_wallet_by_name(name)
        if not wallet:
            raise ValueError(f"❌ Wallet '{name}' not found.")
        return WalletOut(**{**wallet.__dict__, "chrome_profile": wallet.chrome_profile or "Default"})

    # 💾 Backup all wallets to JSON
    def export_wallets_to_json(self):
        self.repo.export_to_json()

    # ♻️ Load from backup file
    def import_wallets_from_json(self) -> int:
        wallets = self.repo.load_from_json()
        imported_count = 0
        for w in wallets:
            if not self.repo.get_wallet_by_name(w.name):
                self.repo.add_wallet(
                    WalletIn(**{**w.__dict__, "chrome_profile": w.chrome_profile or "Default"})
                )
                imported_count += 1
        return imported_count
