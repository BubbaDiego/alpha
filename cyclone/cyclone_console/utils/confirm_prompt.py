# cyclone_console/utils/confirm_prompt.py

from rich.prompt import Confirm
from rich.console import Console

console = Console()


def confirm_action(message="Are you sure?"):
    confirmed = Confirm.ask(f"[yellow]{message}[/yellow]")
    if not confirmed:
        console.print("[red]✋ Action cancelled.[/red]")
    return confirmed
