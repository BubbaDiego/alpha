# cyclone_console/commands/system.py

import typer
from rich.console import Console
from cyclone.cyclone_engine import Cyclone
from core.core_imports import configure_console_log, DB_PATH
from data.data_locker import DataLocker

app = typer.Typer(help="🧹 System operations: wipe, reset, maintenance")

console = Console()
configure_console_log()
cyclone = Cyclone()
dl = DataLocker(str(DB_PATH))


@app.command("wipe")
def wipe_all_data(confirm: bool = typer.Option(False, "--confirm", "-y", help="Confirm wipe operation")):
    """🔥 DELETE ALL alerts, prices, and positions (irreversible)"""
    if not confirm:
        console.print("[yellow]⚠ Confirmation required. Use --confirm to proceed.[/yellow]")
        return

    import asyncio
    asyncio.run(cyclone.run_clear_all_data())
    console.print("[bold red]💥 All alerts, prices, and positions have been wiped.[/bold red]")


@app.command("clear-alerts")
def clear_alerts():
    """🚨 Clear all alert definitions"""
    dl.alerts.clear_all_alerts()
    console.print("[green]✅ Alerts cleared[/green]")


@app.command("clear-prices")
def clear_prices():
    """💰 Clear all market price records"""
    dl.prices.clear_prices()
    console.print("[green]✅ Prices cleared[/green]")


@app.command("clear-positions")
def clear_positions():
    """📊 Clear all position records"""
    dl.positions.clear_positions()
    console.print("[green]✅ Positions cleared[/green]")


@app.command("reset-wallets")
def reset_wallets(confirm: bool = typer.Option(False, "--confirm", "-y", help="Confirm wallet deletion")):
    """💼 Delete all stored wallets"""
    if not confirm:
        console.print("[yellow]⚠ Use --confirm to proceed with wallet wipe.[/yellow]")
        return

    dl.wallets.clear_all_wallets()
    console.print("[bold red]💥 Wallets deleted[/bold red]")
