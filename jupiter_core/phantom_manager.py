from typing import Optional, List
from playwright.sync_api import sync_playwright, Error
import os
import logging


class PhantomManager:
    def __init__(self, extension_path: str, user_data_dir: str = "playwright-data", headless: bool = False) -> None:
        self.extension_path = extension_path
        self.user_data_dir = user_data_dir
        self.headless = headless
        self.browser_context = None
        self.playwright = None
        self.page = None
        self.popup = None
        self.phantom_id = None

        self.logger = logging.getLogger(__name__)
        if self.extension_path.lower().endswith(".crx"):
            self.logger.warning("Provided extension_path is a .crx file. Please extract it to an unpacked folder.")

    def launch_browser(self) -> None:
            """Launch a Chromium browser with the Phantom extension loaded."""
            self.logger.debug("Launching browser with Phantom extension from %s", self.extension_path)
            self.playwright = sync_playwright().start()
            try:
                self.browser_context = self.playwright.chromium.launch_persistent_context(
                    self.user_data_dir,
                    headless=self.headless,
                    channel="chrome",
                    args=[
                        f"--disable-extensions-except={self.extension_path}",
                        f"--load-extension={self.extension_path}",
                        "--window-size=1280,720",
                        "--start-maximized",
                    ],
                )
            except Error as exc:
                self.logger.error("Error launching browser context: %s", exc)
                raise

            self.page = self.browser_context.new_page()
            self.page.on("console", lambda msg: self.logger.debug("PAGE CONSOLE: %s", msg.text))

            if os.path.exists(self.user_data_dir) and os.listdir(self.user_data_dir):
                timeout_value = 2500
                self.logger.debug(
                    "Existing user data detected. Using shorter service worker timeout: %d ms",
                    timeout_value,
                )
            else:
                timeout_value = 30000
                self.logger.debug(
                    "Fresh user data. Using longer service worker timeout: %d ms", timeout_value
                )

            self.logger.debug(
                "Waiting for service worker to register Phantom extension (timeout %d ms)...",
                timeout_value,
            )
            try:
                sw = self.browser_context.wait_for_event("serviceworker", timeout=timeout_value)
                self.phantom_id = sw.url.split("/")[2]
                self.logger.debug("Phantom extension loaded with ID: %s", self.phantom_id)
            except Error as exc:
                self.logger.error("Service worker not registered within timeout: %s", exc)
                for idx, pg in enumerate(self.browser_context.pages):
                    self.logger.debug("Open page %s: %s", idx, pg.url)
                fallback_id = "bfnaelmomeimhlpmgjnjophhpkkoljpa"
                self.logger.debug("Assuming Phantom extension ID as fallback: %s", fallback_id)
                self.phantom_id = fallback_id

        # ------------------------------------------------------------------

    def open_phantom_popup(self):
            """Open the Phantom popup UI."""
            if not self.phantom_id:
                self.logger.error("Phantom extension not loaded. Call launch_browser() first.")
                raise RuntimeError("Phantom extension not loaded. Call launch_browser() first.")
            self.logger.debug("Opening Phantom popup UI...")
            self.popup = self.browser_context.new_page()
            self.popup.on("console", lambda msg: self.logger.debug("POPUP CONSOLE: %s", msg.text))
            try:
                self.popup.goto(f"chrome-extension://{self.phantom_id}/popup.html", timeout=10000)
                self.popup.wait_for_load_state()
                self.logger.debug("Phantom popup UI loaded. URL: %s", self.popup.url)
            except Error as exc:
                self.logger.error("Error loading Phantom popup: %s", exc)
                raise
            return self.popup

        # ------------------------------------------------------------------

    def dismiss_post_unlock_dialog(self):
            """Dismiss the 'Click this dialog to continue' overlay if present."""
            overlay_selector = "text=Click this dialog to continue"
            try:
                self.popup.wait_for_selector(overlay_selector, timeout=3000)
                self.popup.click(overlay_selector)
                self.logger.debug("Dismissed the 'Click this dialog to continue' overlay.")
                self.popup.wait_for_timeout(1000)
            except Error as exc:
                self.logger.debug("No post-unlock dialog overlay found or timed out: %s", exc)

        # ------------------------------------------------------------------

    def approve_transaction(
            self,
            transaction_trigger_selector: str,
            confirm_selectors: Optional[List[str]] = None,
            trigger_timeout: int = 10000,
            confirm_timeout: int = 5000,
        ) -> None:
            """Trigger a transaction in the dApp and approve it in Phantom."""
            self.logger.debug("Triggering transaction with selector: %s", transaction_trigger_selector)
            try:
                self.page.click(transaction_trigger_selector, timeout=trigger_timeout)
            except Error as exc:
                self.logger.error("Error triggering transaction: %s", exc)
                raise

            if not self.popup or self.popup.is_closed():
                self.logger.debug("Phantom popup not open; opening popup for transaction approval.")
                self.open_phantom_popup()
            else:
                self.logger.debug("Bringing Phantom popup to front and reloading to update state.")
                self.popup.bring_to_front()
                self.popup.reload()

            if confirm_selectors is None:
                confirm_selectors = [
                    "button[data-testid='primary-button']:has-text('Confirm Transaction')",
                    "button[data-testid='primary-button']:has-text('Confirm')",
                    "text=Confirm",
                ]

            success = False
            for selector in confirm_selectors:
                try:
                    self.logger.debug("Waiting for confirm button with selector: %s", selector)
                    self.popup.wait_for_selector(selector, timeout=confirm_timeout)
                    self.logger.debug("Clicking confirm button with selector: %s", selector)
                    self.popup.click(selector, timeout=confirm_timeout)
                    success = True
                    break
                except Error as exc:
                    self.logger.warning("Confirm button not found with selector %s: %s", selector, exc)
                    continue

            if not success:
                self.logger.error("Failed to click any confirm button with provided selectors.")
                raise RuntimeError("Transaction approval failed: No confirm button found.")

            self.logger.debug("Transaction approved (Confirm clicked).")

        # ------------------------------------------------------------------

    def handle_onboarding(self) -> None:
            self.logger.debug("Handling Phantom onboarding...")
            try:
                self.popup.wait_for_selector("text=I already have a wallet", timeout=15000)
                self.popup.click("text=I already have a wallet", timeout=10000)
                self.logger.debug("Selected 'I already have a wallet' in onboarding.")
            except Error as exc:
                if "Target page, context or browser has been closed" in str(exc):
                    self.logger.warning("Phantom onboarding popup was closed. Skipping onboarding handling.")
                else:
                    self.logger.warning("Onboarding UI not detected or already handled: %s", exc)

        # ------------------------------------------------------------------

    def handle_wallet_selection(self, wallet_selector: str = "text=Use this wallet") -> None:
            self.logger.debug("Handling wallet selection with selector: %s", wallet_selector)
            try:
                self.popup.wait_for_selector(wallet_selector, timeout=15000)
                self.popup.click(wallet_selector, timeout=10000)
                self.logger.debug("Wallet selection completed.")
            except Error as exc:
                self.logger.warning("Wallet selection UI not detected or already handled: %s", exc)

        # ------------------------------------------------------------------

    def connect_wallet(
            self,
            dapp_url: str,
            dapp_connect_selector: str = "css=span.text-v2-primary",
            popup_connect_selector: str = "text=Connect",
            wallet_selection_selector: str = "text=Use this wallet",
            dapp_connected_selector: str = "text=Connected",
            phantom_password: Optional[str] = None,
        ) -> None:
            self.logger.debug("Navigating to dApp: %s", dapp_url)
            try:
                self.page.goto(dapp_url, timeout=15000)
                self.logger.debug("dApp page loaded. Current URL: %s", self.page.url)
            except Error as exc:
                self.logger.error("Error navigating to dApp: %s", exc)
                raise

            # Handle Jupiter T&C modal if it appears
            try:
                self.page.wait_for_selector("text=Acknowledge Terms and Conditions", timeout=3000)
                self.logger.debug("🛡️ Jupiter Terms modal detected.")
                checkbox = self.page.locator("text=Do not show again")
                if checkbox.is_visible():
                    checkbox.click()
                    self.logger.debug("☑️ Clicked 'Do not show again'")
                accept_btn = self.page.locator("text=Accept and Continue")
                if accept_btn.is_visible():
                    accept_btn.click()
                    self.logger.debug("✓ Accepted Jupiter T&C")
                    self.page.wait_for_timeout(500)
            except Exception:
                self.logger.debug("No Jupiter T&C modal present or already dismissed.")

            self.logger.debug("Checking if wallet is already connected using selector: %s", dapp_connected_selector)
            try:
                self.page.wait_for_selector(dapp_connected_selector, timeout=5000)
                self.logger.debug("Wallet already connected on dApp. Skipping connect flow.")
                return
            except Error:
                self.logger.debug("Wallet not connected; proceeding with connect flow.")

            self.logger.debug("Waiting for dApp connect button...")
            connect_candidates = self.page.locator("button", has_text="Connect")
            for i in range(connect_candidates.count()):
                btn = connect_candidates.nth(i)
                if btn.is_visible():
                    btn.click()
                    self.logger.debug(f"Clicked dApp Connect button [index {i}]")
                    break
            else:
                raise RuntimeError("❌ Could not find a visible 'Connect' button on Jupiter.")

            self.logger.debug("Opening Phantom popup to approve wallet connection.")
            popup = self.open_phantom_popup()
            if phantom_password:
                self.unlock_phantom(phantom_password)
            else:
                self.logger.warning("No Phantom password provided. Please disable auto-lock in Phantom settings.")

            self.popup.wait_for_timeout(500)
            self.handle_onboarding()
            if popup.is_closed():
                self.logger.debug("Phantom popup closed after onboarding, reopening.")
                popup = self.open_phantom_popup()
                popup.wait_for_timeout(500)
                self.handle_onboarding()

            success = False
            attempts = 0
            max_attempts = 2
            while not success and attempts < max_attempts:
                try:
                    popup.wait_for_selector(popup_connect_selector, timeout=10000)
                    self.logger.debug("Clicking Phantom popup connect button.")
                    popup.click(popup_connect_selector, timeout=10000)
                    success = True
                except Error as exc:
                    if popup.is_closed():
                        self.logger.warning("Phantom popup closed unexpectedly; assuming connection is approved.")
                        success = True
                    else:
                        attempts += 1
                        self.logger.error("Error in Phantom connect button flow: %s", exc)
                        self.logger.debug("Reopening Phantom popup and retrying...")
                        popup = self.open_phantom_popup()

            if not success:
                self.logger.warning("Phantom connect button not found after multiple attempts; assuming connection is approved.")

            self.handle_wallet_selection(wallet_selector=wallet_selection_selector)
            self.logger.debug("Waiting for dApp to confirm wallet association.")
            try:
                self.page.wait_for_selector(dapp_connected_selector, timeout=10000)
                self.logger.debug("DApp wallet association confirmed.")
            except Error as exc:
                self.logger.warning("DApp wallet association not confirmed: %s", exc)

    def capture_order_payload(self, url_keyword: str, timeout: int = 10000):
            """Capture payload for a request whose URL contains ``url_keyword``."""
            self.logger.debug("Waiting for network request with keyword: %s", url_keyword)
            try:
                request = self.page.wait_for_event(
                    "requestfinished",
                    predicate=lambda req: url_keyword in req.url,
                    timeout=timeout,
                )
                try:
                    payload = request.post_data_json()
                except Exception:
                    payload = request.post_data()
                self.logger.debug("Captured order payload: %s", payload)
                return payload
            except Error as exc:
                self.logger.error("Error capturing order payload: %s", exc)
                raise

        # ------------------------------------------------------------------

    def unlock_phantom(self, phantom_password: str) -> None:
            """Unlock the Phantom wallet using the given password."""
            self.logger.debug("Unlocking Phantom: selecting password input field.")
            if self.popup is None or self.popup.is_closed():
                self.logger.debug("Phantom popup not open; opening popup for unlocking.")
                self.open_phantom_popup()
            try:
                self.popup.wait_for_selector(
                    "input[data-testid='unlock-form-password-input']", timeout=5000
                )
                self.logger.debug("Phantom password input detected. Filling in password.")
                self.popup.fill(
                    "input[data-testid='unlock-form-password-input']", phantom_password, timeout=2000
                )
                self.logger.debug("Password entered; now clicking the unlock button.")
                self.popup.click(
                    "button[data-testid='unlock-form-submit-button']", timeout=5000
                )
                self.logger.debug("Clicked unlock button. Waiting briefly for unlock to complete...")
                self.popup.wait_for_timeout(2000)
                self.dismiss_post_unlock_dialog()
            except Error as exc:
                self.logger.error("Error unlocking Phantom: %s", exc)
                raise

        # ------------------------------------------------------------------

    def close(self) -> None:
            """Close the browser context and Playwright instance."""
            self.logger.debug("Closing browser context.")
            if self.browser_context:
                self.browser_context.close()
            if self.playwright:
                self.playwright.stop()
            self.logger.debug("Browser closed.")
