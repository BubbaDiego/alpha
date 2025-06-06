from core.core_imports import log
import json
# dl_wallets.py
"""
Author: BubbaDiego
Module: DLWalletManager
Description:
    Manages crypto wallet storage in the database. Supports create, read,
    update, and delete operations for wallet records.

Dependencies:
    - DatabaseManager from database.py
    - ConsoleLogger from console_logger.py
"""


from wallets.encryption import encrypt_key, decrypt_key


class DLWalletManager:
    def __init__(self, db):
        self.db = db
        log.debug("DLWalletManager initialized.", source="DLWalletManager")

    def create_wallet(self, wallet: dict):
        try:
            cursor = self.db.get_cursor()
            cursor.execute(
                """
                INSERT INTO wallets (
                    name, public_address, chrome_profile, private_address, image_path,
                    balance, tags, is_active, type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    wallet["name"],
                    wallet["public_address"],
                    wallet.get("chrome_profile", "Default"),
                    encrypt_key(wallet.get("private_address")),
                    wallet.get("image_path", ""),
                    wallet.get("balance", 0.0),
                    json.dumps(wallet.get("tags", [])),
                    int(wallet.get("is_active", True)),
                    wallet.get("type", "personal"),
                ),
            )
            self.db.commit()  # ✅ not self.db.db
            log.success(f"Wallet created: {wallet['name']}", source="DLWalletManager")
        except Exception as e:
            log.error(f"Failed to create wallet: {e}", source="DLWalletManager")

    def get_wallets(self) -> list:
        try:
            cursor = self.db.get_cursor()
            cursor.execute("SELECT * FROM wallets")
            wallets = [dict(row) for row in cursor.fetchall()]
            for w in wallets:
                w["private_address"] = decrypt_key(w.get("private_address"))
                tags = w.get("tags")
                if isinstance(tags, str):
                    try:
                        w["tags"] = json.loads(tags) if tags else []
                    except json.JSONDecodeError:
                        w["tags"] = [t.strip() for t in tags.split(",") if t.strip()]
                w["is_active"] = bool(w.get("is_active", 1))
            log.debug(f"Retrieved {len(wallets)} wallets", source="DLWalletManager")
            return wallets
        except Exception as e:
            log.error(f"Failed to fetch wallets: {e}", source="DLWalletManager")
            return []

    def update_wallet(self, name: str, wallet: dict):
        try:
            cursor = self.db.get_cursor()
            cursor.execute(
                """
                UPDATE wallets SET
                    public_address = ?,
                    chrome_profile = ?,
                    private_address = ?,
                    image_path = ?,
                    balance = ?,
                    tags = ?,
                    is_active = ?,
                    type = ?
                WHERE name = ?
            """,
                (
                    wallet["public_address"],
                    wallet.get("chrome_profile", "Default"),
                    encrypt_key(wallet.get("private_address")),
                    wallet.get("image_path", ""),
                    wallet.get("balance", 0.0),
                    json.dumps(wallet.get("tags", [])),
                    int(wallet.get("is_active", True)),
                    wallet.get("type", "personal"),
                    name,
                ),
            )
            self.db.commit()
            log.info(f"Wallet updated: {name}", source="DLWalletManager")
        except Exception as e:
            log.error(f"Failed to update wallet {name}: {e}", source="DLWalletManager")



    def get_wallet_by_name(self, name: str) -> dict:
        try:
            cursor = self.db.get_cursor()
            cursor.execute("SELECT * FROM wallets WHERE name = ?", (name,))
            row = cursor.fetchone()
            if row:
                data = dict(row)
                data["private_address"] = decrypt_key(data.get("private_address"))
                tags = data.get("tags")
                if isinstance(tags, str):
                    try:
                        data["tags"] = json.loads(tags) if tags else []
                    except json.JSONDecodeError:
                        data["tags"] = [t.strip() for t in tags.split(",") if t.strip()]
                data["is_active"] = bool(data.get("is_active", 1))
                return data
            return None
        except Exception as e:
            from core.logging import log
            log.error(f"DLWalletManager failed to get wallet '{name}': {e}", source="DLWalletManager")
            return None

    def delete_wallet(self, name: str):
        try:
            cursor = self.db.get_cursor()
            cursor.execute("DELETE FROM wallets WHERE name = ?", (name,))
            self.db.commit()
            log.info(f"Wallet deleted: {name}", source="DLWalletManager")
        except Exception as e:
            log.error(f"Failed to delete wallet {name}: {e}", source="DLWalletManager")

    def delete_all_wallets(self):
        """Remove all wallet records from the database."""
        try:
            cursor = self.db.get_cursor()
            cursor.execute("DELETE FROM wallets")
            self.db.commit()
            log.success("🧹 All wallets deleted", source="DLWalletManager")
        except Exception as e:
            log.error(f"Failed to delete all wallets: {e}", source="DLWalletManager")
