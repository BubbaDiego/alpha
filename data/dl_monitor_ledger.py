import sqlite3
import json
import uuid
from datetime import datetime, timezone
from core.logging import log

class DLMonitorLedgerManager:
    def __init__(self, db):
        self.db = db
        self.ensure_table()

    def ensure_table(self):
        cursor = self.db.get_cursor()
        if not cursor:
            log.error("❌ DB unavailable, ledger table not created", source="DLMonitorLedger")
            return
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS monitor_ledger (
                id TEXT PRIMARY KEY,
                monitor_name TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                status TEXT NOT NULL,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.db.commit()
        log.debug("monitor_ledger table ensured", source="DLMonitorLedger")

    def insert_ledger_entry(self, monitor_name: str, status: str, metadata: dict = None):
        import uuid
        import json

        entry = {
            "id": str(uuid.uuid4()),
            "monitor_name": monitor_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": status,
            "metadata": json.dumps(metadata or {})
        }


        cursor = self.db.get_cursor()
        if not cursor:
            log.error("❌ DB unavailable, ledger entry not stored", source="DLMonitorLedger")
            return
        cursor.execute("""
            INSERT INTO monitor_ledger (
                id, monitor_name, timestamp, status, metadata
            ) VALUES (
                :id, :monitor_name, :timestamp, :status, :metadata
            )
        """, entry)
        self.db.commit()
        log.success(f"🧾 Ledger written to DB for {monitor_name}", source="DLMonitorLedger")

    def get_last_entry(self, monitor_name: str) -> dict:
        cursor = self.db.get_cursor()
        if not cursor:
            log.error("❌ DB unavailable, cannot fetch ledger entry", source="DLMonitorLedger")
            return {}
        cursor.execute("""
            SELECT timestamp, status, metadata
            FROM monitor_ledger
            WHERE monitor_name = ?
            ORDER BY timestamp DESC
            LIMIT 1
        """, (monitor_name,))

        row = cursor.fetchone()

        if not row:
            return {}
        result = {
            "timestamp": row[0],
            "status": row[1],
            "metadata": row[2]
        }
        return result

    def get_status(self, monitor_name: str) -> dict:

        entry = self.get_last_entry(monitor_name)
        if not entry or not entry.get("timestamp"):
            return {"last_timestamp": None, "age_seconds": 9999}

        try:
            raw_ts = entry["timestamp"]
            if raw_ts.endswith("Z"):
                raw_ts = raw_ts.replace("Z", "+00:00")
            last_ts = datetime.fromisoformat(raw_ts)
            now = datetime.now(timezone.utc)
            age = (now - last_ts).total_seconds()
            return {
                "last_timestamp": last_ts.isoformat(),
                "age_seconds": round(age),
                "status": entry.get("status", "Unknown")
            }
        except Exception as e:
            log.error(f"🧨 Failed to parse timestamp for {monitor_name}: {e}", source="DLMonitorLedger")
            return {"last_timestamp": None, "age_seconds": 9999}

