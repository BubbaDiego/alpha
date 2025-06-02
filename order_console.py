# order_console.py

import asyncio
import os
from rich.console import Console
from rich.prompt import Prompt
from dotenv import load_dotenv

from order_core.order_core import OrderCore

console = Console()

async def run_console():
    load_dotenv()

    console.print("[bold cyan]Select Wallet Extension:[/bold cyan]")
    console.print("1) 🪐 Solflare")
    console.print("2) 👻 Phantom")

    wallet_choice = Prompt.ask("Enter number", choices=["1", "2"], default="2")
    wallet_type = "solflare" if wallet_choice == "1" else "phantom"

    extension_path = os.getenv("SOLFLARE_EXTENSION_PATH") if wallet_type == "solflare" else os.getenv("PHANTOM_EXTENSION_PATH")
    phantom_password = os.getenv("PHANTOM_PASSWORD")
    solflare_password = os.getenv("SOLFLARE_PASSWORD")
    dapp_url = os.getenv("JUPITER_DAPP_URL")

    core = OrderCore(
        data_locker=None,
        config_loader=lambda: {},
        wallet_type=wallet_type
    )

    await core.launch(
        extension_path=extension_path,
        headless=False,
        phantom_password=None,
        solflare_password=None
    )

    while True:
        console.print("\n[bold cyan]Order Console Options:[/bold cyan]")
        options = [
            "🔐 Unlock Wallet",
            "🌐 Navigate to DApp (open Jupiter page)",
            "🖱️ Click 'Connect' Button in DApp",
            "🪪 Confirm Wallet Connect Modal",
            "📦 Select Asset",
            "📊 Select Position Type",
            "⚖️ Set Leverage",
            "💰 Set Collateral Asset",
            "📏 Set Position Size",
            "📈 Select Order Type",
            "🍽️ Confirm UI Order Button",
            "✅ Confirm Wallet Transaction",
            "🎯 Place TP/SL Trigger Order",
            "🏁 Run Full Order Flow",
            "🛠 Open DOM Utilities Submenu",
            "❌ Quit",
        ]
        for i, opt in enumerate(options, 1):
            console.print(f"{i}) {opt}")

        choice = Prompt.ask("Select option", default="1")

        if choice == "16":
            break

        try:
            if choice == "1":
                password = phantom_password if wallet_type == "phantom" else solflare_password
                await core.agent.unlock(password)
            elif choice == "2":
                await core.agent.page.goto(dapp_url)
            elif choice == "3":
                await core.agent.click_connect_button()
            elif choice == "4":
                await core.agent.confirm_connect_modal(auto_connect=True, auto_approve=True)
            elif choice == "5":
                asset = Prompt.ask("Enter asset (SOL, ETH, WBTC)", default="SOL")
                await core.engine.select_asset(asset)
            elif choice == "6":
                kind = Prompt.ask("Enter position type (long, short)", default="long")
                await core.engine.select_position_type(kind)
            elif choice == "7":
                leverage = Prompt.ask("Enter leverage (e.g. 5x)", default="5x")
                await core.engine.set_leverage(leverage)
            elif choice == "8":
                collateral = Prompt.ask("Enter collateral asset", default="SOL")
                await core.engine.select_collateral_asset(collateral)
            elif choice == "9":
                size = Prompt.ask("Enter position size (e.g. 0.1)")
                await core.engine.set_position_size(size)
            elif choice == "10":
                order_type = Prompt.ask("Enter order type (market, limit)", default="market")
                await core.engine.select_order_type(order_type)
            elif choice == "11":
                await core.engine.confirm_order()
            elif choice == "12":
                await core.engine.confirm_wallet_transaction()
            elif choice == "13":
                await core.run_tp_sl_flow(
                    input_mint=Prompt.ask("Input mint", default="So11111111111111111111111111111111111111112"),
                    output_mint=Prompt.ask("Output mint", default="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"),
                    in_amount=int(Prompt.ask("Sell amount (lamports)", default="50000000")),
                    out_amount=int(Prompt.ask("Receive target (base units)", default="100000000")),
                    private_key=os.getenv("PRIVATE_KEY")
                )
            elif choice == "14":
                await core.run_order_flow(
                    asset="SOL",
                    kind="long",
                    size="0.1",
                    leverage="5x",
                    order_type="market",
                    collateral_asset="SOL"
                )
            elif choice == "15":
                while True:
                    console.print("\n[bold yellow]🛠 DOM Utilities:[/bold yellow]")
                    submenu = [
                        "📋 Dump All Button InnerText",
                        "🪟 Dump All Div InnerText",
                        "🧾 Dump All Elements with aria-label",
                        "🔙 Return to Main Menu"
                    ]
                    for i, opt in enumerate(submenu, 1):
                        console.print(f"{i}) {opt}")
                    sub = Prompt.ask("Select utility", default="4")
                    if sub == "1":
                        try:
                            buttons = core.agent.page.locator("button")
                            count = await buttons.count()
                            with open("dom_button_texts.txt", "w", encoding="utf-8") as f:
                                for i in range(count):
                                    b = buttons.nth(i)
                                    if await b.is_visible():
                                        text = await b.inner_text()
                                        if text.strip():
                                            f.write(f"[{i}] {text.strip()}\n")
                            console.print("[green]✅ Saved to dom_button_texts.txt[/green]")
                        except Exception as e:
                            console.print(f"[red]❌ Failed: {e}[/red]")
                    elif sub == "2":
                        try:
                            divs = core.agent.page.locator("div")
                            count = await divs.count()
                            with open("dom_div_texts.txt", "w", encoding="utf-8") as f:
                                for i in range(count):
                                    d = divs.nth(i)
                                    if await d.is_visible():
                                        text = await d.inner_text()
                                        if text.strip():
                                            f.write(f"[{i}] {text.strip()}\n")
                            console.print("[green]✅ Saved to dom_div_texts.txt[/green]")
                        except Exception as e:
                            console.print(f"[red]❌ Failed: {e}[/red]")
                    elif sub == "3":
                        try:
                            all_nodes = core.agent.page.locator("[aria-label]")
                            count = await all_nodes.count()
                            with open("dom_aria_labels.txt", "w", encoding="utf-8") as f:
                                for i in range(count):
                                    node = all_nodes.nth(i)
                                    label = await node.get_attribute("aria-label")
                                    if label:
                                        f.write(f"[{i}] {label}\n")
                            console.print("[green]✅ Saved to dom_aria_labels.txt[/green]")
                        except Exception as e:
                            console.print(f"[red]❌ Failed: {e}[/red]")
                    elif sub == "4":
                        break
        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")

if __name__ == "__main__":
    asyncio.run(run_console())
