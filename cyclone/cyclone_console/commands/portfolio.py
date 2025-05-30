# cyclone_console/commands/portfolio.py

import typer
from rich.console import Console
from rich.table import Table
from cyclone.cyclone_portfolio_service import CyclonePortfolioService
from positions.position_core_service import PositionCoreService
from core.core_imports import configure_console_log, DB_PATH
from data.data_locker import DataLocker

app = typer.Typer(help="📦 Portfolio tools")

console = Console()
configure_console_log()
dl = DataLocker(str(DB_PATH))
portfolio_service = CyclonePortfolioService(dl)
core_service = PositionCoreService(dl)


@app.command("snapshot")
def take_snapshot():
    """📸 Record snapshot of portfolio metrics (totals, leverage, etc)"""
    core_service.record_positions_snapshot()
    console.print("[green]✅ Snapshot recorded[/green]")


@app.command("view")
def view_snapshots():
    """👁 View historical snapshots"""
    snapshots = dl.portfolio.get_snapshots()

    if not snapshots:
        console.print("[red]⚠ No portfolio snapshots found[/red]")
        return

    table = Table(title="📦 Portfolio Snapshot History", show_lines=True)
    table.add_column("Time", style="cyan")
    table.add_column("Size", justify="right")
    table.add_column("Value", justify="right")
    table.add_column("Collateral", justify="right")
    table.add_column("Leverage", justify="right")
    table.add_column("Travel %", justify="right")
    table.add_column("Heat Index", justify="right")

    for snap in snapshots:
        table.add_row(
            snap.get("snapshot_time", "")[:19],
            f"{snap.get('total_size', 0):.2f}",
            f"${snap.get('total_value', 0):,.2f}",
            f"${snap.get('total_collateral', 0):,.2f}",
            f"{snap.get('avg_leverage', 0):.2f}x",
            f"{snap.get('avg_travel_percent', 0):.1f}%",
            f"{snap.get('avg_heat_index', 0):.1f}"
        )

    console.print(table)


@app.command("alerts")
def create_portfolio_alerts():
    """🔔 Auto-generate alerts for portfolio metrics (value, heat, etc)"""
    import asyncio
    asyncio.run(portfolio_service.create_portfolio_alerts())
    console.print("[green]✅ Portfolio alerts created[/green]")
