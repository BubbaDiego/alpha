# dl_traders.py
"""
Author: BubbaDiego
Module: DLTraderManager
Description:
    Provides CRUD operations for managing Trader objects in the database.
    Each trader is stored as a JSON blob for flexibility.
"""

import json
from datetime import datetime
from uuid import uuid4
from core.core_imports import log


class DLTraderManager:
    def __init__(self, db):
        self.db = db
        log.debug("DLTraderManager initialized.", source="DLTraderManager")

        self._initialize_table()

    def _initialize_table(self):
        cursor = self.db.get_cursor()
        if not cursor:
            log.error("❌ DB unavailable for trader table init", source="DLTraderManager")
            return
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS traders (
                name TEXT PRIMARY KEY,
                trader_json TEXT NOT NULL,
                created_at TEXT,
                last_updated TEXT
            )
        """)
        self.db.commit()

    def create_trader(self, trader: dict):
        try:
            name = trader.get("name")
            if not name:
                raise ValueError("Trader 'name' is required")

            trader_json = json.dumps(trader, indent=2)
            now = datetime.now().isoformat()

            cursor = self.db.get_cursor()
            cursor.execute("""
                INSERT INTO traders (name, trader_json, created_at, last_updated)
                VALUES (?, ?, ?, ?)
            """, (name, trader_json, now, now))

            self.db.commit()
            log.success(f"✅ Trader created: {name}", source="DLTraderManager")
        except Exception as e:
            log.error(f"❌ Failed to create trader: {e}", source="DLTraderManager")

    def get_trader_by_name(self, name: str) -> dict:
        try:
            cursor = self.db.get_cursor()
            cursor.execute("SELECT trader_json FROM traders WHERE name = ?", (name,))
            row = cursor.fetchone()
            return json.loads(row["trader_json"]) if row else None
        except Exception as e:
            log.error(f"❌ Failed to retrieve trader '{name}': {e}", source="DLTraderManager")
            return None

    def list_traders(self) -> list:
        try:
            cursor = self.db.get_cursor()
            cursor.execute("SELECT trader_json FROM traders")
            rows = cursor.fetchall()
            return [json.loads(row["trader_json"]) for row in rows]
        except Exception as e:
            log.error(f"❌ Failed to list traders: {e}", source="DLTraderManager")
            return []

    def update_trader(self, name: str, fields: dict):
        try:
            trader = self.get_trader_by_name(name)
            if not trader:
                log.warning(f"⚠️ Trader not found for update: {name}", source="DLTraderManager")
                return

            trader.update(fields)
            trader_json = json.dumps(trader, indent=2)
            now = datetime.now().isoformat()

            cursor = self.db.get_cursor()
            cursor.execute("""
                UPDATE traders
                SET trader_json = ?, last_updated = ?
                WHERE name = ?
            """, (trader_json, now, name))

            self.db.commit()
            log.info(f"🛠️ Trader updated: {name}", source="DLTraderManager")
        except Exception as e:
            log.error(f"❌ Failed to update trader '{name}': {e}", source="DLTraderManager")

    def delete_trader(self, name: str):
        try:
            cursor = self.db.get_cursor()
            cursor.execute("DELETE FROM traders WHERE name = ?", (name,))
            self.db.commit()
            log.info(f"🗑️ Trader deleted: {name}", source="DLTraderManager")
        except Exception as e:
            log.error(f"❌ Failed to delete trader '{name}': {e}", source="DLTraderManager")
