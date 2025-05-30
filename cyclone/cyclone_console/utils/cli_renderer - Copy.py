# cyclone_console/commands/system.py

import typer
from rich.console import Console
from cyclone_engine import Cyclone
from core.core_imports import configure_console_log, DB_PATH
from data.data_locker import DataLocker

from cyclone_console.utils.cli_renderer import banner, print_success, print_warning, print_error
from cyclone_console.utils.confirm_prompt import confirm_action

app = typer.Typer(help="🧹 System operations: wipe, reset, maintenance")

console = Console()
configure_console_log()
cyclone = Cyclone()
dl = DataLocker(str(DB_PATH))


@app.command("wipe")
def wipe_all_data():
    """🔥 DELETE ALL alerts, prices, and positions (irreversible)"""
    banner("💀 FULL DATA WIPE")
    if not confirm_action("This will erase alerts, prices, and positions. Proceed?"):
        raise typer.Abort()

    import asyncio
    asyncio.run(cyclone.run_clear_all_data())
    print_success("All alerts, prices, and positions have been wiped.")


@app.command("clear-alerts")
def clear_alerts():
    """🚨 Clear all alert definitions"""
    dl.alerts.clear_all_alerts()
    print_success("All alerts cleared.")


@app.command("clear-prices")
def clear_prices():
    """💰 Clear all market price records"""
    dl.prices.clear_prices()
    print_success("Prices cleared.")


@app.command("clear-positions")
def clear_positions():
    """📊 Clear all position records"""
    dl.positions.clear_positions()
    print_success("Positions cleared.")


@app.command("reset-wallets")
def reset_wallets():
    """💼 Delete all stored wallets"""
    banner("💼 Wallet Reset")
    if not confirm_action("This will delete all wallet records. Continue?"):
        raise typer.Abort()

    dl.wallets.clear_all_wallets()
    print_warning("Wallets deleted.")
