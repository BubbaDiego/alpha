# solflare_manager.py

from playwright.async_api import async_playwright
import asyncio
from utils.console_logger import ConsoleLogger

class SolflareManager:
    def __init__(self, extension_path: str, headless: bool = False):
        self.extension_path = extension_path
        self.headless = headless
        self.browser = None
        self.page = None

    async def launch_browser(self):
        ConsoleLogger.info("🚀 Launching browser with Solflare extension", source="Solflare")
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch_persistent_context(
            user_data_dir="/tmp/solflare-user-data",
            headless=self.headless,
            args=[
                f"--disable-extensions-except={self.extension_path}",
                f"--load-extension={self.extension_path}",
            ]
        )
        self.page = self.browser.pages[0]
        ConsoleLogger.success("✅ Browser launched with Solflare", source="Solflare")

    async def unlock_wallet(self, password: str):
        ConsoleLogger.info("🔐 Attempting to unlock Solflare", source="Solflare")
        try:
            input_box = await self.page.wait_for_selector("input[type='password']", timeout=10000)
            await input_box.fill(password)
            await input_box.press("Enter")
            ConsoleLogger.success("✅ Solflare unlocked", source="Solflare")
        except Exception as e:
            ConsoleLogger.error("❌ Failed to unlock Solflare", payload={"error": str(e)}, source="Solflare")

    async def approve_transaction(self):
        ConsoleLogger.info("🔍 Waiting for transaction modal", source="Solflare")
        try:
            button = await self.page.wait_for_selector("button:has-text('Approve')", timeout=10000)
            await button.click()
            ConsoleLogger.success("✅ Transaction approved", source="Solflare")
        except Exception as e:
            ConsoleLogger.error("❌ Failed to approve transaction", payload={"error": str(e)}, source="Solflare")

    async def connect_wallet(self, dapp_url: str):
        ConsoleLogger.info(f"🌐 Navigating to DApp: {dapp_url}", source="Solflare")
        try:
            await self.page.goto(dapp_url)
            ConsoleLogger.success("✅ Wallet connected to DApp", source="Solflare")
        except Exception as e:
            ConsoleLogger.error("❌ Failed to connect wallet to DApp", payload={"error": str(e)}, source="Solflare")

    async def close(self):
        await self.browser.close()
