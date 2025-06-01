from rich.prompt import Prompt
from utils.console_logger import ConsoleLogger

async def connect_wallet(engine):
    ConsoleLogger.info("🔗 Connecting Solflare wallet...", source="Steps")
    await engine.pm.connect_wallet(dapp_url=engine.dapp_url, solflare_password=engine.solflare_password)

async def unlock_wallet(engine):
    ConsoleLogger.info("🔓 Unlocking Solflare wallet...", source="Steps")
    if engine.solflare_password:
        await engine.pm.unlock_wallet(engine.solflare_password)
    else:
        ConsoleLogger.warn("⚠️ No password provided for unlocking Solflare", source="Steps")

async def dump_visible_buttons(engine):
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