# dl_portfolio.py
"""
Author: BubbaDiego
Module: DLPortfolioManager
Description:
    Handles recording and retrieving portfolio snapshots including total size,
    value, collateral, and metrics like leverage and heat index over time.

Dependencies:
    - DatabaseManager from database.py
    - ConsoleLogger from console_logger.py
"""

from uuid import uuid4
from datetime import datetime
from core.core_imports import log

class DLPortfolioManager:
    def __init__(self, db):
        self.db = db
        log.debug("DLPortfolioManager initialized.", source="DLPortfolioManager")

    def record_snapshot(self, totals: dict):
        try:
            cursor = self.db.get_cursor()
            cursor.execute("""
                INSERT INTO positions_totals_history (
                    id, snapshot_time, total_size, total_value,
                    total_collateral, avg_leverage, avg_travel_percent, avg_heat_index
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(uuid4()),
                datetime.now().isoformat(),
                totals.get("total_size", 0.0),
                totals.get("total_value", 0.0),
                totals.get("total_collateral", 0.0),
                totals.get("avg_leverage", 0.0),
                totals.get("avg_travel_percent", 0.0),
                totals.get("avg_heat_index", 0.0)
            ))
            self.db.commit()
            log.success("Portfolio snapshot recorded", source="DLPortfolioManager")
        except Exception as e:
            log.error(f"Failed to record portfolio snapshot: {e}", source="DLPortfolioManager")

    def get_snapshots(self) -> list:
        try:
            cursor = self.db.get_cursor()
            cursor.execute("SELECT * FROM positions_totals_history ORDER BY snapshot_time ASC")
            rows = cursor.fetchall()
            log.debug(f"Retrieved {len(rows)} portfolio snapshots", source="DLPortfolioManager")
            return [dict(row) for row in rows]
        except Exception as e:
            log.error(f"Failed to fetch portfolio snapshots: {e}", source="DLPortfolioManager")
            return []

    def get_latest_snapshot(self) -> dict:
        try:
            cursor = self.db.get_cursor()
            cursor.execute("SELECT * FROM positions_totals_history ORDER BY snapshot_time DESC LIMIT 1")
            row = cursor.fetchone()
            if row:
                log.debug("Latest portfolio snapshot retrieved", source="DLPortfolioManager")
            return dict(row) if row else {}
        except Exception as e:
            log.error(f"Failed to fetch latest snapshot: {e}", source="DLPortfolioManager")
            return {}
    def add_entry(self, entry: dict):
        """Insert a manual portfolio entry into positions_totals_history."""
        try:
            cursor = self.db.get_cursor()
            if "id" not in entry:
                entry["id"] = str(uuid4())
            if "snapshot_time" not in entry:
                entry["snapshot_time"] = datetime.now().isoformat()
            cursor.execute(
                """
                INSERT INTO positions_totals_history (
                    id, snapshot_time, total_size, total_value,
                    total_collateral, avg_leverage, avg_travel_percent, avg_heat_index
                ) VALUES (:id, :snapshot_time, :total_size, :total_value,
                          :total_collateral, :avg_leverage, :avg_travel_percent, :avg_heat_index)
                """,
                {
                    "id": entry["id"],
                    "snapshot_time": entry.get("snapshot_time"),
                    "total_size": entry.get("total_size", 0.0),
                    "total_value": entry.get("total_value", 0.0),
                    "total_collateral": entry.get("total_collateral", 0.0),
                    "avg_leverage": entry.get("avg_leverage", 0.0),
                    "avg_travel_percent": entry.get("avg_travel_percent", 0.0),
                    "avg_heat_index": entry.get("avg_heat_index", 0.0),
                },
            )
            self.db.commit()
            log.success(f"Portfolio entry added: {entry['id']}", source="DLPortfolioManager")
        except Exception as e:
            log.error(f"Failed to add portfolio entry: {e}", source="DLPortfolioManager")

    def update_entry(self, entry_id: str, fields: dict):
        """Update fields of an existing portfolio entry by id."""
        try:
            if not fields:
                return
            cursor = self.db.get_cursor()
            set_clause = ", ".join(f"{k} = ?" for k in fields.keys())
            params = list(fields.values()) + [entry_id]
            cursor.execute(
                f"UPDATE positions_totals_history SET {set_clause} WHERE id = ?",
                params,
            )
            self.db.commit()
            log.info(f"Portfolio entry updated: {entry_id}", source="DLPortfolioManager")
        except Exception as e:
            log.error(f"Failed to update portfolio entry {entry_id}: {e}", source="DLPortfolioManager")

    def get_entry_by_id(self, entry_id: str) -> dict:
        """Return a portfolio entry by its ID."""
        try:
            cursor = self.db.get_cursor()
            cursor.execute(
                "SELECT * FROM positions_totals_history WHERE id = ?",
                (entry_id,),
            )
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            log.error(f"Failed to fetch portfolio entry {entry_id}: {e}", source="DLPortfolioManager")
            return None

    def delete_entry(self, entry_id: str):
        """Delete a portfolio entry by ID."""
        try:
            cursor = self.db.get_cursor()
            cursor.execute(
                "DELETE FROM positions_totals_history WHERE id = ?",
                (entry_id,),
            )
            self.db.commit()
            log.info(f"Portfolio entry deleted: {entry_id}", source="DLPortfolioManager")
        except Exception as e:
            log.error(f"Failed to delete portfolio entry {entry_id}: {e}", source="DLPortfolioManager")
