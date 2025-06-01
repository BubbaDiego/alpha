# order_core/agent_phantom.py

import os
import logging
from typing import Optional
from playwright.async_api import async_playwright, Page, BrowserContext, Error

logger = logging.getLogger(__name__)

class PhantomAgent:
    def __init__(self, extension_path: str, headless: bool = False, user_data_dir: str = "phantom-user-data"):
        self.extension_path = extension_path
        self.headless = headless
        self.user_data_dir = user_data_dir
        self.browser_context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.popup: Optional[Page] = None
        self.phantom_id: Optional[str] = None
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
        self.page = await self.browser_context.new_page()
        pages = self.browser_context.pages
        if pages:
            self.page = pages[0]

        try:
            sw = await self.browser_context.wait_for_event("serviceworker", timeout=10000)
            self.phantom_id = sw.url.split("/")[2]
        except Error:
            self.phantom_id = "bfnaelmomeimhlpmgjnjophhpkkoljpa"

    async def open_popup(self):
        if not self.phantom_id:
            raise RuntimeError("Phantom extension ID not loaded.")
        self.popup = await self.browser_context.new_page()
        await self.popup.goto(f"chrome-extension://{self.phantom_id}/popup.html", timeout=10000)
        await self.popup.wait_for_load_state()
        return self.popup

    async def unlock(self, password: str):
        print("🔐 Attempting to unlock Phantom")
        if not self.popup or self.popup.is_closed():
            self.popup = await self.open_popup()
        try:
            await self.popup.wait_for_selector("input[data-testid='unlock-form-password-input']", timeout=7000)
            await self.popup.fill("input[data-testid='unlock-form-password-input']", password)
            await self.popup.click("button[data-testid='unlock-form-submit-button']", timeout=3000)
            await self.popup.wait_for_timeout(1000)
            print("✅ Phantom unlocked")
        except Exception as e:
            print(f"❌ Failed to unlock Phantom: {e}")

    async def connect_wallet(self, dapp_url: str):
        print(f"🌐 Navigating to DApp: {dapp_url}")
        await self.page.goto(dapp_url, timeout=15000)
        try:
            btn = self.page.locator("button:has-text('Connect')")
            if await btn.is_visible():
                await btn.click()
        except Exception:
            pass

        self.popup = await self.open_popup()
        try:
            await self.popup.click("text=Connect", timeout=10000)
            await self.popup.click("text=Use this wallet", timeout=10000)
        except Exception as e:
            print(f"⚠️ Connection flow skipped or already connected: {e}")

    async def confirm_transaction(self):
        popup = self.popup or await self.open_popup()
        btn = popup.locator("div[role='dialog'] button:has-text('Confirm')")
        await btn.first.wait_for(state="visible", timeout=5000)
        await btn.first.click(timeout=3000)
