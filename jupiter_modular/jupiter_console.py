from __future__ import annotations

import asyncio
import importlib.util
from pathlib import Path
from typing import List

from rich.console import Console
from rich.prompt import Prompt

from .engine.jupiter_engine_core import JupiterEngineCore

console = Console()

STEPS_PATH = Path(__file__).parent / "steps"
EXTENSION_PATH = r"C:\\v0.83\\wallets\\phantom_wallet"
DAPP_URL = "https://jup.ag/perps-legacy/short/SOL-SOL"
PHANTOM_PASSWORD = None


def load_steps() -> List[tuple[str, object]]:
    steps = []
    for file in sorted(STEPS_PATH.glob("auto_*.py")):
        name = file.stem
        spec = importlib.util.spec_from_file_location(name, file)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader
        spec.loader.exec_module(module)
        steps.append((name, module))
    return steps


async def main() -> None:
    engine = JupiterEngineCore(
        extension_path=EXTENSION_PATH,
        dapp_url=DAPP_URL,
        phantom_password=PHANTOM_PASSWORD,
        headless=False,
    )
    await engine.launch()

    steps = load_steps()
    while True:
        console.print("\n[bold magenta]Available Steps:[/bold magenta]")
        for i, (name, _) in enumerate(steps, 1):
            console.print(f"{i}) {name}")
        choice = Prompt.ask("Select step number or 'q' to quit")
        if choice.lower() in {"q", "quit", "exit"}:
            break
        if not choice.isdigit() or not (1 <= int(choice) <= len(steps)):
            console.print("[red]Invalid selection[/red]")
            continue
        _, module = steps[int(choice) - 1]
        await module.run(engine)

    await engine.close()


if __name__ == "__main__":
    asyncio.run(main())
