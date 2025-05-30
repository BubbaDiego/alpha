# cyclone_console/commands/alerts.py

import typer
from rich.table import Table
from rich.console import Console
from cyclone.cyclone_alert_service import CycloneAlertService
from core.core_imports import configure_console_log, DB_PATH
from data.data_locker import DataLocker

app = typer.Typer(help="🔔 Alert tools: view, enrich, evaluate")

console = Console()
configure_console_log()
dl = DataLocker(str(DB_PATH))
service = CycloneAlertService(dl)


@app.command("view")
def view_alerts():
    """👁 View all alerts"""
    alerts = dl.alerts.get_all_alerts()

    if not alerts:
        console.print("[red]⚠ No alerts found[/red]")
        return

    table = Table(title="🔔 Alerts", show_lines=True)
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Type")
    table.add_column("Asset")
    table.add_column("Trigger", justify="right")
    table.add_column("Eval", justify="right")
    table.add_column("Cond")
    table.add_column("Level", style="magenta")
    table.add_column("Status")

    for a in alerts:
        table.add_row(
            a.get("id", "")[:6],
            a.get("alert_type", ""),
            a.get("asset", ""),
            f"{a.get('trigger_value', 0):.2f}",
            f"{a.get('evaluated_value', 0):.2f}",
            a.get("condition", ""),
            a.get("level", ""),
            a.get("status", "")
        )

    console.print(table)


@app.command("enrich")
def enrich_all():
    """✨ Enrich all alerts with evaluated values"""
    import asyncio
    asyncio.run(service.enrich_all_alerts())
    console.print("[green]✅ Alerts enriched[/green]")


@app.command("evaluate")
def evaluate_all():
    """🧮 Evaluate alert conditions"""
    import asyncio
    asyncio.run(service.update_evaluated_values())
    console.print("[blue]✅ Alerts evaluated[/blue]")


@app.command("refresh")
def refresh_alerts():
    """🔄 Run enrichment + evaluation pipeline"""
    import asyncio
    asyncio.run(service.run_alert_updates())
    console.print("[green]✅ Alert refresh complete[/green]")


@app.command("clean")
def clean_ids():
    """🧹 Remove stale alerts + clear broken references"""
    service.clear_stale_alerts()
    console.print("[yellow]🧽 Alert IDs cleansed[/yellow]")
