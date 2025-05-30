"""Interactive console application for Phantom wallet testing."""

import os
from pathlib import Path

try:  # Optional dependency for loading environment variables
    from dotenv import load_dotenv
except Exception:  # pragma: no cover - optional dependency may be missing
    def load_dotenv(*_args, **_kwargs):
        pass

from jupiter_integration.playwright import PhantomManager, JupiterPerpsFlow

load_dotenv()


def main() -> None:
    """Run the Phantom wallet demo console."""

    # Set paths and URL (update these as needed)
    EXTENSION_PATH = os.getenv(
        "PHANTOM_PATH",
        str(Path(__file__).resolve().parents[2] / "wallets" / "phantom_wallet"),
    )
    DAPP_URL = "https://jup.ag/perps-legacy/short/SOL-SOL"
    phantom_password = os.environ.get("PHANTOM_PASSWORD")

    # Initialize PhantomManager and launch the browser.
    pm = PhantomManager(extension_path=EXTENSION_PATH, headless=False)
    pm.launch_browser()

    # Create the JupiterPerpsFlow instance.
    jp = JupiterPerpsFlow(phantom_manager=pm)

    # Try to connect the wallet.
    try:
        pm.connect_wallet(dapp_url=DAPP_URL, phantom_password=phantom_password)
        print("✅ Wallet connected!")
    except Exception as e:  # pragma: no cover - demo utility
        print("Error connecting wallet:", e)

    # Main interactive menu with Unicode icons in the menu display.
    while True:
        print("\nAvailable commands:")
        print("1: Connect Wallet 🔗")
        print("2: Approve Transaction ✅")
        print("3: Unlock Phantom 🔓")
        print("4: Set Position Type 📈")
        print("5: Select Payment Asset 💰")
        print("6: Set Order Type 💱")
        print("7: Set Position Size 📏")
        print("8: Set Leverage ⚖️")
        print("9: Open Position 🚀")
        print("10: Capture Order Payload 📦")
        print("11: Exit ❌")
        cmd = input("Enter command number: ").strip()

        if cmd == "1":
            try:
                pm.connect_wallet(dapp_url=DAPP_URL, phantom_password=phantom_password)
                print("✅ Wallet connected!")
            except Exception as e:  # pragma: no cover - demo utility
                print("Error connecting wallet:", e)
        elif cmd == "2":
            try:
                pm.approve_transaction(transaction_trigger_selector="text=Confirm")
                print("✅ Transaction approved!")
            except Exception as e:  # pragma: no cover - demo utility
                print("Error approving transaction:", e)
        elif cmd == "3":
            if phantom_password:
                try:
                    pm.unlock_phantom(phantom_password)
                    print("🔓 Phantom unlocked!")
                except Exception as e:  # pragma: no cover - demo utility
                    print("Error unlocking Phantom:", e)
            else:
                print(
                    "⚠️ No Phantom password provided. Set PHANTOM_PASSWORD or disable auto-lock in Phantom settings."
                )
        elif cmd == "4":
            pos_type = input("📈 Enter position type (long/short): ").strip().lower()
            try:
                jp.select_position_type(pos_type)
                print("✅ Position type set to", pos_type)
            except Exception as e:  # pragma: no cover - demo utility
                print("Error selecting position type:", e)
        elif cmd == "5":
            asset = input(
                "💰 Enter payment asset (e.g., SOL, USDT, USDC, WBTC, WETH): "
            ).strip().upper()
            try:
                jp.select_payment_asset(asset)
                print("✅ Payment asset set to", asset)
            except Exception as e:  # pragma: no cover - demo utility
                print("Error selecting payment asset:", e)
        elif cmd == "6":
            order_type = input("💱 Enter order type (market/limit): ").strip().lower()
            try:
                jp.select_order_type(order_type)
                print("✅ Order type set to", order_type)
            except Exception as e:  # pragma: no cover - demo utility
                print("Error selecting order type:", e)
        elif cmd == "7":
            size = input("📏 Enter position size: ").strip()
            try:
                jp.set_position_size(size)
                print("✅ Position size set to", size)
            except Exception as e:  # pragma: no cover - demo utility
                print("Error setting position size:", e)
        elif cmd == "8":
            leverage = input("⚖️ Enter leverage (e.g., 7.8x): ").strip()
            try:
                jp.set_leverage(leverage)
                print("✅ Leverage set to", leverage)
            except Exception as e:  # pragma: no cover - demo utility
                print("Error setting leverage:", e)
        elif cmd == "9":
            try:
                jp.open_position()
                print("🚀 Position opened!")
            except Exception as e:  # pragma: no cover - demo utility
                print("Error opening position:", e)
        elif cmd == "10":
            keyword = input(
                "📦 Enter URL keyword to capture order payload (e.g., 'order-submit'): "
            ).strip()
            try:
                payload = pm.capture_order_payload(keyword)
                print("✅ Captured order payload:")
                print(payload)
            except Exception as e:  # pragma: no cover - demo utility
                print("Error capturing order payload:", e)
        elif cmd == "11":
            print("❌ Exiting...")
            break
        else:
            print("❓ Invalid command. Please try again.")

    pm.close()


if __name__ == "__main__":  # pragma: no cover - script entry point
    main()

