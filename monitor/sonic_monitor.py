import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import asyncio
import logging
import time
from datetime import datetime, timezone
from cyclone.cyclone_engine import Cyclone

from data.data_locker import DataLocker
from core.constants import DB_PATH

MONITOR_NAME = "sonic_monitor"
DEFAULT_INTERVAL = 60  # fallback if nothing set in DB

def get_monitor_interval(db_path=DB_PATH, monitor_name=MONITOR_NAME):
    dl = DataLocker(str(db_path))
    cursor = dl.db.get_cursor()
    if not cursor:
        logging.error("No DB cursor available; using default interval")
        return DEFAULT_INTERVAL
    cursor.execute(
        "SELECT interval_seconds FROM monitor_heartbeat WHERE monitor_name = ?",
        (monitor_name,)
    )
    row = cursor.fetchone()
    if row and row[0]:
        try:
            return int(row[0])
        except Exception:
            pass
    return DEFAULT_INTERVAL

def update_heartbeat(monitor_name, interval_seconds, db_path=DB_PATH):
    dl = DataLocker(str(db_path))
    cursor = dl.db.get_cursor()
    if not cursor:
        logging.error("No DB cursor available; heartbeat not recorded")
        return
    cursor.execute("""
        INSERT INTO monitor_heartbeat (monitor_name, last_run, interval_seconds)
        VALUES (?, datetime('now'), ?)
        ON CONFLICT(monitor_name) DO UPDATE SET last_run = excluded.last_run, interval_seconds = excluded.interval_seconds
    """, (monitor_name, interval_seconds))
    dl.db.commit()

def heartbeat(loop_counter: int):
    timestamp = datetime.now(timezone.utc).isoformat()
    logging.info("❤️ SonicMonitor heartbeat #%d at %s", loop_counter, timestamp)

async def sonic_cycle(loop_counter: int, cyclone: Cyclone, interval: int):
    logging.info("🔄 SonicMonitor cycle #%d starting", loop_counter)
    await cyclone.run_cycle()
    heartbeat(loop_counter)
    update_heartbeat(MONITOR_NAME, interval)
    logging.info("✅ SonicMonitor cycle #%d complete", loop_counter)

def main():
    loop_counter = 0

    from monitor.monitor_core import MonitorCore
    monitor_core = MonitorCore()
    cyclone = Cyclone(monitor_core=monitor_core)

    # --- Ensure the heartbeat table exists ---
    dl = DataLocker(str(DB_PATH))
    cursor = dl.db.get_cursor()
    if not cursor:
        logging.error("No DB cursor available; cannot initialize heartbeat table")
        return
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS monitor_heartbeat (
            monitor_name TEXT PRIMARY KEY,
            last_run TIMESTAMP NOT NULL,
            interval_seconds INTEGER NOT NULL
        )
    """)
    dl.db.commit()

    loop = asyncio.get_event_loop()
    try:
        while True:
            # Always use the latest interval from the DB for max flexibility
            interval = get_monitor_interval()
            loop_counter += 1
            loop.run_until_complete(sonic_cycle(loop_counter, cyclone, interval))
            time.sleep(interval)
    except KeyboardInterrupt:
        logging.info("SonicMonitor terminated by user.")

if __name__ == "__main__":
    main()
