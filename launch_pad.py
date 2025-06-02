#!/usr/bin/env python3
"""Sonic Launch console."""

import os
import sys
import subprocess
import time
import webbrowser
import asyncio
import cyclone_app
from rich.console import Console
from rich.text import Text

from core.core_imports import configure_console_log
from core.logging import log
from monitor.operations_monitor import OperationsMonitor
from test_core import TestCore
from data.data_locker import DataLocker
from core.constants import DB_PATH
from utils.startup_service import StartUpService
from scripts.verify_all_tables_exist import verify_all_tables_exist

console = Console()
configure_console_log()


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def show_banner():
    """Display the Sonic Launch banner."""
    try:
        from pyfiglet import Figlet
        art = Figlet(font="slant").renderText("Sonic Launch")
        console.print(Text(art, style="cyan"))
    except Exception:
        console.print(Text("Sonic Launch", style="bold cyan italic"), justify="center")
        console.print()


def launch_sonic_web():
    """Start the Sonic web server and open the browser.

    The previous behaviour blocked the launcher until the web server exited,
    requiring a restart to get back to the menu. The server is now started in
    the background and control returns to the main menu immediately.
    """
    console.print("[bold green]Launching Sonic Web...[/bold green]")
    subprocess.Popen([sys.executable, "sonic_app.py"])
    time.sleep(2)
    log.print_dashboard_link(host="127.0.0.1", port=5000, route="/")
    webbrowser.open("http://127.0.0.1:5000")
    console.print("[cyan]Sonic Web started in background.[/cyan]")
    input("Press ENTER to return...")


def launch_cyclone():
    """Launch the Cyclone interactive console."""
    console.print("[bold blue]Launching Cyclone...[/bold blue]")
    asyncio.run(cyclone_app.main())


def launch_web_and_monitor():
    """Start the Sonic web server and Sonic monitor together."""
    console.print("[bold green]Launching Sonic App and Monitor...[/bold green]")
    subprocess.Popen([sys.executable, "sonic_app.py"])
    subprocess.Popen([sys.executable, os.path.join("monitor", "sonic_monitor.py")])
    time.sleep(2)
    log.print_dashboard_link(host="127.0.0.1", port=5000, route="/")
    webbrowser.open("http://127.0.0.1:5000")
    console.print("[cyan]Sonic Web and Monitor started in background.[/cyan]")
    input("Press ENTER to return...")


def launch_trader_cards():
    """Open the Trader Cards page in the Sonic web UI."""
    console.print("[bold green]Launching Trader Cards...[/bold green]")
    subprocess.Popen([sys.executable, "sonic_app.py"])
    time.sleep(2)
    route = "/trader/cards"
    log.print_dashboard_link(host="127.0.0.1", port=5000, route=route)
    webbrowser.open(f"http://127.0.0.1:5000{route}")
    console.print("[cyan]Sonic Web started in background.[/cyan]")
    input("Press ENTER to return...")


def operations_menu():
    """Operations utilities."""
    while True:
        clear_screen()
        console.print("[bold cyan]Operations[/bold cyan]")
        console.print("1) 🚀 Run POST")
        console.print("2) 🛠️ Core Config Test")
        console.print("3) ♻️ Recover Database")
        console.print("b) 🔙 Back")
        choice = input("→ ").strip().lower()
        if choice == "1":
            monitor = OperationsMonitor()

            result = monitor.run_startup_post()
            log.info("POST Result", payload=result)
            input("Press ENTER to continue...")
        elif choice == "2":
            monitor = OperationsMonitor()

            result = monitor.run_configuration_test()
            log.info("Config Test Result", payload=result)
            input("Press ENTER to continue...")
        elif choice == "3":
            console.print("[yellow]Attempting database recovery...[/yellow]")
            dl = DataLocker(str(DB_PATH))
            dl.db.recover_database()
            dl.initialize_database()
            dl._seed_modifiers_if_empty()
            dl._seed_wallets_if_empty()
            dl._seed_thresholds_if_empty()
            dl.close()
            console.print("[green]Database recovery complete.[/green]")
            input("Press ENTER to continue...")
        elif choice == "b":
            break
        else:
            console.print("Invalid selection.", style="red")
            time.sleep(1)


def database_utils_menu():
    """Database utilities including wallet import."""
    while True:
        clear_screen()
        console.print("[bold cyan]Database Utilities[/bold cyan]")
        console.print("1) 🆕 Initialize Database")
        console.print("2) ♻️ Recover Database")
        console.print("3) 👛 Insert Wallets from JSON")
        console.print("4) ✅ Verify Required Tables")
        console.print("b) 🔙 Back")
        choice = input("→ ").strip().lower()

        if choice == "1":
            from scripts.initialize_database import main as init_db_main

            init_db_main([])
            input("Press ENTER to continue...")
        elif choice == "2":
            console.print("[yellow]Attempting database recovery...[/yellow]")
            dl = DataLocker(str(DB_PATH))
            dl.db.recover_database()
            dl.initialize_database()
            dl._seed_modifiers_if_empty()
            dl._seed_wallets_if_empty()
            dl._seed_thresholds_if_empty()
            dl.close()
            console.print("[green]Database recovery complete.[/green]")
            input("Press ENTER to continue...")
        elif choice == "3":
            path = input(
                "Wallet JSON path (leave blank for default data/wallet_backup.json): "
            ).strip()
            args = ["--json", path] if path else []
            from scripts.insert_wallets import main as insert_wallets_main

            insert_wallets_main(args)
            input("Press ENTER to continue...")
        elif choice == "4":
            code = verify_all_tables_exist()
            msg = "[green]All tables verified.[/green]" if code == 0 else "[red]Missing tables detected.[/red]"
            console.print(msg)
            input("Press ENTER to continue...")
        elif choice == "b":
            break
        else:
            console.print("Invalid selection.", style="red")
            time.sleep(1)


def core_tests_menu():
    """Run unit tests via :class:`TestCore`."""
    tester = TestCore()
    tester.interactive_menu()
    input("Press ENTER to return...")


def check_api_status():
    """Check ChatGPT and Twilio API connectivity."""
    clear_screen()
    console.print("[bold magenta]API Status Check[/bold magenta]")

    # --- ChatGPT ---
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPEN_AI_KEY")
    if not api_key:
        console.print("[yellow]⚠️ OPENAI_API_KEY not configured.[/yellow]")
    else:
        try:
            from openai import OpenAI

            client = OpenAI(api_key=api_key)
            client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "ping"}],
            )
            console.print("[green]✅ ChatGPT API reachable.[/green]")
        except Exception as exc:  # pragma: no cover - network dependent
            console.print(f"[red]❌ ChatGPT check failed: {exc}[/red]")

    # --- Twilio ---
    try:
        from xcom.check_twilio_heartbeat_service import CheckTwilioHeartbeatService

        result = CheckTwilioHeartbeatService({}).check(dry_run=True)
        if result.get("success"):
            console.print("[green]✅ Twilio credentials valid.[/green]")
        else:
            console.print(
                f"[red]❌ Twilio check failed: {result.get('error', 'unknown error')}[/red]"
            )
    except Exception as exc:  # pragma: no cover - network dependent
        console.print(f"[red]❌ Twilio check failed: {exc}[/red]")

    input("Press ENTER to return...")


def main_menu():
    while True:
        clear_screen()
        show_banner()
        console.print("1) 🦔 Sonic App + 🖥️ Sonic Monitor")
        console.print("2) 🌀 Launch Cyclone")
        console.print("3) 🌐 Launch Sonic Web")
        console.print("4) 🌅 Startup Service")
        console.print("5) ⚙️ Operations")
        console.print("6) 🗄️ Database Utilities")
        console.print("7) 🧪 Test Core")
        console.print("8) 🔌 API Status")
        console.print("9) 🃏 Trader Cards")
        console.print("10) 🚪 Exit")
        choice = input("→ ").strip()
        if choice == "1":
            launch_web_and_monitor()
        elif choice == "2":
            launch_cyclone()
        elif choice == "3":
            launch_sonic_web()
        elif choice == "4":
            StartUpService.run_all()
            input("Press ENTER to continue...")
        elif choice == "5":
            operations_menu()
        elif choice == "6":
            database_utils_menu()
        elif choice == "7":
            core_tests_menu()
        elif choice == "8":
            check_api_status()
        elif choice == "9":
            launch_trader_cards()
        elif choice == "10":
            console.print("Goodbye!", style="green")
            break
        else:
            console.print("Invalid selection.", style="red")
            time.sleep(1)


if __name__ == "__main__":
    main_menu()
