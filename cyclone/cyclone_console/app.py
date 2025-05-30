# cyclone_console/app.py

import typer
from rich import print
from rich.panel import Panel

# CLI app instance
app = typer.Typer(
    name="Cyclone",
    help="🌀 Cyclone CLI — Realtime orchestration for alerts, positions, and portfolios.",
    add_completion=True
)

# Import commands
from cyclone_console.commands import prices, positions, alerts, portfolio, hedge, system

# Register command groups
app.add_typer(prices.app, name="prices", help="💰 Price commands")
app.add_typer(positions.app, name="positions", help="📊 Position lifecycle tools")
app.add_typer(alerts.app, name="alerts", help="🔔 Alert evaluation & creation")
app.add_typer(portfolio.app, name="portfolio", help="📦 Portfolio monitoring")
app.add_typer(hedge.app, name="hedge", help="🛡 Hedge analysis tools")
app.add_typer(system.app, name="system", help="🧹 System cleanup & DB utilities")


@app.command("legacy")
def legacy_console():
    """🧾 Launch old menu-based console"""
    from cyclone_console.old_console_legacy import CycloneConsoleService
    from cyclone_engine import Cyclone
    CycloneConsoleService(Cyclone()).run()


@app.callback()
def main():
    print(Panel.fit("🌀 [bold cyan]Cyclone CLI v2[/bold cyan] — Headless Financial Control System", border_style="blue"))


if __name__ == "__main__":
    app()
