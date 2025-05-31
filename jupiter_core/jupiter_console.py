import asyncio
import os
from inspect import signature
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from jupiter_auto_engine import JupiterAutoEngine
from step_registry import build_step_registry

console = Console()

# Dummy config – in practice, replace with env or CLI args
EXTENSION_PATH = r"C:\v0.83\wallets\phantom_wallet"
DAPP_URL = "https://jup.ag/perps-legacy/short/SOL-SOL"
PHANTOM_PASSWORD = os.environ.get("PHANTOM_PASSWORD")

engine = JupiterAutoEngine(
    extension_path=EXTENSION_PATH,
    dapp_url=DAPP_URL,
    phantom_password=PHANTOM_PASSWORD,
    headless=False
)
engine.setup_browser()

step_registry = build_step_registry(engine)
step_definitions = list(step_registry.items())

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

if __name__ == "__main__":
    asyncio.run(step_menu())
