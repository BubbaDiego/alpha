import os
import asyncio
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from cyclone.cyclone_engine import Cyclone
from monitor.monitor_core import MonitorCore
from core.core_imports import configure_console_log, DB_PATH
from data.data_locker import DataLocker

console = Console()
configure_console_log(debug=True)
dl = DataLocker(str(DB_PATH))
monitor_core = MonitorCore()
cyclone = Cyclone(monitor_core, debug=True)


def get_counts_banner():
    prices = len(dl.prices.get_all_prices())
    positions = len(dl.positions.get_all_positions())
    alerts = len(dl.alerts.get_all_alerts())
    return f"[bold blue]===[/bold blue]   Prices: {prices}    Positions: {positions}    Alerts: {alerts}   [bold blue]===[/bold blue]"


def show_main_menu():
    os.system("cls" if os.name == "nt" else "clear")
    console.print(Panel("[bold cyan]🌀 Cyclone Interactive Console 🌀[/bold cyan]", border_style="blue"))
    console.print(get_counts_banner())
    console.print("""
[bold]Choose an option:[/bold]

1) 🌀 Full Cyclone Run
2) 📈 Update Prices
3) 📊 Update Positions
4) 💣 Delete All Data (except wallets)
5) 🧪 Cyclone Workbench
6) 🛠 Alert Control Center
7) ❌ Exit
""")


async def step_engine_menu():
    """Interactive runner for Cyclone's step engine.

    The menu reflects the step names expected by :meth:`Cyclone.run_cycle` and
    shows which internal method each step triggers so it stays in sync with the
    engine implementation.
    """

    step_definitions = [
        ("update_operations", cyclone.run_operations_update),
        ("market_updates", cyclone.run_market_updates),
        ("check_jupiter_for_updates", cyclone.run_check_jupiter_for_updates),
        ("enrich_positions", cyclone.run_enrich_positions),
        ("enrich_alerts", cyclone.run_alert_enrichment),
        ("update_evaluated_value", cyclone.run_update_evaluated_value),
        ("create_portfolio_alerts", cyclone.run_create_portfolio_alerts),
        ("create_position_alerts", cyclone.run_create_position_alerts),
        ("create_global_alerts", cyclone.run_create_global_alerts),
        ("evaluate_alerts", cyclone.run_alert_evaluation),
        ("cleanse_ids", cyclone.run_cleanse_ids),
        ("link_hedges", cyclone.run_link_hedges),
        ("update_hedges", cyclone.run_update_hedges),
    ]

    steps = {str(i + 1): name for i, (name, _) in enumerate(step_definitions)}

    while True:
        os.system("cls" if os.name == "nt" else "clear")
        console.print(Panel("[bold magenta]🧪 Cyclone Workbench — Step Engine[/bold magenta]", border_style="magenta"))
        console.print(get_counts_banner())
        console.print("Select one or more steps (comma separated), or [bold red]X[/bold red] to return:\n")
        for i, (name, func) in enumerate(step_definitions, start=1):
            console.print(f"{i}) {name} -> {func.__name__}")

        choice = Prompt.ask("→")
        if choice.strip().lower() in {"x", "exit"}:
            return

        selected = [s.strip() for s in choice.split(",") if s.strip() in steps]
        if not selected:
            console.print("[red]⚠ Invalid step selection[/red]")
            await asyncio.sleep(1.5)
            continue

        selected_steps = [steps[s] for s in selected]
        console.print(f"[cyan]▶ Running steps:[/cyan] {', '.join(selected_steps)}")
        await cyclone.run_cycle(steps=selected_steps)
        input("Press [Enter] to return to the menu...")


async def alert_menu():
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        console.print(Panel("[bold yellow]🛠 Alert Control Center[/bold yellow]", border_style="yellow"))
        console.print(get_counts_banner())
        console.print("""
1) 👁 View Alerts
2) 🛠 Create ALL Alerts
3) 💰 Create Market Alerts
4) 📦 Create Portfolio Alerts
5) 📊 Create Position Alerts
6) 🌐 Create Global Alerts
7) 🧹 Delete All Alerts
8) ✏️ Edit Alert by ID
9) ❌ Delete Alert by ID
10) ⬅ Back
""")

        choice = Prompt.ask("→")

        if choice == "1":
            alerts = dl.alerts.get_all_alerts()
            if not alerts:
                console.print("[yellow]No alerts found.[/yellow]")
                await asyncio.sleep(1.5)
                continue
            table = Table(title="🔔 Alerts", show_lines=True)
            table.add_column("ID", style="cyan")
            table.add_column("Type")
            table.add_column("Asset")
            table.add_column("Trigger", justify="right")
            table.add_column("Eval", justify="right")
            table.add_column("Level")
            for a in alerts:
                table.add_row(
                    a.get("id", "")[:6],
                    a.get("alert_type", ""),
                    a.get("asset", ""),
                    str(a.get("trigger_value", "")),
                    str(a.get("evaluated_value", "")),
                    a.get("level", "")
                )
            console.print(table)
            input("Press [Enter] to return...")

        elif choice == "2":
            await cyclone.run_create_portfolio_alerts()
            await cyclone.run_create_position_alerts()
            await cyclone.run_create_global_alerts()

        elif choice == "3":
            await cyclone.run_create_market_alerts()

        elif choice == "4":
            await cyclone.run_create_portfolio_alerts()

        elif choice == "5":
            await cyclone.run_create_position_alerts()

        elif choice == "6":
            await cyclone.run_create_global_alerts()

        elif choice == "7":
            if Prompt.ask("[red]Are you sure? (yes/no)[/red]") == "yes":
                cyclone.clear_alerts_backend()

        elif choice == "8":
            alert_id = Prompt.ask("🔎 Enter Alert ID to edit (exact)")
            alert = dl.alerts.get_alert(alert_id)
            if not alert:
                console.print("[red]❌ No alert found[/red]")
                await asyncio.sleep(1.5)
                continue

            new_trigger = Prompt.ask(f"✏️ New trigger value (was {alert['trigger_value']})", default=str(alert["trigger_value"]))
            new_level = Prompt.ask(f"✏️ New level (was {alert['level']})", default=str(alert["level"]))

            try:
                alert["trigger_value"] = float(new_trigger)
                alert["level"] = new_level.capitalize()
                dl.alerts.update_alert(alert)
                console.print("[green]✅ Alert updated[/green]")
            except Exception as e:
                console.print(f"[red]❌ Failed to update alert: {e}[/red]")
            input("Press [Enter]...")

        elif choice == "9":
            alert_id = Prompt.ask("❌ Enter Alert ID to delete")
            try:
                dl.alerts.delete_alert(alert_id)
                console.print("[green]✅ Alert deleted[/green]")
            except Exception as e:
                console.print(f"[red]❌ Failed to delete: {e}[/red]")
            input("Press [Enter]...")

        elif choice == "10":
            return


async def handle_main(choice):
    if choice == "1":
        await cyclone.run_cycle()
    elif choice == "2":
        await cyclone.run_market_updates()
    elif choice == "3":
        await cyclone.run_composite_position_pipeline()
    elif choice == "4":
        await cyclone.run_clear_all_data()
    elif choice == "5":
        await step_engine_menu()
    elif choice == "6":
        await alert_menu()
    elif choice == "7":
        console.print("[green]Goodbye![/green]")
        raise SystemExit
    else:
        console.print("[red]Invalid choice[/red]")
        await asyncio.sleep(1)


async def main():
    while True:
        show_main_menu()
        choice = Prompt.ask("→")
        await handle_main(choice)


if __name__ == "__main__":
    asyncio.run(main())
