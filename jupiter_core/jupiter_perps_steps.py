from rich.prompt import Prompt

async def connect_wallet(engine):
    """Connect the Phantom wallet to Jupiter."""
    await engine.pm.connect_wallet(
        dapp_url=engine.dapp_url,
        phantom_password=engine.phantom_password,
    )

async def unlock_wallet(engine):
    """Unlock the Phantom wallet using the stored password."""
    if engine.phantom_password:
        await engine.pm.unlock_phantom(engine.phantom_password)

async def select_position_type(engine):
    """Prompt for Long/Short and select the position type via JupiterPerpsFlow."""
    choice = Prompt.ask("Choose position type", choices=["long", "short"], default="long")
    await engine.jp.select_position_type(choice)


async def set_collateral_asset(engine):
    """Set the collateral asset (token being paid)."""
    asset = Prompt.ask("💰 Choose collateral asset", choices=["SOL", "USDC", "ETH", "WBTC"], default="USDC")
    await engine.jp.select_payment_asset(asset)  # Reusing order asset selection logic here

async def set_position_size(engine):
    """Set the size of the position."""
    size = Prompt.ask("📏 Enter position size (e.g., 0.05)")
    await engine.jp.set_position_size(size)

async def set_leverage(engine):
    """Set the leverage (e.g., 5x, 20x)."""
    leverage = Prompt.ask("⚖️ Enter leverage (e.g., 7.8x, 20x)", default="5x")
    await engine.jp.set_leverage(leverage)

async def select_order_asset(engine):
    asset = Prompt.ask("📦 Choose order asset", choices=["SOL", "ETH", "BTC"], default="SOL")
    await engine.jp.select_payment_asset(asset)


from rich.prompt import Prompt

async def select_order_type(engine):
    """Prompt user to select the order type (market or limit)."""
    order_type = Prompt.ask("📈 Choose order type", choices=["market", "limit"], default="market")
    engine.jp.select_order_type(order_type)

async def place_tp_sl_limit_order(engine):
    """Prompt for TP/SL details and submit a Jupiter trigger order."""
    try:
        from tp_sl_helper import place_tp_sl_order
        import os

        input_mint = Prompt.ask("🪙 Input mint", default="So11111111111111111111111111111111111111112")
        output_mint = Prompt.ask("💵 Output mint", default="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")
        in_amt_str = Prompt.ask("📤 Amount to sell (lamports)", default="50000000")
        out_amt_str = Prompt.ask("🎯 Target output (base units)", default="100000000")

        private_key = os.environ.get("PRIVATE_KEY")
        if not private_key:
            print("❌ Missing PRIVATE_KEY in environment.")
            return

        result = place_tp_sl_order(
            private_key_base58=private_key,
            input_mint=input_mint,
            output_mint=output_mint,
            in_amount=int(in_amt_str),
            out_amount=int(out_amt_str),
        )
        print(result)

    except Exception as e:
        print(f"❌ Error placing TP/SL order: {e}")

async def dump_visible_buttons(engine):
    """Dump all visible <button> labels into button_dump.txt."""
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
        print("✅ Dumped visible buttons to button_dump.txt")
    except Exception as e:
        print(f"❌ Error dumping buttons: {e}")

async def dump_visible_divs(engine):
    """Dump all visible <div> elements with inner text into div_dump.txt."""
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
        print("✅ Dumped visible <div> elements to div_dump.txt")
    except Exception as e:
        print(f"❌ Error dumping <div> content: {e}")