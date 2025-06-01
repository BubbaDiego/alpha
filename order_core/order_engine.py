# order_core/order_engine.py

from typing import Optional
from order_core.order_model import OrderModel

class OrderEngine:
    def __init__(self, agent, broker):
        self.agent = agent
        self.broker = broker
        self.order_definition = {}

    async def connect_wallet(self, dapp_url: str):
        await self.agent.connect_wallet(dapp_url)

    async def select_position_type(self, kind: str):
        await self.agent.page.click(f"button:has-text('{kind.capitalize()}')")
        self.order_definition["position_type"] = kind.lower()

    async def select_order_type(self, kind: str):
        await self.agent.page.click(f"button:has-text('{kind.capitalize()}')")
        self.order_definition["order_type"] = kind.lower()

    async def select_asset(self, symbol: str):
        await self.agent.page.locator(f"button:visible:has-text('{symbol}')").first.click(timeout=10000)
        self.order_definition["asset"] = symbol.upper()

    async def select_collateral_asset(self, symbol: str = "SOL"):
        self.order_definition["collateral_asset"] = symbol.upper()

    async def set_position_size(self, size: str):
        await self.agent.page.fill("input[placeholder='0.00']", size)
        self.order_definition["position_size"] = float(size)

    async def set_leverage(self, leverage: str):
        # Jupiter leverage starts at 1.1x and increments by 0.1x via "+" button.
        try:
            desired = float(leverage.replace("x", ""))
            if desired < 1.1:
                raise ValueError("Minimum leverage is 1.1x")

            clicks = int((desired - 1.1) / 0.1)
            for _ in range(clicks):
                await self.agent.page.click("button:has-text('+')")
                await self.agent.page.wait_for_timeout(100)

            self.order_definition["leverage"] = desired
        except Exception as e:
            print(f"❌ Leverage setting error: {e}")

    async def confirm_order(self):
        print("🔎 Looking for button with type='submit'")
        try:
            await self.agent.page.evaluate("""
                const btn = document.querySelector('button[type="submit"]');
                if (btn) {
                    console.log("✅ Found confirm button:", btn.innerText);
                    btn.click();
                } else {
                    console.warn("⚠️ No confirm button found with type=submit");
                }
            """)
            print("✅ Clicked submit-type confirm button")
        except Exception as e:
            print(f"❌ Failed to click confirm: {e}")

    async def confirm_wallet_transaction(self):
        popup = self.agent.popup or await self.agent.open_popup()
        btn = popup.locator("div[role='dialog'] button:has-text('Confirm')")
        await btn.first.wait_for(state="visible", timeout=5000)
        await btn.first.click(timeout=3000)

    async def place_tp_sl_limit_order(self, input_mint: str, output_mint: str,
                                      in_amount: int, out_amount: int, private_key: str):
        from tp_sl_helper import place_tp_sl_order
        result = place_tp_sl_order(
            private_key_base58=private_key,
            input_mint=input_mint,
            output_mint=output_mint,
            in_amount=in_amount,
            out_amount=out_amount,
        )
        return result

    def get_order(self) -> Optional[OrderModel]:
        try:
            return OrderModel(
                id="generated-later",
                asset=self.order_definition.get("asset", "UNKNOWN"),
                position_type=self.order_definition.get("position_type", ""),
                collateral_asset=self.order_definition.get("collateral_asset", ""),
                position_size=float(self.order_definition.get("position_size", 0)),
                leverage=float(self.order_definition.get("leverage", 0)),
                order_type=self.order_definition.get("order_type", "market"),
                status="pending",
                entry_price=float(self.order_definition.get("entry_price", 0)),
                fees=float(self.order_definition.get("fees", 0)),
                source="jupiter"
            )
        except Exception as e:
            print("❌ Error building OrderModel:", e)
            return None
