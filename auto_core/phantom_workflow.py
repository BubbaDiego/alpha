"""Helper workflow for Phantom wallet automation via Playwright.

Selectors and workflow steps follow the collateral automation white paper
located at ``sonic_labs/collateral_management_playwright_white_paper.md``.
"""

from playwright.sync_api import Page, BrowserContext
from typing import Optional


def open_extension_popup(context: BrowserContext, extension_id: Optional[str]) -> Optional[Page]:
    """Open the Phantom popup page explicitly.

    This is useful in headless mode where the Phantom window is not
    automatically displayed.
    """
    if not extension_id:
        return None
    popup_page = context.new_page()
    popup_page.goto(f"chrome-extension://{extension_id}/popup.html")
    return popup_page


def connect_wallet(page: Page) -> None:
    """Connect Phantom wallet on Jupiter using the connect popup."""
    # Click the connect button on Jupiter
    page.click("button:has-text('Connect')")
    popup = page.context.wait_for_event("page")
    wallet_page = popup.value if hasattr(popup, "value") else popup
    wallet_page.wait_for_selector("button:has-text('Connect')")
    wallet_page.click("button:has-text('Connect')")
    wallet_page.close()


def approve_popup(page: Page) -> None:
    """Approve a Phantom confirmation popup."""
    popup = page.context.wait_for_event("page")
    p = popup.value if hasattr(popup, "value") else popup
    p.wait_for_selector("button:has-text('Approve')")
    p.click("button:has-text('Approve')")
    p.close()


def confirm_transaction(page: Page, timeout: int = 30_000) -> None:
    """Wait for Jupiter UI to display a transaction confirmation."""
    page.wait_for_selector("text=Transaction confirmed", timeout=timeout)

