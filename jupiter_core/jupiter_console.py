import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "auto_engine")))

import asyncio
from inspect import signature
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from auto_engine.jupiter_auto_engine import JupiterAutoEngine
from auto_engine.step_registry import build_step_registry

console = Console()

# Dummy config – in practice, replace with env or CLI args
EXTENSION_PATH = r"C:\\v0.83\\wallets\\phantom_wallet"
DAPP_URL = "https://jup.ag/perps-legacy/short/SOL-SOL"
PHANTOM_PASSWORD = os.environ.get("PHANTOM_PASSWORD")

engine = None
step_registry = {}
step_definitions = []

async def step_menu():
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        console.print(Panel("[bold magenta]🚀 Jupiter Auto Console[/bold magenta]", border_style="magenta"))

        for i, (name, _) in enumerate(step_definitions, start=1):
            console.print(f"{i}) {name}")

        console.print("\n[X] Exit")
        choice = Prompt.ask("→ Select step(s) to run (e.g. 1,2,3)")

        if choice.strip().lower() in {"x", "exit"}:
            break

        selected = [s.strip() for s in choice.split(",") if s.strip().isdigit() and int(s.strip()) <= len(step_definitions)]

        if not selected:
            console.print("[red]⚠ Invalid selection[/red]")
            await asyncio.sleep(1.5)
            continue

        for idx in selected:
            name, func = step_definitions[int(idx) - 1]
            console.print(f"[cyan]▶ Running: {name}[/cyan]")
            try:
                sig = signature(func)
                kwargs = {}
                for param in sig.parameters.values():
                    user_input = Prompt.ask(f"🔧 {param.name} ({param.annotation.__name__ if param.annotation != param.empty else 'str'})")
                    kwargs[param.name] = user_input

                result = await func(**kwargs) if kwargs else await func()
                if result:
                    console.print(f"[green]✅ {name} completed with payload:[/green] {result}")
            except Exception as e:
                console.print(f"[red]❌ {name} failed:[/red] {e}")
            input("Press Enter to continue...")

async def main_menu():
    global engine, step_registry, step_definitions
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        console.print(Panel("[bold cyan]🌐 Jupiter Automation Main Menu[/bold cyan]", border_style="blue"))
        console.print("""
1) 🧠 Launch Browser
2) 🧪 Step Menu
3) ❌ Exit
""")
        choice = Prompt.ask("→ Select an option")

        if choice == "1":
            engine = JupiterAutoEngine(
                extension_path=EXTENSION_PATH,
                dapp_url=DAPP_URL,
                phantom_password=PHANTOM_PASSWORD,
                headless=False
            )
            await engine.setup_browser()
            step_registry = build_step_registry(engine)
            step_definitions = list(step_registry.items())
            console.print("[green]✅ Browser launched and engine initialized.[/green]")
            input("Press Enter to continue...")

        elif choice == "2":
            if not engine:
                console.print("[red]❌ You must launch the browser first.[/red]")
                input("Press Enter to continue...")
            else:
                await step_menu()

        elif choice == "3":
            console.print("[green]Goodbye![/green]")
            break
        else:
            console.print("[red]Invalid option[/red]")
            await asyncio.sleep(1.5)

if __name__ == "__main__":
    asyncio.run(main_menu())
