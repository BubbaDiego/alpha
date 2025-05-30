# ops_console.py

import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


from core.logging import log
from core.core_imports import configure_console_log, DB_PATH

from data.data_locker import DataLocker
from xcom.xcom_core import XComCore
from monitor.monitor_core import MonitorCore
from monitor.monitor_registry import MonitorRegistry
from monitor.price_monitor import PriceMonitor
from data.dl_system_data import DLSystemDataManager


configure_console_log()

dl = DataLocker(str(DB_PATH))  # Same DB as Sonic Dashboard
xcom = XComCore(dl.system)
sysman = dl.system

# Monitor Registration
registry = MonitorRegistry()
registry.register("price_monitor", PriceMonitor())
monitor_core = MonitorCore(registry=registry)

# ───────────────────────────────────────────────
def clear_screen(): os.system("cls" if os.name == "nt" else "clear")

def pause(): input("\n🔁 Press ENTER to continue...")

def banner(title): log.banner(f"🎛️ {title}")

# ───────────────────────────────────────────────
def menu_monitors():
    while True:
        banner("📡 MONITOR MENU")
        print("1) 🚀 Run Monitor")
        print("2) 🧠 Run All Monitors")
        print("3) 📊 Show Status")
        print("4) 🧼 Clear Ledger (legacy)")
        print("5) 🧪 Run Monitor Tests")
        print("b) 🔙 Back")
        choice = input("Choose > ").strip()

        if choice == "1":
            mon = select_monitor()
            if mon: run_monitor(mon)
        elif choice == "2":
            monitor_core.run_all()
        elif choice == "3":
            mon = select_monitor()
            if mon:
                status = dl.ledger.get_status(mon)
                log.info("Monitor Status", payload=status)
        elif choice == "4":
            mon = select_monitor()
            if mon:
                try:
                    os.remove(f"monitor/{mon}_ledger.json")
                    log.success(f"Ledger for {mon} deleted")
                except:
                    log.warning("No legacy ledger found")
        elif choice == "5":
            os.system("python test_monitor_core.py")
        elif choice.lower() == "b":
            break
        pause()

def select_monitor():
    names = list(sorted(registry.get_all_monitors().keys()))
    if not names: log.warning("No monitors registered"); return None
    for i, n in enumerate(names): print(f"{i+1}) {n}")
    try:
        sel = int(input("Select > ").strip())
        return names[sel-1] if 1 <= sel <= len(names) else None
    except:
        return None

def run_monitor(name):
    try:
        mon = registry.get(name)
        mon.run_cycle()
        log.success(f"{name} ran successfully")
    except Exception as e:
        log.error(f"{name} failed: {e}")

# ───────────────────────────────────────────────
def menu_xcom():
    while True:
        banner("📬 XCOM NOTIFICATION TESTING")
        print("1) 🔔 Send LOW Notification (email)")
        print("2) 📱 Send MEDIUM Notification (sms)")
        print("3) 📢 Send HIGH Notification (sms + voice + sound)")
        print("4) 🧾 Show Twilio Config")
        print("b) 🔙 Back")
        choice = input("Choose > ").strip()

        subj = "🔔 XCom Test"
        msg = "Hello, this is a test from SOC."

        if choice == "1":
            xcom.send_notification("LOW", subj, msg)
        elif choice == "2":
            xcom.send_notification("MEDIUM", subj, msg)
        elif choice == "3":
            xcom.send_notification("HIGH", subj, msg)
        elif choice == "4":
            api_cfg = xcom.config_service.get_provider("api")
            masked = {k: ("****" if "token" in k or "sid" in k else v) for k, v in api_cfg.items()}
            log.info("API Config", payload=masked)
        elif choice.lower() == "b":
            break
        pause()

# ───────────────────────────────────────────────
def menu_data():
    while True:
        banner("🗄️ DATA UTILITIES")
        print("1) 📦 List Prices")
        print("2) 📈 List Positions")
        print("3) 👛 List Wallets")
        print("4) 🧹 Clear Alerts")
        print("b) 🔙 Back")
        choice = input("Choose > ").strip()

        if choice == "1":
            for p in dl.prices.get_all_prices(): print(p)
        elif choice == "2":
            for p in dl.positions.get_all_positions(): print(p)
        elif choice == "3":
            for w in dl.wallets.get_wallets(): print(w)
        elif choice == "4":
            dl.alerts.clear_all_alerts()
            log.success("All alerts cleared")
        elif choice.lower() == "b":
            break
        pause()

# ───────────────────────────────────────────────
def menu_profile():
    while True:
        banner("🧩 PROFILE MANAGER")
        print("1) 👀 View Active Profile")
        print("2) 🗂️ List All Profiles")
        print("3) 📄 Dump Profile JSON")
        print("4) ✏️  Set Active Profile")
        print("b) 🔙 Back")
        choice = input("Choose > ").strip()

        if choice == "1":
            print(sysman.get_active_theme_profile())
        elif choice == "2":
            print(sysman.get_theme_profiles().keys())
        elif choice == "3":
            profile = sysman.get_active_theme_profile()
            import json; print(json.dumps(profile, indent=2))
        elif choice == "4":
            name = input("Enter profile name to activate: ").strip()
            sysman.set_active_theme_profile(name)
            log.success(f"Profile '{name}' set as active")
        elif choice.lower() == "b":
            break
        pause()

# ───────────────────────────────────────────────
def menu_sysvars():
    banner("🧠 SYSTEM VARS")
    vars = sysman.get_last_update_times().__dict__
    log.info("System Vars Snapshot", payload=vars)
    pause()

# ───────────────────────────────────────────────
def menu_thresholds():
    banner("🎯 ALERT THRESHOLDS")
    cursor = dl.db.get_cursor()
    if not cursor:
        log.error("No DB cursor available; cannot load alert thresholds.")
        pause()
        return
    rows = cursor.execute("SELECT * FROM alert_thresholds").fetchall()
    for r in rows:
        print(f"{r['alert_type']} ({r['alert_class']}): low={r['low']}, med={r['medium']}, high={r['high']}")
    pause()

# ───────────────────────────────────────────────
def menu_ops_test():
    banner("🧪 OPS TEST")
    xcom.send_notification("LOW", "Ops Test", "Ping from SonicOpsConsole")
    xcom.send_notification("MEDIUM", "Ops Test", "Ping from SonicOpsConsole")
    xcom.send_notification("HIGH", "Ops Test", "Ping from SonicOpsConsole")
    pause()

# ───────────────────────────────────────────────

# ───────────────────────────────────────────────
def main():
    while True:
        clear_screen()
        banner("🎛️ SONIC OPERATIONS CONSOLE")
        print(f"📂 DB: {DB_PATH}")
        print("👤 Active Profile:", sysman.get_active_theme_profile())

        print("""
1) 📡 Monitors
2) 📬 XCom: Notification & Twilio Settings
3) 🗄️ Database / Data Utilities
4) 🧩 Manage Profile
5) 🧠 Inspect System Vars
6) 🎯 Alert Thresholds & Settings
7) 🧪 Operations Test
q) ❌ Quit
        """)
        cmd = input("Choose an option > ").strip().lower()
        if cmd == "1": menu_monitors()
        elif cmd == "2": menu_xcom()
        elif cmd == "3": menu_data()
        elif cmd == "4": menu_profile()
        elif cmd == "5": menu_sysvars()
        elif cmd == "6": menu_thresholds()
        elif cmd == "7": menu_ops_test()
        elif cmd == "q":
            log.success("Console exited. Goodbye 👋", source="SOC")
            break
        else:
            log.warning("Invalid input. Try again.")

# ───────────────────────────────────────────────
if __name__ == "__main__":
    main()
