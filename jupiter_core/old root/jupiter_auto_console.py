from __future__ import annotations

import asyncio
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt
from dotenv import load_dotenv
import os

from jupiter_core.engine.jupiter_engine_core import JupiterEngineCore
from jupiter_core import jupiter_perps_steps as steps_module
from utils.console_logger import ConsoleLogger

# Load .env values
load_dotenv()

base_dir = Path(__file__).resolve().parent.parent
load_dotenv(base_dir / ".env")
load_dotenv(base_dir / ".env.example")

console = Console()


WORKFLOWS = TBD

STEPS = [

    # Wallet Support
    ("🔗 Connect Wallet", steps_module.connect_wallet),
    ("🔓 Unlock Wallet", steps_module.unlock_wallet),

    # Extension Support
    ("🔐 Enter Phantom Password", steps_module.enter_phantom_password),

    # Order Creation / Update
    ("📊 Select Position Type", steps_module.select_position_type),
    ("📦 Select Order Asset", steps_module.select_order_asset),
    ("💰 Set Collateral Asset", steps_module.set_collateral_asset),
    ("📏 Set Position Size", steps_module.set_position_size),
    ("⚖️ Set Leverage", steps_module.set_leverage),
    ("📈 Select Order Type", steps_module.select_order_type),
    ("🎯 Place TP/SL Limit Order", steps_module.place_tp_sl_limit_order),

    # Order Confirmation
    ("🧩 Confirm Full Order", steps_module.confirm_full_order),
    ("🍽️ Confirm Order", steps_module.confirm_order),
    ("✅ Confirm in Wallet", steps_module.confirm_wallet_transaction),

    # Utilities
    ("🧹 Dump Visible Buttons", steps_module.dump_visible_buttons),
    ("🪟 Dump Visible Divs", steps_module.dump_visible_divs),
]

async def main() -> None:
    engine = JupiterEngineCore(
        extension_path=r"C:\\v0.83\\wallets\\phantom_wallet",
        dapp_url="https://jup.ag/perps-legacy/short/SOL-SOL",
        phantom_password=os.getenv("PHANTOM_PASSWORD"),
        headless=False,
    )

    ConsoleLogger.debug(
        "🧪 Phantom password set",
        payload={"set": bool(engine.phantom_password)},
        source="Console"
    )

    await engine.launch()

    # Auto-connect wallet for testing
    await engine.pm.connect_wallet(
        dapp_url=engine.dapp_url,
        phantom_password=engine.phantom_password,
    )

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
