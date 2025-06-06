"""Data access layer for Trader records.

This module persists Trader metadata in a simple SQLite table. When
retrieving trader dictionaries, missing fields are populated for
convenience:

* ``born_on`` - Defaults to the ``created_at`` timestamp stored in the
  database if not present in the JSON payload.
* ``initial_collateral`` - Defaults to ``0.0`` when absent.
"""

import json
from datetime import datetime
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
        log.route("Ensuring 'traders' table exists...", source="DLTraderManager")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS traders (
                name TEXT PRIMARY KEY,
                trader_json TEXT NOT NULL,
                created_at TEXT,
                last_updated TEXT
            )
        """)
        self.db.commit()
        log.success("✅ Trader table ready", source="DLTraderManager")

    def create_trader(self, trader: dict) -> bool:
        """Persist a new trader record.

        Returns ``True`` on success, ``False`` if any error occurs."""
        try:
            name = trader.get("name")
            if not name:
                raise ValueError("Trader 'name' is required")
            log.debug("Creating trader", source="DLTraderManager", payload=trader)

            now = datetime.now().isoformat()
            trader.setdefault("born_on", now)
            if "initial_collateral" not in trader:
                bal = trader.get("wallet_balance", 0.0)
                try:
                    bal = float(bal)
                except Exception:
                    bal = 0.0
                trader["initial_collateral"] = bal

            trader_json = json.dumps(trader, indent=2)
            now = datetime.now().isoformat()
            trader.setdefault("born_on", now)
            trader.setdefault("initial_collateral", 0.0)
            trader_json = json.dumps(trader, indent=2)

            cursor = self.db.get_cursor()
            if not cursor:
                raise RuntimeError("DB cursor unavailable")

            cursor.execute("""
                INSERT INTO traders (name, trader_json, created_at, last_updated)
                VALUES (?, ?, ?, ?)
            """, (name, trader_json, now, now))
            self.db.commit()
            log.success(f"✅ Trader created: {name}", source="DLTraderManager")
            return True
        except Exception as e:
            log.error(f"❌ Failed to create trader: {e}", source="DLTraderManager")
            return False

    def get_trader_by_name(self, name: str) -> dict:
        """Return a trader dict by name with default fields filled in."""
        try:
            log.info(
                f"🔍 Fetching trader by name: {name}", source="DLTraderManager"
            )
            cursor = self.db.get_cursor()
            cursor.execute(
                "SELECT trader_json, created_at FROM traders WHERE name = ?",
                (name,),
            )
            row = cursor.fetchone()
            trader = json.loads(row["trader_json"]) if row else None

            if trader is not None:
                # Fill defaults from DB metadata when missing
                if "born_on" not in trader:
                    trader["born_on"] = row["created_at"]
                trader.setdefault("initial_collateral", 0.0)
            log.debug(
                "Trader loaded", source="DLTraderManager", payload=trader or {})

            if trader is not None and "born_on" not in trader:
                trader["born_on"] = row["created_at"]
            log.debug("Trader loaded", source="DLTraderManager", payload=trader or {})

            return trader
        except Exception as e:
            log.error(f"❌ Failed to retrieve trader '{name}': {e}", source="DLTraderManager")
            return None

    def list_traders(self) -> list:
        """Return all traders with defaults applied."""
        try:
            log.route("Fetching traders from DB...", source="DLTraderManager")
            cursor = self.db.get_cursor()
            cursor.execute("SELECT trader_json, created_at FROM traders")
            rows = cursor.fetchall()
            traders = []
            for row in rows:

                trader = json.loads(row["trader_json"])
                if "born_on" not in trader:
                    trader["born_on"] = row["created_at"]
                trader.setdefault("initial_collateral", 0.0)
                traders.append(trader)
            log.debug(
                f"Loaded {len(traders)} traders from DB", source="DLTraderManager"
            )
            return traders
        except Exception as e:
            log.error(f"❌ Failed to list traders: {e}", source="DLTraderManager")
            return []

    def update_trader(self, name: str, fields: dict):
        try:
            log.debug(f"Attempting update on trader: {name}", source="DLTraderManager", payload=fields)
            trader = self.get_trader_by_name(name)
            if not trader:
                log.warning(f"⚠️ Trader not found for update: {name}", source="DLTraderManager")
                return

            trader.update(fields)
            trader_json = json.dumps(trader, indent=2)
            now = datetime.now().isoformat()

            cursor = self.db.get_cursor()
            cursor.execute(
                "UPDATE traders SET trader_json = ?, last_updated = ? WHERE name = ?",
                (trader_json, now, name),
            )
            self.db.commit()
            log.success(f"🔄 Trader updated: {name}", source="DLTraderManager")
        except Exception as e:
            log.error(f"❌ Failed to update trader '{name}': {e}", source="DLTraderManager")

    def delete_trader(self, name: str):
        try:
            log.route(f"Deleting trader: {name}", source="DLTraderManager")
            cursor = self.db.get_cursor()
            cursor.execute("DELETE FROM traders WHERE name = ?", (name,))
            deleted = cursor.rowcount > 0
            self.db.commit()
            if deleted:
                log.info(f"🗑️ Trader deleted: {name}", source="DLTraderManager")
            else:
                log.warning(f"Trader not found for deletion: {name}", source="DLTraderManager")
            return deleted
        except Exception as e:
            log.error(f"❌ Failed to delete trader '{name}': {e}", source="DLTraderManager")
            raise

    def delete_all_traders(self):
        """Remove all trader records from the database."""
        try:
            cursor = self.db.get_cursor()
            cursor.execute("DELETE FROM traders")
            self.db.commit()
            log.success("🧹 All traders deleted", source="DLTraderManager")
        except Exception as e:
            log.error(f"❌ Failed to delete all traders: {e}", source="DLTraderManager")

