# test_alert_db_levels.py

import sqlite3
import os

DB_PATH = "C:/v0.8/data/mother_brain.db"  # 🔧 update path if needed

def fetch_alert_levels():
    if not os.path.exists(DB_PATH):
        print(f"❌ DB not found at: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = """
    SELECT id, alert_type, alert_class, asset, evaluated_value, level, created_at
    FROM alerts
    ORDER BY created_at DESC
    LIMIT 20
    """

    cursor.execute(sql)
    alerts = cursor.fetchall()
    print("\n📊 Last 20 Alerts:")
    for alert in alerts:
        print(f"🆔 {alert['id']}")
        print(f"📌 Type: {alert['alert_type']} | Class: {alert['alert_class']}")
        print(f"💰 Asset: {alert['asset']} | 📈 Evaluated: {alert['evaluated_value']} | 📊 Level: {alert['level']}")
        print(f"🕒 Created: {alert['created_at']}")
        print("-" * 60)

    cursor.close()
    conn.close()


if __name__ == "__main__":
    fetch_alert_levels()
