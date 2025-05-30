import sqlite3

DB_PATH = "mother_brain.db"
MONITOR_NAME = "sonic_monitor"
NEW_INTERVAL = 111

def set_sonic_interval():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Ensure the row exists (insert if not)
    cursor.execute("""
        INSERT INTO monitor_heartbeat (monitor_name, last_run, interval_seconds)
        VALUES (?, datetime('now'), ?)
        ON CONFLICT(monitor_name) DO UPDATE SET interval_seconds = excluded.interval_seconds
    """, (MONITOR_NAME, NEW_INTERVAL))
    conn.commit()
    print(f"✅ Set interval_seconds for {MONITOR_NAME} to {NEW_INTERVAL}.")
    # Show the updated row
    cursor.execute("SELECT * FROM monitor_heartbeat WHERE monitor_name = ?", (MONITOR_NAME,))
    print(cursor.fetchone())
    conn.close()

if __name__ == "__main__":
    set_sonic_interval()
