import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import sqlite3
from datetime import datetime, timezone
from uuid import uuid4

from data.models import AlertThreshold, AlertLevel, AlertType
from data.alert import Alert
from alert_core.threshold_service import ThresholdService
from alert_core.alert_evaluation_service import AlertEvaluationService
from data.dl_thresholds import DLThresholdManager


# === MOCK DB WRAPPER ===
class DBWrapper:
    def __init__(self, conn):
        self.conn = conn
    def get_cursor(self):
        return self.conn.cursor()
    def commit(self):
        return self.conn.commit()


# === FAKE REPO WRAPPER ===
class FakeRepo:
    def __init__(self, db_wrapper):
        class DL:
            def __init__(self, db): self.db = db
        self.data_locker = DL(db_wrapper)


# === DB INIT ===
def init_db():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE alerts (
            id TEXT PRIMARY KEY,
            created_at TEXT,
            alert_type TEXT,
            alert_class TEXT,
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
        )
    """)

    cur.execute("""
        CREATE TABLE alert_thresholds (
            id TEXT PRIMARY KEY,
            alert_type TEXT NOT NULL,
            alert_class TEXT NOT NULL,
            metric_key TEXT NOT NULL,
            condition TEXT NOT NULL,
            low REAL NOT NULL,
            medium REAL NOT NULL,
            high REAL NOT NULL,
            enabled BOOLEAN DEFAULT 1,
            last_modified TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    return DBWrapper(conn)


# === THRESHOLD SEED ===
def seed_thresholds(dl_mgr: DLThresholdManager):
    threshold = AlertThreshold(
        id=str(uuid4()),
        alert_type="Profit",
        alert_class="Position",
        metric_key="profit",
        condition="ABOVE",
        low=10,
        medium=50,
        high=100,
        enabled=True,
        last_modified=datetime.now(timezone.utc).isoformat()
    )
    assert dl_mgr.insert(threshold), "❌ Failed to insert test threshold"


# === ALERT SEED ===
def seed_alert(db):
    cursor = db.get_cursor()
    alert = {
        "id": str(uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "alert_type": "Profit",
        "alert_class": "Position",
        "asset_type": "BTC",
        "trigger_value": 60.0,
        "condition": "ABOVE",
        "notification_type": "SMS",
        "level": "Normal",
        "last_triggered": None,
        "status": "Active",
        "frequency": 1,
        "counter": 0,
        "liquidation_distance": 0.0,
        "travel_percent": 0.0,
        "liquidation_price": 0.0,
        "notes": "E2E test alert",
        "description": "profit",
        "position_reference_id": "pos-123",
        "evaluated_value": 75.0,
        "position_type": "long"
    }

    cursor.execute("""
        INSERT INTO alerts (
            id, created_at, alert_type, alert_class, asset_type,
            trigger_value, condition, notification_type, level,
            last_triggered, status, frequency, counter, liquidation_distance,
            travel_percent, liquidation_price, notes, description,
            position_reference_id, evaluated_value, position_type
        ) VALUES (
            :id, :created_at, :alert_type, :alert_class, :asset_type,
            :trigger_value, :condition, :notification_type, :level,
            :last_triggered, :status, :frequency, :counter, :liquidation_distance,
            :travel_percent, :liquidation_price, :notes, :description,
            :position_reference_id, :evaluated_value, :position_type
        )
    """, alert)

    db.commit()
    return alert["id"]


# === RUN E2E TEST ===
def run_evaluation_test():
    print("🚀 INIT: Starting full evaluation test...")
    db = init_db()

    dl_mgr = DLThresholdManager(db)
    seed_thresholds(dl_mgr)
    alert_id = seed_alert(db)

    row = db.get_cursor().execute("SELECT * FROM alerts WHERE id = ?", (alert_id,)).fetchone()
    alert = Alert(**dict(row))

    threshold_service = ThresholdService(db)
    evaluator = AlertEvaluationService(threshold_service)
    evaluator.inject_repo(FakeRepo(db))

    evaluated = evaluator.evaluate(alert)
    evaluator.update_alert_level(alert.id, evaluated.level)
    evaluator.update_alert_evaluated_value(alert.id, evaluated.evaluated_value)

    final = db.get_cursor().execute("SELECT level, evaluated_value FROM alerts WHERE id = ?", (alert_id,)).fetchone()
    assert final["level"] == "Medium", f"❌ Expected Medium, got {final['level']}"
    assert final["evaluated_value"] == 75.0, f"❌ Value mismatch: {final['evaluated_value']}"

    print("✅ TEST PASSED: Alert successfully evaluated and DB updated ✅")


if __name__ == "__main__":
    run_evaluation_test()
