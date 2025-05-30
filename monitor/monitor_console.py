#!/usr/bin/env python3

import sys
import os
import subprocess
from datetime import datetime

# Project path bootstrap
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, PROJECT_ROOT)

from monitor_core import MonitorCore
from monitor_registry import MonitorRegistry
from price_monitor import PriceMonitor
from operations_monitor import OperationsMonitor
from latency_monitor import LatencyMonitor
from position_monitor import PositionMonitor
from core.logging import log
from core.core_imports import configure_console_log

from data.data_locker import DataLocker

# ✅ Resolve correct DB path
DB_PATH = os.getenv("DB_PATH", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "mother_brain.db")))
configure_console_log()
data_locker = DataLocker(DB_PATH)
ledger = data_locker.ledger

# Register monitors
registry = MonitorRegistry()
registry.register("price_monitor", PriceMonitor())
registry.register("operations_monitor", OperationsMonitor())
registry.register("latency_monitor", LatencyMonitor())
registry.register("position_monitor", PositionMonitor())

core = MonitorCore(registry=registry)

# ───────────────────────────────────────────────

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def show_banner():
    clear_screen()
    log.banner("🧠 MONITOR CONSOLE")

def show_monitor_freshness():
    print("\n📊 Monitor Freshness Snapshot")
    print("-" * 40)
    for name in sorted(registry.get_all_monitors().keys()):
        try:
            status = ledger.get_status(name)
            ts = status.get("last_timestamp", "N/A")
            age = status.get("age_seconds", "???")
            freshness = f"{age}s ago" if ts != "N/A" else "No data"
            print(f"{name:<20} :: {freshness}")
        except Exception as e:
            print(f"{name:<20} :: ERROR: {e}")
    print("-" * 40)

def select_monitor(title: str):
    monitors = list(sorted(registry.get_all_monitors().keys()))
    if not monitors:
        log.warning("No monitors registered.", source="Console")
        return None

    print(f"\n{title}")
    for i, name in enumerate(monitors, start=1):
        print(f"{i}) {name}")
    try:
        choice = int(input("\nEnter number → ").strip())
        if 1 <= choice <= len(monitors):
            return monitors[choice - 1]
        else:
            log.warning("Invalid selection number.", source="Console")
            return None
    except ValueError:
        log.warning("Input must be a number.", source="Console")
        return None

def run_monitor():
    name = select_monitor("📡 Select Monitor to RUN")
    if not name:
        return
    log.banner(f"🚀 Running {name}")
    try:
        mon = registry.get(name)
        mon.run_cycle()
        log.success(f"{name} completed successfully.", source="Console")
    except Exception as e:
        log.error(f"{name} failed: {e}", source="Console")

def show_status():
    name = select_monitor("📊 Select Monitor to VIEW STATUS")
    if not name:
        return
    status = ledger.get_status(name)
    if status["last_timestamp"]:
        log.info(f"Last heartbeat for {name}", source="Console", payload=status)
    else:
        log.warning(f"No recent heartbeat found for '{name}'", source="Console")

def clear_ledger():
    name = select_monitor("🧼 Select Monitor to CLEAR LEDGER")
    if not name:
        return
    path = os.path.join("monitor", f"{name}_ledger.json")
    if not os.path.exists(path):
        log.warning(f"No legacy ledger found: {path}", source="Console")
        return
    try:
        os.remove(path)
        log.success(f"Ledger '{path}' cleared", source="Console")
    except Exception as e:
        log.error(f"Failed to clear ledger: {e}", source="Console")

def run_all():
    log.banner("🚀 Running All Monitors")
    core.run_all()

def run_tests():
    log.banner("🧪 Running Monitor Test Suite")
    try:
        subprocess.run([sys.executable, "test_monitor_core.py"], check=True)
    except subprocess.CalledProcessError:
        log.error("Test suite failed", source="Console")

def main_menu():
    while True:
        show_banner()
        print(f"🧠 Active DB: {DB_PATH}")
        show_monitor_freshness()

        print("""
    📡 MONITOR ACTIONS
    -----------------------------
    1) 🚀 Run a Monitor
    2) 📊 Show Monitor Status
    3) 🧪 Run Monitor Test Suite
    4) 🧼 Clear Legacy JSON Ledger
    5) 🚀 Run All Monitors

    ❌ OTHER
    -----------------------------
    0) ❌ Exit
        """)
        choice = input("Choose an option: ").strip()

        if choice == "1":
            run_monitor()
        elif choice == "2":
            show_status()
        elif choice == "3":
            run_tests()
        elif choice == "4":
            clear_ledger()
        elif choice == "5":
            run_all()
        elif choice == "0":
            log.success("Goodbye! Console closed.", source="Console")
            break
        else:
            log.warning("Invalid input. Please try again.", source="Console")

        input("\nPress ENTER to continue...")

if __name__ == "__main__":
    import sqlite3

    print("🧠 OPENING DB TO CONFIRM WRITE")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT monitor_name, timestamp FROM monitor_ledger ORDER BY timestamp DESC LIMIT 5")
    print("🧠 LATEST WRITES:")
    print(cur.fetchall())
    conn.close()

    main_menu()
