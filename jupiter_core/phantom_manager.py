import os
import logging
from typing import Optional, List
from playwright.async_api import async_playwright, Page, BrowserContext, Error

logger = logging.getLogger(__name__)

class PhantomManager:
    def __init__(self, extension_path: str, user_data_dir: str = "playwright-data", headless: bool = False) -> None:
        self.extension_path = extension_path
        self.user_data_dir = user_data_dir
        self.headless = headless
        self.browser_context: Optional[BrowserContext] = None
        self.playwright = None
        self.page: Optional[Page] = None
        self.popup: Optional[Page] = None
        self.phantom_id = None

    async def launch_browser(self) -> None:
        logger.info("Launching browser with Phantom extension...")
        self.playwright = await async_playwright().start()
        self.browser_context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.user_data_dir,
            headless=self.headless,
            channel="chrome",
            args=[
                f"--disable-extensions-except={self.extension_path}",
                f"--load-extension={self.extension_path}",
                "--window-size=1280,720",
                "--start-maximized",
            ],
        )
        self.page = await self.browser_context.new_page()
        self.page.on("console", lambda msg: logger.debug("PAGE CONSOLE: %s", msg.text))

        if os.path.exists(self.user_data_dir) and os.listdir(self.user_data_dir):
            timeout_value = 2500
        else:
            timeout_value = 30000

        try:
            sw = await self.browser_context.wait_for_event("serviceworker", timeout=timeout_value)
            self.phantom_id = sw.url.split("/")[2]
        except Error:
            self.phantom_id = "bfnaelmomeimhlpmgjnjophhpkkoljpa"

    async def open_phantom_popup(self):
        if not self.phantom_id:
            raise RuntimeError("Phantom extension not loaded.")
        self.popup = await self.browser_context.new_page()
        self.popup.on("console", lambda msg: logger.debug("POPUP CONSOLE: %s", msg.text))
        await self.popup.goto(f"chrome-extension://{self.phantom_id}/popup.html", timeout=10000)
        await self.popup.wait_for_load_state()
        return self.popup

    async def unlock_phantom(self, phantom_password: str) -> None:
        logger.debug("Unlocking Phantom: selecting password input field.")
        if self.popup is None or self.popup.is_closed():
            await self.open_phantom_popup()
        await self.popup.wait_for_selector("input[data-testid='unlock-form-password-input']", timeout=5000)
        await self.popup.fill("input[data-testid='unlock-form-password-input']", phantom_password, timeout=2000)
        await self.popup.click("button[data-testid='unlock-form-submit-button']", timeout=5000)
        await self.popup.wait_for_timeout(2000)

    async def connect_wallet(
        self,
        dapp_url: str,
        dapp_connect_selector: str = "css=span.text-v2-primary",
        popup_connect_selector: str = "text=Connect",
        wallet_selection_selector: str = "text=Use this wallet",
        dapp_connected_selector: str = "text=Connected",
        phantom_password: Optional[str] = None,
    ) -> None:
        logger.debug("Navigating to dApp: %s", dapp_url)
        await self.page.goto(dapp_url, timeout=15000)

        try:
            await self.page.wait_for_selector("text=Acknowledge Terms and Conditions", timeout=3000)
            if await self.page.locator("text=Do not show again").is_visible():
                await self.page.locator("text=Do not show again").click()
            if await self.page.locator("text=Accept and Continue").is_visible():
                await self.page.locator("text=Accept and Continue").click()
        except Exception:
            pass

        try:
            await self.page.wait_for_selector(dapp_connected_selector, timeout=5000)
            logger.info("Wallet already connected")
            return
        except Error:
            pass

        connect_candidates = self.page.locator("button", has_text="Connect")
        count = await connect_candidates.count()
        for i in range(count):
            btn = connect_candidates.nth(i)
            if await btn.is_visible():
                await btn.click()
                break

        popup = await self.open_phantom_popup()
        if phantom_password:
            await self.unlock_phantom(phantom_password)

        success = False
        attempts = 0
        while not success and attempts < 2:
            try:
                await popup.wait_for_selector(popup_connect_selector, timeout=10000)
                await popup.click(popup_connect_selector, timeout=10000)
                success = True
            except Error:
                if popup.is_closed():
                    success = True
                else:
                    attempts += 1
                    popup = await self.open_phantom_popup()

        await popup.wait_for_selector(wallet_selection_selector, timeout=15000)
        await popup.click(wallet_selection_selector, timeout=10000)
        await self.page.wait_for_selector(dapp_connected_selector, timeout=10000)

    async def close(self) -> None:
        if self.browser_context:
            await self.browser_context.close()
        if self.playwright:
            await self.playwright.stop()