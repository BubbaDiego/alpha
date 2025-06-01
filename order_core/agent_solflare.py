# order_core/agent_solflare.py

import os
import logging
from typing import Optional
from playwright.async_api import async_playwright, Page, BrowserContext, Error

logger = logging.getLogger(__name__)

class SolflareAgent:
    def __init__(self, extension_path: str, headless: bool = False, user_data_dir: str = "solflare-user-data"):
        self.extension_path = extension_path
        self.headless = headless
        self.user_data_dir = user_data_dir
        self.browser_context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.popup: Optional[Page] = None
        self.playwright = None

    async def launch_browser(self):
        self.playwright = await async_playwright().start()
        self.browser_context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.user_data_dir,
            headless=self.headless,
            args=[
                f"--disable-extensions-except={self.extension_path}",
                f"--load-extension={self.extension_path}",
                "--window-size=1280,720",
            ]
        )
        pages = self.browser_context.pages
        self.page = pages[0] if pages else await self.browser_context.new_page()

    async def unlock(self, password: str):
        print("🔐 Attempting to unlock Solflare")
        try:
            input_box = await self.page.wait_for_selector("input[type='password']", timeout=10000)
            await input_box.fill(password)
            await input_box.press("Enter")
            print("✅ Solflare unlocked")
        except Exception as e:
            print(f"❌ Failed to unlock Solflare: {e}")

    async def connect_wallet(self, dapp_url: str):
        print(f"🌐 Navigating to DApp: {dapp_url}")
        try:
            await self.page.goto(dapp_url, timeout=15000)
            connect_btn = self.page.locator("button:has-text('Connect')")
            if await connect_btn.first.is_visible():
                await connect_btn.first.click(timeout=5000)
                print("✅ Clicked Connect button in DApp")

                # Wait for the popup that Solflare triggers
                self.popup = await self.browser_context.wait_for_event("page", timeout=7000)
                await self.popup.wait_for_load_state()
                print("✅ Solflare popup opened")
            else:
                print("⚠️ No Connect button found — already connected?")
        except Exception as e:
            print(f"❌ Failed to connect wallet to DApp: {e}")

    async def click_connect_button(self):
        print("🖱️ Attempting to click Connect button in dApp")
        try:
            connect_btn = self.page.locator("button:has-text('Connect')")
            if await connect_btn.first.is_visible():
                await connect_btn.first.click(timeout=5000)
                print("✅ Clicked Connect button in dApp")
            else:
                print("⚠️ Connect button not visible")
        except Exception as e:
            print(f"❌ Error clicking Connect button: {e}")

    async def confirm_connect_modal(self, auto_connect=True, auto_approve=True):
        print("🪪 Confirming wallet connect modal in popup...")
        try:
            popup = self.popup
            if not popup:
                print("❌ No popup available. Did you trigger it via the DApp connect button?")
                return

            if auto_connect:
                checkbox1 = popup.locator("text=Auto-connect")
                if await checkbox1.is_visible():
                    await checkbox1.click()
                    print("☑️ Enabled Auto-connect")

            if auto_approve:
                checkbox2 = popup.locator("text=Auto-approve")
                if await checkbox2.is_visible():
                    await checkbox2.click()
                    print("☑️ Enabled Auto-approve")

            await popup.wait_for_selector("div[role='dialog']", timeout=7000)
            await popup.wait_for_timeout(500)
            await popup.evaluate("""
                const modal = document.querySelector('div[role="dialog"]');
                const connectBtn = [...modal.querySelectorAll('button')].find(btn => btn.innerText.includes('Connect'));
                connectBtn?.click();
            """)
            await popup.wait_for_timeout(1000)
            print("✅ Triggered connect inside popup")
        except Exception as e:
            print(f"❌ Failed to confirm connect modal: {e}")

    async def confirm_transaction(self):
        print("🔍 Waiting for Solflare transaction modal")
        try:
            button = await self.page.wait_for_selector("button:has-text('Approve')", timeout=10000)
            await button.click()
            print("✅ Transaction approved")
        except Exception as e:
            print(f"❌ Failed to approve transaction: {e}")
