from rich.prompt import Prompt
from utils.console_logger import ConsoleLogger
import os
from tp_sl_helper import place_tp_sl_order

def is_phantom(engine): return hasattr(engine.pm, "unlock_phantom")
def is_solflare(engine): return hasattr(engine.pm, "unlock_wallet")

# ------------------ Wallet & Utility Actions ------------------
async def connect_wallet(engine):
    ConsoleLogger.info("🔗 Connecting wallet...", source="Steps")
    await engine.pm.connect_wallet(engine.dapp_url)

async def unlock_wallet(engine):
    ConsoleLogger.info("🔓 Unlocking wallet...", source="Steps")
    try:
        if is_phantom(engine) and engine.phantom_password:
            await engine.pm.unlock_phantom(engine.phantom_password)
        elif is_solflare(engine) and engine.solflare_password:
            await engine.pm.unlock_wallet(engine.solflare_password)
        else:
            ConsoleLogger.warn("⚠️ No password or unsupported wallet type", source="Steps")
    except Exception as e:
        if "Timeout" in str(e) and "unlock-form-password-input" in str(e):
            ConsoleLogger.info("🔓 Wallet already unlocked — skipping", source="Steps")
        else:
            raise

async def dump_visible_buttons(engine):
    try:
        page = engine.pm.page
        buttons = page.locator("button")
        count = await buttons.count()
        with open("button_dump.txt", "w", encoding="utf-8") as f:
            for i in range(count):
                btn = buttons.nth(i)
                if await btn.is_visible():
                    label = await btn.inner_text()
                    if label.strip():
                        f.write(f"[{i}] {label.strip()}\n")
        ConsoleLogger.success("✅ Dumped visible buttons", source="Steps")
    except Exception as e:
        ConsoleLogger.error("❌ Error dumping buttons", payload={"error": str(e)}, source="Steps")

async def dump_visible_divs(engine):
    try:
        page = engine.pm.page
        divs = page.locator("div")
        count = await divs.count()
        with open("div_dump.txt", "w", encoding="utf-8") as f:
            for i in range(count):
                div = divs.nth(i)
                if await div.is_visible():
                    text = await div.inner_text()
                    if text.strip():
                        f.write(f"[{i}] {text.strip()}\n")
        ConsoleLogger.success("✅ Dumped visible divs", source="Steps")
    except Exception as e:
        ConsoleLogger.error("❌ Error dumping divs", payload={"error": str(e)}, source="Steps")

# ------------------ Trading Flow ------------------
async def select_order_asset(engine):
    if not engine.jp:
        ConsoleLogger.warn("⚠️ Trading flow not initialized", source="Steps")
        return
    asset = Prompt.ask("📦 Choose order asset", choices=["SOL", "ETH", "WBTC"], default="SOL")
    try:
        await engine.pm.page.locator(f"button:visible:has-text('{asset}')").first.click(timeout=10000)
        engine.jp.order_definition["asset"] = asset.upper()
        ConsoleLogger.success(f"✅ Order asset set: {asset}", source="Steps")
    except Exception as e:
        ConsoleLogger.error("❌ Failed to set order asset", payload={"error": str(e)}, source="Steps")

async def select_position_type(engine):
    if not engine.jp:
        ConsoleLogger.warn("⚠️ Trading flow not initialized", source="Steps")
        return
    choice = Prompt.ask("📊 Choose position type", choices=["long", "short"], default="long")
    await engine.jp.select_position_type(choice)
    ConsoleLogger.success(f"✅ Position type set: {choice}", source="Steps")

async def select_order_type(engine):
    if not engine.jp:
        ConsoleLogger.warn("⚠️ Trading flow not initialized", source="Steps")
        return
    order_type = Prompt.ask("📈 Choose order type", choices=["market", "limit"], default="market")
    await engine.jp.select_order_type(order_type)
    ConsoleLogger.success(f"✅ Order type set: {order_type}", source="Steps")

async def set_collateral_asset(engine):
    ConsoleLogger.info("💰 Setting collateral asset (default SOL fallback)", source="Steps")
    engine.jp.order_definition["collateral_asset"] = "SOL"
    ConsoleLogger.success("✅ Collateral asset set: SOL", source="Steps")

async def set_position_size(engine):
    ConsoleLogger.info("📏 Entering position size", source="Steps")
    size = Prompt.ask("Enter position size (e.g. 0.05)")
    await engine.jp.set_position_size(size)
    ConsoleLogger.success(f"✅ Position size set: {size}", source="Steps")

async def set_leverage(engine):
    ConsoleLogger.info("⚖️ Setting leverage", source="Steps")
    leverage = Prompt.ask("Enter leverage (e.g. 7.5x)", default="5x")
    await engine.jp.set_leverage(leverage)
    ConsoleLogger.success(f"✅ Leverage set: {leverage}", source="Steps")

async def place_tp_sl_limit_order(engine):
    ConsoleLogger.info("🎯 Placing TP/SL limit order", source="Steps")
    input_mint = Prompt.ask("🪙 Input mint", default="So11111111111111111111111111111111111111112")
    output_mint = Prompt.ask("💵 Output mint", default="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")
    in_amt_str = Prompt.ask("📤 Amount to sell (lamports)", default="50000000")
    out_amt_str = Prompt.ask("🎯 Target output (base units)", default="100000000")
    private_key = os.environ.get("PRIVATE_KEY")
    if not private_key:
        ConsoleLogger.error("❌ Missing PRIVATE_KEY in environment", source="Steps")
        return
    result = place_tp_sl_order(
        private_key_base58=private_key,
        input_mint=input_mint,
        output_mint=output_mint,
        in_amount=int(in_amt_str),
        out_amount=int(out_amt_str),
    )
    ConsoleLogger.success("✅ TP/SL order placed", payload={"tx": result}, source="Steps")

async def confirm_order(engine):
    ConsoleLogger.info("🍽️ Confirming order", source="Steps")
    page = engine.pm.page
    asset = engine.jp.order_definition.get("asset", "SOL")
    position = engine.jp.order_definition.get("position_type", "Long").capitalize()
    btn = page.locator(f"button:has-text('{position} {asset}')")
    await btn.first.wait_for(state="visible", timeout=7000)
    await btn.first.click(timeout=5000)
    ConsoleLogger.success("✅ Order confirm clicked", source="Steps")

async def confirm_wallet_transaction(engine):
    ConsoleLogger.info("✅ Confirming wallet transaction", source="Steps")
    popup = engine.pm.popup or await engine.pm.open_phantom_popup()
    btn = popup.locator("div[role='dialog'] button:has-text('Confirm')")
    await btn.first.wait_for(state="visible", timeout=5000)
    await btn.first.click(timeout=3000)
    ConsoleLogger.success("✅ Confirmed in wallet popup", source="Steps")

async def confirm_full_order(engine):
    ConsoleLogger.info("🧩 Starting full confirm flow", source="Steps")
    await confirm_order(engine)
    await engine.pm.page.wait_for_timeout(1500)
    await confirm_wallet_transaction(engine)
    ConsoleLogger.success("✅ Full confirm flow done", source="Steps")

# ------------------ Step Constant for CLI ------------------
STEPS = [
    # 🛠 Wallet Support
    ("🔗 Connect Wallet", connect_wallet),
    ("🔓 Unlock Wallet", unlock_wallet),

    # 🧩 Extension Support
    ("🔐 Enter Phantom Password", unlock_wallet),

    # 🧾 Order Creation / Update
    ("📊 Select Position Type", select_position_type),
    ("📦 Select Order Asset", select_order_asset),
    ("💰 Set Collateral Asset", set_collateral_asset),
    ("📏 Set Position Size", set_position_size),
    ("⚖️ Set Leverage", set_leverage),
    ("📈 Select Order Type", select_order_type),
    ("🎯 Place TP/SL Limit Order", place_tp_sl_limit_order),

    # ✅ Order Confirmation
    ("🧩 Confirm Full Order", confirm_full_order),
    ("🍽️ Confirm Order", confirm_order),
    ("✅ Confirm in Wallet", confirm_wallet_transaction),

    # 🧰 Utilities
    ("🧹 Dump Visible Buttons", dump_visible_buttons),
    ("🪟 Dump Visible Divs", dump_visible_divs),
]

if __name__ == "__main__":
    import asyncio
    from jupiter_core.jupiter_engine_core import JupiterEngineCore
    from dotenv import load_dotenv

    load_dotenv()
    extension_path = os.getenv("PHANTOM_EXTENSION_PATH")
    dapp_url = os.getenv("JUPITER_DAPP_URL")
    phantom_password = os.getenv("PHANTOM_PASSWORD")

    async def _main():
        from rich.console import Console
        from rich.prompt import Prompt
        console = Console()

        engine = JupiterEngineCore(
            extension_path=extension_path,
            dapp_url=dapp_url,
            phantom_password=phantom_password,
            wallet_type="phantom",
        )

        await engine.launch()
        await engine.pm.page.goto(engine.dapp_url)

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

    asyncio.run(_main())
