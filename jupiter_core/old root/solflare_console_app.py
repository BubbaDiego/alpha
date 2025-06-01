from __future__ import annotations
import asyncio
from rich.console import Console
from rich.prompt import Prompt
from solflare_manager import SolflareManager

console = Console()

async def main():
    extension_path = Prompt.ask("🔌 Enter Solflare extension path", default="alpha/jupiter_core/solflare_extension.crx")
    dapp_url = Prompt.ask("🌐 Enter dApp URL", default="https://jup.ag")
    password = Prompt.ask("🔐 Solflare Password", password=True)

    manager = SolflareManager(extension_path=extension_path, headless=False)

    await manager.launch_browser()
    await manager.connect_wallet(dapp_url)
    await manager.unlock_wallet(password)

    while True:
        console.print("\n[bold magenta]Available Actions:[/bold magenta]")
        console.print("1) ✅ Approve Transaction Popup")
        console.print("2) ❌ Close Browser")
        console.print("3) 🧹 Dump Visible Buttons")
        console.print("4) 🪟 Dump Visible Divs")
        choice = Prompt.ask("Choose action or 'q' to quit")
        if choice.lower() in {"q", "quit"}:
            break
        elif choice == "1":
            await manager.approve_transaction()
        elif choice == "2":
            await manager.close()
        elif choice == "3":
            await dump_visible_buttons(manager)
        elif choice == "4":
            await dump_visible_divs(manager)

            break

    await manager.close()

if __name__ == "__main__":
    asyncio.run(main())

async def dump_visible_buttons(engine):
    """Dump all visible <button> labels into button_dump.txt."""
    ConsoleLogger.info("↪ Entering dump_visible_buttons", source="Steps")
    try:
        page = engine.pm.page
        buttons = page.locator("button")
        count = await buttons.count()
        with open("button_dump.txt", "w", encoding="utf-8") as f:
            for i in range(count):
                try:
                    btn = buttons.nth(i)
                    if await btn.is_visible():
                        label = await btn.inner_text()
                        if label.strip():
                            f.write(f"[{i}] {label.strip()}\n")
                except Exception:
                    continue
        ConsoleLogger.success("✅ Dumped visible buttons to button_dump.txt", source="Steps")
    except Exception as e:
        ConsoleLogger.error("❌ Error dumping buttons", payload={"error": str(e)}, source="Steps")

async def dump_visible_divs(engine):
    """Dump all visible <div> elements with inner text into div_dump.txt."""
    ConsoleLogger.info("↪ Entering dump_visible_divs", source="Steps")
    try:
        page = engine.pm.page
        divs = page.locator("div")
        count = await divs.count()
        with open("div_dump.txt", "w", encoding="utf-8") as f:
            for i in range(count):
                try:
                    div = divs.nth(i)
                    if await div.is_visible():
                        text = await div.inner_text()
                        if text.strip():
                            f.write(f"[{i}] {text.strip()}\n")
                except Exception:
                    continue
        ConsoleLogger.success("✅ Dumped visible divs to div_dump.txt", source="Steps")
    except Exception as e:
        ConsoleLogger.error("❌ Error dumping divs", payload={"error": str(e)}, source="Steps")