# cyclone_console/utils/cli_renderer.py

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def banner(text: str, style="bold cyan"):
    console.print(Panel(Text(text, style=style), border_style="blue"))


def print_success(msg: str):
    console.print(f"[green]✅ {msg}[/green]")


def print_warning(msg: str):
    console.print(f"[yellow]⚠ {msg}[/yellow]")


def print_error(msg: str):
    console.print(f"[red]❌ {msg}[/red]")
