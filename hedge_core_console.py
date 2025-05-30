import os
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from core.core_imports import configure_console_log, DB_PATH
from data.data_locker import DataLocker
from hedge_core.hedge_core import HedgeCore

console = Console()
configure_console_log()

# Initialize HedgeCore
locker = DataLocker(str(DB_PATH))
core = HedgeCore(locker)


def _display_hedges(hedges):
    """Render hedge summary table."""
    if not hedges:
        console.print("[yellow]No hedges found[/yellow]")
        return
    table = Table(title="Hedges", show_lines=True)
    table.add_column("ID", style="cyan")
    table.add_column("Positions", justify="right")
    table.add_column("Long Size", justify="right")
    table.add_column("Short Size", justify="right")
    table.add_column("Heat", justify="right")
    for h in hedges:
        table.add_row(
            h.id[:6],
            str(len(h.positions)),
            f"{h.total_long_size:.2f}",
            f"{h.total_short_size:.2f}",
            f"{h.total_heat_index:.2f}",
        )
    console.print(table)


def main_menu():
    while True:
        console.clear()
        console.print(Panel("[bold green]HedgeCore Test Console[/bold green]", border_style="green"))
        console.print("""
1) Update Hedges
2) Link Hedges
3) Unlink Hedges
4) Build Hedges
5) Show DB Hedges
6) Show Modifiers
7) Exit
""")
        choice = console.input("Choose > ").strip()

        if choice == "1":
            hedges = core.update_hedges()
            _display_hedges(hedges)
        elif choice == "2":
            groups = core.link_hedges()
            console.print(f"[green]Linked {len(groups)} group(s)[/green]")
        elif choice == "3":
            core.unlink_hedges()
            console.print("[yellow]Hedges unlinked[/yellow]")
        elif choice == "4":
            hedges = core.build_hedges()
            _display_hedges(hedges)
        elif choice == "5":
            hedges = core.get_db_hedges()
            _display_hedges(hedges)
        elif choice == "6":
            mods = core.get_modifiers()
            console.print(mods)
        elif choice == "7":
            break
        else:
            console.print("[red]Invalid choice[/red]")
        console.input("\nPress Enter to continue...")


if __name__ == "__main__":
    main_menu()
