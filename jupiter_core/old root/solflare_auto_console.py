import os
import asyncio
from dotenv import load_dotenv
from rich.console import Console
from jupiter_core.engine.jupiter_engine_core import JupiterEngineCore
from jupiter_core import solflare_perps_steps as steps_module

# Load .env if present
load_dotenv()
console = Console()

STEPS = [
    ("🔗 Connect Wallet", steps_module.connect_wallet),
    ("🔓 Unlock Wallet", steps_module.unlock_wallet),
    ("🧹 Dump Visible Buttons", steps_module.dump_visible_buttons),
    ("🪟 Dump Visible Divs", steps_module.dump_visible_divs),
]

async def main():
    extension_path = os.getenv("SOLFLARE_EXTENSION_PATH", "alpha/jupiter_core/solflare_extension.crx")
    dapp_url = os.getenv("DAPP_URL", "https://jup.ag")
    solflare_password = os.getenv("SOLFLARE_PASSWORD", "1492braxx")

    engine = JupiterEngineCore(
        extension_path=extension_path,
        dapp_url=dapp_url,
        phantom_password=None,
        solflare_password=solflare_password,
        headless=False,
        wallet_type="solflare"
    )
    console.print(f"🌐 Using dApp: {dapp_url}")
    console.print(f"🔌 Using Solflare extension: {extension_path}")
    await engine.launch()

    while True:
        console.print("\n[bold magenta]Available Steps:[/bold magenta]")
        for i, (name, _) in enumerate(STEPS, 1):
            console.print(f"{i}) {name}")
        choice = input("Select step number or 'q' to quit: ").strip()
        if choice.lower() in {"q", "quit"}:
            break
        if not choice.isdigit() or not (1 <= int(choice) <= len(STEPS)):
            console.print("[red]Invalid selection[/red]")
            continue
        _, step_fn = STEPS[int(choice) - 1]
        await step_fn(engine)

    await engine.close()

if __name__ == "__main__":
    asyncio.run(main())