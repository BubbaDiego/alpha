# cyclone_console/commands/prices.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import typer
from rich.table import Table
from rich.console import Console
from core.core_imports import configure_console_log, DB_PATH
from data.data_locker import DataLocker
from monitor.price_monitor import PriceMonitor

app = typer.Typer(help="💰 Market price operations")

console = Console()
configure_console_log()
dl = DataLocker(str(DB_PATH))


@app.command("update")
def update_prices():
    """🔄 Fetch latest prices and store in DB"""
    monitor = PriceMonitor()
    result = monitor._do_work()
    count = result.get("loop_counter", 0)
    console.print(f"[bold green]✅ Updated {count} prices[/bold green]")


@app.command("view")
def view_prices():
    """👁 View recent stored prices"""
    prices = dl.prices.get_all_prices()

    if not prices:
        console.print("[red]⚠ No price records found[/red]")
        return

    table = Table(title="📈 Latest Market Prices", show_lines=True)
    table.add_column("Asset", style="cyan", no_wrap=True)
    table.add_column("Current", justify="right")
    table.add_column("Previous", justify="right")
    table.add_column("Updated", justify="center")
    table.add_column("Source", style="dim")

    for p in prices:
        table.add_row(
            p.get("asset_type", "?"),
            f"${p.get('current_price', 0):,.2f}",
            f"${p.get('previous_price', 0):,.2f}",
            p.get("last_update_time", "N/A"),
            p.get("source", "unknown")
        )

    console.print(table)
