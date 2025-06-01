from rich.prompt import Prompt
from utils.console_logger import ConsoleLogger

async def connect_wallet(engine):
    """Connect the Phantom wallet to Jupiter."""
    ConsoleLogger.info("↪ Entering connect_wallet", source="Steps")
    await engine.pm.connect_wallet(
        dapp_url=engine.dapp_url,
        phantom_password=engine.phantom_password,
    )

async def unlock_wallet(engine):
    """Unlock the Phantom wallet using the stored password."""
    ConsoleLogger.info("↪ Entering unlock_wallet", source="Steps")
    if engine.phantom_password:
        await engine.pm.unlock_phantom(engine.phantom_password)

async def select_position_type(engine):
    """Prompt for Long/Short and select the position type via JupiterPerpsFlow."""
    ConsoleLogger.info("↪ Entering select_position_type", source="Steps")
    choice = Prompt.ask("📊 Choose position type", choices=["long", "short"], default="long")
    await engine.jp.select_position_type(choice)
    ConsoleLogger.success(f"✅ Position type set: {choice}", source="Steps")

async def select_order_asset(engine):
    """Select the order asset using top-left button (SOL, ETH, WBTC)."""
    ConsoleLogger.info("↪ Entering select_order_asset", source="Steps")
    asset = Prompt.ask("📦 Choose order asset", choices=["SOL", "ETH", "WBTC"], default="SOL")
    try:
        await engine.pm.page.locator(f"button:visible:has-text('{asset}')").first.click(timeout=10000)
        engine.jp.order_definition["asset"] = asset.upper()
        ConsoleLogger.success(f"✅ Order asset set: {asset}", source="Steps")
    except Exception as e:
        ConsoleLogger.error("❌ Failed to set order asset", payload={"error": str(e)}, source="Steps")

async def set_collateral_asset(engine):
    """Fallback to SOL collateral until modal selector is fully integrated."""
    ConsoleLogger.info("↪ Entering set_collateral_asset", source="Steps")
    try:
        # NOTE [SPEC]: Collateral asset selection via dropdown is currently unstable.
        # This fallback assumes SOL and logs it for now.
        asset = "SOL"
        engine.jp.order_definition["collateral_asset"] = asset
        ConsoleLogger.success(f"⚠️ Defaulted collateral asset to {asset}", source="Steps")
    except Exception as e:
        ConsoleLogger.error("❌ Failed to set collateral asset (fallback path)", payload={"error": str(e)}, source="Steps")

async def set_position_size(engine):
    """Set the size of the position."""
    ConsoleLogger.info("↪ Entering set_position_size", source="Steps")
    size = Prompt.ask("📏 Enter position size (e.g., 0.05)")
    await engine.jp.set_position_size(size)
    ConsoleLogger.success(f"✅ Position size set: {size}", source="Steps")

async def set_leverage(engine):
    """Set the leverage (e.g., 5x, 20x) using calibrated + button clicks."""
    ConsoleLogger.info("↪ Entering set_leverage", source="Steps")
    leverage = Prompt.ask("⚖️ Enter leverage (e.g., 7.8x, 20x)", default="5x")
    await engine.jp.set_leverage(leverage)
    ConsoleLogger.success(f"✅ Leverage input: {leverage}", source="Steps")

async def select_order_type(engine):
    """Prompt user to select the order type (market or limit)."""
    ConsoleLogger.info("↪ Entering select_order_type", source="Steps")
    order_type = Prompt.ask("📈 Choose order type", choices=["market", "limit"], default="market")
    engine.jp.select_order_type(order_type)
    ConsoleLogger.success(f"✅ Order type set: {order_type}", source="Steps")

async def place_tp_sl_limit_order(engine):
    """Prompt for TP/SL details and submit a Jupiter trigger order."""
    ConsoleLogger.info("↪ Entering place_tp_sl_limit_order", source="Steps")
    try:
        from tp_sl_helper import place_tp_sl_order
        import os

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

    except Exception as e:
        ConsoleLogger.error("❌ Error placing TP/SL order", payload={"error": str(e)}, source="Steps")

async def confirm_order(engine):
    from utils.console_logger import ConsoleLogger
    ConsoleLogger.info("🍽️ Entering confirm_order — chef’s kiss", source="Steps")

    try:
        page = engine.pm.page
        asset = engine.jp.order_definition.get("asset", "SOL")
        position = engine.jp.order_definition.get("position_type", "Long").capitalize()

        # Step 1: Locate and click "Long SOL", "Short ETH", etc.
        ConsoleLogger.info(f"🔍 Looking for confirmation button ({position} {asset})", source="Steps")
        confirm_button = page.locator(f"button:has-text('{position} {asset}')")

        await confirm_button.first.wait_for(state="visible", timeout=7000)
        await confirm_button.first.click(timeout=5000)
        ConsoleLogger.success("✅ Order confirmation button clicked", source="Steps")

        # Step 2: Wait a bit to see if modal appears
        await page.wait_for_timeout(1500)
        ConsoleLogger.info("⏳ Waiting to see if a confirm modal appears", source="Steps")

        modals = page.locator("[role='dialog'], div[aria-modal='true']")
        count = await modals.count()
        ConsoleLogger.debug("🔎 Modal count after click", payload={"count": count}, source="Steps")

        # Step 3: If a modal appears, try to confirm again
        if count > 0:
            ConsoleLogger.info("🖱️ Attempting to click confirm inside modal", source="Steps")
            try:
                modal_confirm = modals.locator("button", has_text="Confirm")
                await modal_confirm.first.wait_for(state="visible", timeout=5000)
                await modal_confirm.first.click(timeout=3000)
                ConsoleLogger.success("✅ Modal confirm button clicked", source="Steps")
            except Exception as e:
                ConsoleLogger.warning("⚠️ Modal confirm button not found or failed", payload={"error": str(e)}, source="Steps")

        # Final log of order state
        ConsoleLogger.debug("📦 Final order state", payload=engine.jp.order_definition, source="Steps")

    except Exception as e:
        ConsoleLogger.error("❌ Failed to confirm order", payload={"error": str(e)}, source="Steps")


async def enter_phantom_password(engine):
    from utils.console_logger import ConsoleLogger
    ConsoleLogger.info("🔓 Entering Phantom unlock via standalone step", source="Steps")

    try:
        if engine.phantom_password:
            await engine.pm.unlock_phantom(engine.phantom_password)
            ConsoleLogger.success("✅ Phantom unlocked (manual trigger)", source="Steps")
        else:
            ConsoleLogger.warning("⚠️ No phantom_password set on engine", source="Steps")

    except Exception as e:
        ConsoleLogger.error("❌ Failed to unlock Phantom", payload={"error": str(e)}, source="Steps")

async def confirm_wallet_transaction(engine):
    from utils.console_logger import ConsoleLogger
    ConsoleLogger.info("🪙 Entering wallet transaction confirm step", source="Steps")

    try:
        popup = engine.pm.popup or await engine.pm.open_phantom_popup()

        # Step 0: If locked overlay appears, click to continue
        if await popup.locator("text='Click this dialog to continue.'").is_visible(timeout=2000):
            ConsoleLogger.info("🔓 Dismissing Phantom dialog overlay", source="Steps")
            await popup.mouse.click(400, 300)  # or use .click("body") if safer

        # Step 1: Try native popup confirm
        confirm_btn = popup.locator("div[role='dialog'] button:has-text('Confirm')")
        try:
            await confirm_btn.wait_for(state="visible", timeout=5000)
            await confirm_btn.click(timeout=3000)
            ConsoleLogger.success("✅ Confirmed via Phantom popup", source="Steps")
            return
        except Exception:
            ConsoleLogger.warning("⚠️ Phantom popup confirm not found, trying Jupiter modal", source="Steps")

        # Step 2: Fallback to Jupiter in-app modal
        page = engine.pm.page
        jup_btn = page.locator("div[data-testid='approve-transaction'] button:has-text('Confirm')")
        await jup_btn.wait_for(state="visible", timeout=5000)
        await jup_btn.click(timeout=3000)
        ConsoleLogger.success("✅ Confirmed via Jupiter in-page modal", source="Steps")

    except Exception as e:
        ConsoleLogger.error("❌ Failed to confirm transaction", payload={"error": str(e)}, source="Steps")

async def confirm_full_order(engine):
    from utils.console_logger import ConsoleLogger
    ConsoleLogger.info("🚀 Starting full order confirmation flow", source="Steps")

    try:
        page = engine.pm.page

        # Step 1: Re-unlock if password exists
        if engine.phantom_password:
            ConsoleLogger.info("🔐 Re-unlocking Phantom before confirm", source="Steps")
            await engine.pm.unlock_phantom(engine.phantom_password)

        # Step 2: Click the main Jupiter confirm button (Short WBTC / Long ETH etc.)
        asset = engine.jp.order_definition.get("asset", "SOL")
        position = engine.jp.order_definition.get("position_type", "Long").capitalize()
        confirm_button = page.locator(f"button:has-text('{position} {asset}')")

        ConsoleLogger.info(f"🔍 Clicking confirm button: {position} {asset}", source="Steps")
        await confirm_button.first.wait_for(state="visible", timeout=7000)
        await confirm_button.first.click(timeout=5000)

        # Step 3: Wait briefly to allow Phantom to render
        await page.wait_for_timeout(1500)

        # Step 4: Handle Phantom confirm
        popup = engine.pm.popup or await engine.pm.open_phantom_popup()

        # 4A: If the "Click to continue" overlay appears, dismiss it
        if await popup.locator("text='Click this dialog to continue.'").is_visible(timeout=2000):
            ConsoleLogger.info("🔓 Clicking unlock dialog overlay", source="Steps")
            await popup.mouse.click(400, 300)

        # 4B: Try Confirm in popup
        try:
            btn = popup.locator("div[role='dialog'] button:has-text('Confirm')")
            await btn.wait_for(state="visible", timeout=5000)
            await btn.click(timeout=3000)
            ConsoleLogger.success("✅ Confirmed via Phantom popup", source="Steps")
        except Exception:
            # Step 5: Fallback to in-page confirm if popup fails
            ConsoleLogger.warning("⚠️ Phantom confirm failed — trying in-app modal", source="Steps")
            inapp_btn = page.locator("div[data-testid='approve-transaction'] button:has-text('Confirm')")
            await inapp_btn.wait_for(state="visible", timeout=5000)
            await inapp_btn.click(timeout=3000)
            ConsoleLogger.success("✅ Confirmed via Jupiter modal", source="Steps")

        # Final order state log
        ConsoleLogger.debug("📦 Final order definition", payload=engine.jp.order_definition, source="Steps")

    except Exception as e:
        ConsoleLogger.error("❌ Full confirm failed", payload={"error": str(e)}, source="Steps")


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
