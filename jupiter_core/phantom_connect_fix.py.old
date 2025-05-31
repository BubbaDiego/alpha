from playwright.sync_api import Page
import logging

logger = logging.getLogger(__name__)


def find_and_click_connect_button(page: Page) -> None:
    """Try several selectors to click the Phantom connect button."""
    # Expand wallet list if needed
    try:
        if page.locator("text=View More Wallets").is_visible():
            logger.debug("View More Wallets button visible — expanding wallet list.")
            page.click("text=View More Wallets")
            page.wait_for_timeout(500)
    except Exception as e:  # pragma: no cover - best effort fallback
        logger.debug(f"Wallet expand check failed or skipped: {e}")

    selectors = [
        "text=Phantom",
        "css=span:text('Phantom')",
        "button:has-text(\"Phantom\")",
        "xpath=//button[contains(., 'Phantom')]",
        "xpath=//span[contains(text(), 'Phantom')]/ancestor::button",
    ]
    for sel in selectors:
        try:
            locator = page.locator(sel)
            if locator.is_visible():
                logger.debug(f"Clicking Phantom connect button with selector: {sel}")
                locator.click()
                return
        except Exception as e:  # pragma: no cover - optional selectors
            logger.debug(f"Selector failed: {sel} -> {e}")
            continue

    raise RuntimeError("\u274c No Phantom wallet button found in wallet selector modal.")
