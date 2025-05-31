from __future__ import annotations

import asyncio
from rich.console import Console
from rich.prompt import Prompt

from jupiter_core.engine.jupiter_engine_core import JupiterEngineCore
from jupiter_core import jupiter_perps_steps as steps_module

console = Console()

STEPS = [
    ("Connect Wallet", steps_module.connect_wallet),
    ("Unlock Wallet", steps_module.unlock_wallet),
    ("Select Position Type", steps_module.select_position_type),
]

async def main() -> None:
    engine = JupiterEngineCore(
        extension_path=r"C:\\v0.83\\wallets\\phantom_wallet",
        dapp_url="https://jup.ag/perps-legacy/short/SOL-SOL",
        phantom_password=None,
        headless=False,
    )
    await engine.launch()

    while True:
        console.print("\n[bold magenta]Available Steps:[/bold magenta]")
        for i, (name, _) in enumerate(STEPS, 1):
            console.print(f"{i}) {name}")
        choice = Prompt.ask("Select step number or 'q' to quit")
        if choice.lower() in {"q", "quit", "exit"}:
            break
        if not choice.isdigit() or not (1 <= int(choice) <= len(STEPS)):
            console.print("[red]Invalid selection[/red]")
            continue
        _, step_fn = STEPS[int(choice) - 1]
        await step_fn(engine)

    await engine.close()

if __name__ == "__main__":
    asyncio.run(main())
