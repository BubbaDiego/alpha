import os
from phantom_manager import PhantomManager
from jupiter_perps_flow import JupiterPerpsFlow
from dotenv import load_dotenv
load_dotenv()

def main():
    EXTENSION_PATH = r"C:\v0.83\wallets\phantom_wallet"
    DAPP_URL = "https://jup.ag/perps-legacy/short/SOL-SOL"
    phantom_password = os.environ.get("PHANTOM_PASSWORD")

    pm = PhantomManager(extension_path=EXTENSION_PATH, headless=False)
    pm.launch_browser()
    jp = JupiterPerpsFlow(phantom_manager=pm)

    try:
        pm.connect_wallet(dapp_url=DAPP_URL, phantom_password=phantom_password)
        print("✅ Wallet connected!")
    except Exception as e:
        print("Error connecting wallet:", e)

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
        print("12: Dump Visible Buttons 🧹")
        print("13: Dump All Text Nodes 📄")
        print("14: Dump All <div> With Text 🔍")
        cmd = input("Enter command number: ").strip()

        if cmd == "1":
            try:
                pm.connect_wallet(dapp_url=DAPP_URL, phantom_password=phantom_password)
                print("✅ Wallet connected!")
            except Exception as e:
                print("Error connecting wallet:", e)
        elif cmd == "2":
            try:
                pm.approve_transaction(transaction_trigger_selector="text=Confirm")
                print("✅ Transaction approved!")
            except Exception as e:
                print("Error approving transaction:", e)
        elif cmd == "3":
            if phantom_password:
                try:
                    pm.unlock_phantom(phantom_password)
                    print("🔓 Phantom unlocked!")
                except Exception as e:
                    print("Error unlocking Phantom:", e)
            else:
                print("⚠️ No Phantom password provided. Set PHANTOM_PASSWORD or disable auto-lock in Phantom settings.")
        elif cmd == "4":
            pos_type = input("📈 Enter position type (long/short): ").strip().lower()
            try:
                jp.select_position_type(pos_type)
                print("✅ Position type set to", pos_type)
            except Exception as e:
                print("Error selecting position type:", e)
        elif cmd == "5":
            asset = input("💰 Enter payment asset (e.g., SOL, USDT, USDC, WBTC, WETH): ").strip().upper()
            try:
                jp.select_payment_asset(asset)
                print("✅ Payment asset set to", asset)
            except Exception as e:
                print("Error selecting payment asset:", e)
        elif cmd == "6":
            order_type = input("💱 Enter order type (market/limit): ").strip().lower()
            try:
                jp.select_order_type(order_type)
                print("✅ Order type set to", order_type)
            except Exception as e:
                print("Error selecting order type:", e)
        elif cmd == "7":
            size = input("📏 Enter position size: ").strip()
            try:
                jp.set_position_size(size)
                print("✅ Position size set to", size)
            except Exception as e:
                print("Error setting position size:", e)
        elif cmd == "8":
            leverage = input("⚖️ Enter leverage (e.g., 7.8x): ").strip()
            try:
                jp.set_leverage(leverage)
                print("✅ Leverage set to", leverage)
            except Exception as e:
                print("Error setting leverage:", e)
        elif cmd == "9":
            try:
                jp.open_position()
                print("🚀 Position opened!")
            except Exception as e:
                print("Error opening position:", e)
        elif cmd == "10":
            keyword = input("📦 Enter URL keyword to capture order payload (e.g., 'order-submit'): ").strip()
            try:
                payload = pm.capture_order_payload(keyword)
                print("✅ Captured order payload:")
                print(payload)
            except Exception as e:
                print("Error capturing order payload:", e)
        elif cmd == "12":
            try:
                print("🕵️ Dumping visible buttons to button_dump.txt...")
                from phantom_debug_mode_patch import dump_visible_buttons
                dump_visible_buttons(pm.page)
                print("✅ Dump complete. Check button_dump.txt")
            except Exception as e:
                print(f"Error during DOM sweep: {e}")
        elif cmd == "13":
            try:
                all_text = pm.page.locator("*").all_inner_texts()
                with open("all_text_dump.txt", "w", encoding="utf-8") as f:
                    for text in all_text:
                        cleaned = text.strip()
                        if cleaned:
                            f.write(cleaned + "\n")
                print("✅ Dumped all visible inner text to all_text_dump.txt")
            except Exception as e:
                print(f"Error dumping text nodes: {e}")
        elif cmd == "14":
            try:
                divs = pm.page.locator("div")
                with open("div_text_dump.txt", "w", encoding="utf-8") as f:
                    for i in range(divs.count()):
                        try:
                            div = divs.nth(i)
                            if div.is_visible():
                                text = div.inner_text().strip()
                                if text:
                                    f.write(f"[{i}] {text}\n")
                        except Exception:
                            pass
                print("✅ Dumped visible <div> elements to div_text_dump.txt")
            except Exception as e:
                print(f"Error dumping <div> content: {e}")
        elif cmd == "11":
            print("❌ Exiting...")
            break
        else:
            print("❓ Invalid command. Please try again.")

    pm.close()

if __name__ == "__main__":
    main()
