# cyclone_console/commands/positions.py

import typer
from rich.table import Table
from rich.console import Console
from core.core_imports import configure_console_log, DB_PATH
from data.data_locker import DataLocker
from cyclone.cyclone_position_service import CyclonePositionService
from core.logging import log

app = typer.Typer(help="📊 Position lifecycle commands")

console = Console()
configure_console_log()
dl = DataLocker(str(DB_PATH))
service = CyclonePositionService(dl)


@app.command("view")
def view_positions():
    """👁 View current positions from DB"""
    positions = dl.positions.get_all_positions()

    if not positions:
        console.print("[red]⚠ No positions found[/red]")
        return

    table = Table(title="📊 Current Positions", show_lines=True)
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Asset")
    table.add_column("Type")
    table.add_column("Entry", justify="right")
    table.add_column("Current", justify="right")
    table.add_column("Liq. Price", justify="right")
    table.add_column("Size", justify="right")
    table.add_column("PnL", justify="right")
    table.add_column("Wallet")

    for p in positions:
        table.add_row(
            p.get("id", "")[:6],
            p.get("asset_type", ""),
            p.get("position_type", ""),
            f"{p.get('entry_price', 0):.2f}",
            f"{p.get('current_price', 0):.2f}",
            f"{p.get('liquidation_price', 0):.2f}",
            f"{p.get('size', 0):.2f}",
            f"${p.get('pnl_after_fees_usd', 0):.2f}",
            p.get("wallet_name", "")
        )

    console.print(table)


@app.command("enrich")
def enrich_positions():
    """✨ Enrich position data"""
    import asyncio
    asyncio.run(service.enrich_positions())
    console.print("[green]✅ Enrichment complete[/green]")


@app.command("clear")
def clear_positions():
    """🧹 Clear all position data from DB"""
    import asyncio
    asyncio.run(service.clear_positions_backend())
    console.print("[red]⚠ All positions have been cleared[/red]")


@app.command("snapshot")
def snapshot_positions():
    """📸 Save a snapshot of portfolio totals"""
    from positions.position_core_service import PositionCoreService
    core = PositionCoreService(dl)
    core.record_positions_snapshot()
    console.print("[blue]📸 Snapshot recorded[/blue]")
