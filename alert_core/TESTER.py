import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import sqlite3
from datetime import datetime, timezone
from uuid import uuid4
from data.dl_thresholds import DLThresholdManager

DB_PATH = ":memory:"


# === Ensure schema exists ===
def ensure_schema(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alert_thresholds (
            id TEXT PRIMARY KEY,
            alert_type TEXT NOT NULL,
            alert_class TEXT NOT NULL,
            metric_key TEXT NOT NULL,
            condition TEXT NOT NULL,
            low REAL NOT NULL,
            medium REAL NOT NULL,
            high REAL NOT NULL,
            enabled BOOLEAN DEFAULT 1,
            last_modified TEXT DEFAULT CURRENT_TIMESTAMP,
            low_notify TEXT,
            medium_notify TEXT,
            high_notify TEXT
        )
    """)
    conn.commit()


# === Insert raw test threshold row ===
def insert_threshold(conn, t):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO alert_thresholds (
            id, alert_type, alert_class, metric_key, condition,
            low, medium, high, enabled,
            last_modified, low_notify, medium_notify, high_notify
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        t["id"], t["alert_type"], t["alert_class"], t["metric_key"], t["condition"],
        t["low"], t["medium"], t["high"], t["enabled"],
        t["last_modified"], t["low_notify"], t["medium_notify"], t["high_notify"]
    ))
    conn.commit()


# === Run test cases ===
def run_test():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    ensure_schema(conn)

    mgr = DLThresholdManager(DBWrapper(conn))

    test_cases = [
        {
            "alert_type": "Profit", "alert_class": "Position", "metric_key": "profit",
            "condition": "ABOVE",
            "low": 10, "medium": 50, "high": 100, "enabled": True,
            "low_notify": "SMS,Email,Voice",
            "medium_notify": "SMS,Email,Voice",
            "high_notify": "SMS,Email,Voice"
        },
        {
            "alert_type": "HeatIndex", "alert_class": "Position", "metric_key": "heatindex",
            "condition": "ABOVE",
            "low": 5, "medium": 15, "high": 25, "enabled": True,
            "low_notify": "Email",
            "medium_notify": "Email",
            "high_notify": "Email"
        },
        {
            "alert_type": "TotalValue", "alert_class": "Portfolio", "metric_key": "total_value",
            "condition": "ABOVE",
            "low": 10000, "medium": 25000, "high": 50000, "enabled": True,
            "low_notify": "",
            "medium_notify": "",
            "high_notify": "SMS"
        },
        {
            "alert_type": "PriceThreshold", "alert_class": "Market", "metric_key": "price",
            "condition": "ABOVE",
            "low": 20000, "medium": 30000, "high": 40000, "enabled": False,
            "low_notify": "",
            "medium_notify": "",
            "high_notify": ""
        }
    ]

    for t in test_cases:
        t["id"] = str(uuid4())
        t["last_modified"] = datetime.now(timezone.utc).isoformat()
        insert_threshold(conn, t)
        print(f"🧪 Inserted threshold: {t['alert_type']} ({t['alert_class']}) → {t['id']}")

        # Simulate updated data
        updated_fields = {
            "low": t["low"] + 5,
            "medium": t["medium"] + 10,
            "high": t["high"] + 20,
            "enabled": not t["enabled"],
            "low_notify": t["low_notify"].split(",") if t["low_notify"] else [],
            "medium_notify": t["medium_notify"].split(",") if t["medium_notify"] else [],
            "high_notify": t["high_notify"].split(",") if t["high_notify"] else []
        }

        success = mgr.update(t["id"], updated_fields)
        print("   ✅ Update:", "Success" if success else "❌ Failed")

        row = conn.cursor().execute("SELECT * FROM alert_thresholds WHERE id = ?", (t["id"],)).fetchone()
        print("   📄 DB:", {
            "low": row["low"],
            "medium": row["medium"],
            "high": row["high"],
            "enabled": row["enabled"],
            "low_notify": row["low_notify"],
            "medium_notify": row["medium_notify"],
            "high_notify": row["high_notify"]
        })


# === Mock wrapper to satisfy DLThresholdManager expectations ===
class DBWrapper:
    def __init__(self, conn):
        self.conn = conn
    def get_cursor(self):
        return self.conn.cursor()
    def commit(self):
        return self.conn.commit()


if __name__ == "__main__":
    run_test()
