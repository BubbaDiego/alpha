# dl_positions.py
"""
Author: BubbaDiego
Module: DLPositionManager
Description:
    Provides CRUD operations for managing trading positions in the database.
    Supports position creation, listing all positions, and deletion by ID.

Dependencies:
    - DatabaseManager from database.py
    - ConsoleLogger from console_logger.py
"""
import os
from uuid import uuid4
from datetime import datetime
import sqlite3
from core.core_imports import log


class DLPositionManager:
    def __init__(self, db):
        self.db = db
        log.debug("DLPositionManager initialized.", source="DLPositionManager")

    def create_position(self, position: dict):
        from datetime import datetime
        import os
        import json
        import traceback

        try:
            # ✅ Default injection — retain logic
            position.setdefault("id", str(uuid4()))
            position.setdefault("asset_type", "UNKNOWN")
            position.setdefault("entry_price", 0.0)
            position.setdefault("liquidation_price", 0.0)
            position.setdefault("position_type", "LONG")
            position.setdefault("wallet_name", "Unspecified")
            position.setdefault("collateral", 0.0)
            position.setdefault("size", 0.0)
            position.setdefault("leverage", 1.0)
            position.setdefault("value", 0.0)
            position.setdefault("current_price", 0.0)
            position.setdefault("travel_percent", 0.0)
            position.setdefault("pnl_after_fees_usd", 0.0)
            position.setdefault("current_heat_index", 0.0)
            position.setdefault("heat_index", position["current_heat_index"])
            position.setdefault("liquidation_distance", 0.0)
            position.setdefault("status", "ACTIVE")
            position.setdefault("last_updated", datetime.now().isoformat())
            position.setdefault("alert_reference_id", None)
            position.setdefault("hedge_buddy_id", None)
            position.setdefault("profit", position["value"])

            # ✅ Fetch DB schema and sanitize fields
            cursor = self.db.get_cursor()
            cursor.execute("PRAGMA table_info(positions);")
            db_columns = set(row[1] for row in cursor.fetchall())
            valid_position = {k: v for k, v in position.items() if k in db_columns}

            # ⚠️ Warn about stripped fields
            stripped_keys = set(position.keys()) - db_columns
            if stripped_keys:
                log.warning(f"🧹 Stripped non-schema keys: {stripped_keys}", source="DLPositionManager")

            # ✅ Build dynamic SQL from allowed keys
            fields = ", ".join(valid_position.keys())
            placeholders = ", ".join(f":{k}" for k in valid_position.keys())

            cursor.execute(f"""
                INSERT INTO positions (
                    {fields}
                ) VALUES (
                    {placeholders}
                )
            """, valid_position)

            self.db.commit()
            log.success(f"💾 Position INSERTED: {position['id']}", source="DLPositionManager")

        except Exception as e:
            err_msg = f"❌ Failed to insert position {position.get('id')}: {e}"
            log.error(err_msg, source="DLPositionManager")

            tb = traceback.format_exc()
            log.debug(tb, source="DLPositionManager")

            try:
                logs_dir = os.path.join(os.path.dirname(self.db.db_path), "..", "logs")
                os.makedirs(logs_dir, exist_ok=True)
                log_path = os.path.join(logs_dir, "dl_failed_inserts.log")

                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(f"\n[{datetime.now().isoformat()}] :: INSERT FAIL: {position.get('id')}\n")
                    f.write(f"{err_msg}\n")
                    f.write("Payload:\n")
                    f.write(json.dumps(position, indent=2))
                    f.write("\nTraceback:\n")
                    f.write(tb)
                    f.write("\n" + "=" * 60 + "\n")

                log.warning(f"📄 DL insert error written to: {log_path}", source="DLPositionManager")

            except Exception as file_err:
                log.error(f"⚠️ Failed to write insert failure log: {file_err}", source="DLPositionManager")

    def get_all_positions(self) -> list:
        try:
            cursor = self.db.get_cursor()
            try:
                cursor.execute("SELECT * FROM positions")
            except sqlite3.DatabaseError as e:
                err_msg = str(e)
                if "malformed" in err_msg or "file is not a database" in err_msg:
                    log.error(f"Error fetching positions: {e}", source="DLPositionManager")
                    log.warning(
                        "Database appears corrupt. Attempting recovery...",
                        source="DLPositionManager",
                    )
                    self.db.recover_database()
                    return []
                raise
            rows = cursor.fetchall()
            log.debug(
                f"Fetched {len(rows)} positions", source="DLPositionManager"
            )
            return [dict(row) for row in rows]
        except Exception as e:
            err_msg = str(e)
            if "malformed" in err_msg or "file is not a database" in err_msg:
                log.error(f"Error fetching positions: {e}", source="DLPositionManager")
                log.warning(
                    "Database appears corrupt. Attempting recovery...",
                    source="DLPositionManager",
                )
                self.db.recover_database()
                return []
            log.error(f"Error fetching positions: {e}", source="DLPositionManager")
            return []

    def _delete_all_positions(self):
        self.delete_all_positions()


    def delete_position(self, position_id: str):
        try:
            cursor = self.db.get_cursor()
            cursor.execute("DELETE FROM positions WHERE id = ?", (position_id,))
            self.db.commit()
            log.info(f"Deleted position {position_id}", source="DLPositionManager")
        except Exception as e:
            log.error(f"Failed to delete position {position_id}: {e}", source="DLPositionManager")

    def delete_all_positions(self):
        try:
            cursor = self.db.get_cursor()
            cursor.execute("DELETE FROM positions")
            self.db.commit()
            cursor.close()
            log.success("🧹 All positions got fucked", source="DLPositionManager")
        except Exception as e:
            log.error(f"❌ Failed to wipe positions: {e}", source="DLPositionManager")
            # Do not propagate DB errors
            return

    # Primary method
    def delete_positions(self):
        self._delete_all_positions()

    # Alias for dev tools / backcompat
    def clear_positions(self):
        self._delete_all_positions()

    def record_positions_totals_snapshot(self, totals: dict):
        try:
            snapshot_id = str(uuid4())
            snapshot_time = datetime.now().isoformat()
            cursor = self.db.get_cursor()
            if not cursor:
                log.error("❌ DB unavailable for snapshot", source="DLPositionManager")
                return
            cursor.execute("""
                INSERT INTO positions_totals_history (
                    id, snapshot_time, total_size, total_value, total_collateral,
                    avg_leverage, avg_travel_percent, avg_heat_index
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                snapshot_id,
                snapshot_time,
                totals.get("total_size", 0.0),
                totals.get("total_value", 0.0),
                totals.get("total_collateral", 0.0),
                totals.get("avg_leverage", 0.0),
                totals.get("avg_travel_percent", 0.0),
                totals.get("avg_heat_index", 0.0)
            ))
            self.db.commit()
            log.success(f"📸 Snapshot recorded: {snapshot_id}", source="DataLocker")
        except Exception as e:
            log.error(f"❌ Failed to record position snapshot: {e}", source="DataLocker")
            return

    def initialize_schema(db):
        cursor = db.get_cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS positions (
            id TEXT PRIMARY KEY,
            asset_type TEXT,
            entry_price REAL,
            liquidation_price REAL,
            position_type TEXT,
            wallet_name TEXT,
            current_heat_index REAL,
            pnl_after_fees_usd REAL,
            travel_percent REAL,
            liquidation_distance REAL
        )""")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id TEXT PRIMARY KEY,
            created_at TEXT,
            alert_type TEXT,
            alert_class TEXT,
            asset TEXT,
            asset_type TEXT,
            trigger_value REAL,
            condition TEXT,
            notification_type TEXT,
            level TEXT,
            last_triggered TEXT,
            status TEXT,
            frequency INTEGER,
            counter INTEGER,
            liquidation_distance REAL,
            travel_percent REAL,
            liquidation_price REAL,
            notes TEXT,
            description TEXT,
            position_reference_id TEXT,
            evaluated_value REAL,
            position_type TEXT
        )""")
        db.commit()

    def insert_position(self, position: dict):
        try:
            cursor = self.db.get_cursor()
            cursor.execute("""
                INSERT INTO positions (
                    id, asset_type, entry_price, liquidation_price,
                    position_type, wallet_name, current_heat_index,
                    pnl_after_fees_usd, travel_percent, liquidation_distance
                ) VALUES (
                    :id, :asset_type, :entry_price, :liquidation_price,
                    :position_type, :wallet_name, :current_heat_index,
                    :pnl_after_fees_usd, :travel_percent, :liquidation_distance
                )
            """, position)
            self.db.commit()
            log.success(f"✅ Position inserted for test: {position['id']}", source="DLPositionManager")
        except Exception as e:
            log.error(f"❌ Failed to insert test position: {e}", source="DLPositionManager")

    def get_active_positions(self) -> list:
        try:
            cursor = self.db.get_cursor()
            cursor.execute("SELECT * FROM positions WHERE status = 'ACTIVE'")
            rows = cursor.fetchall()
            log.debug(f"🔎 Found {len(rows)} active positions", source="DLPositionManager")
            return [dict(row) for row in rows]
        except Exception as e:
            log.error(f"❌ Failed to fetch active positions: {e}", source="DLPositionManager")
            return []

    def get_active_positions_by_wallet(self, wallet_name: str) -> list:
        """Return active positions for a specific wallet."""
        try:
            cursor = self.db.get_cursor()
            cursor.execute(
                "SELECT * FROM positions WHERE status = 'ACTIVE' AND wallet_name = ?",
                (wallet_name,),
            )
            rows = cursor.fetchall()
            log.debug(
                f"🔎 Found {len(rows)} active positions for {wallet_name}",
                source="DLPositionManager",
            )
            return [dict(row) for row in rows]
        except Exception as e:
            log.error(
                f"❌ Failed to fetch active positions for {wallet_name}: {e}",
                source="DLPositionManager",
            )
            return []

    def get_position_by_id(self, pos_id: str):
        try:
            cursor = self.db.get_cursor()
            if not cursor:
                return None
            cursor.execute("SELECT * FROM positions WHERE id = ?", (pos_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            log.error(f"❌ Failed to fetch position {pos_id}: {e}", source="DLPositionManager")
            return None
