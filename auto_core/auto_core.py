"""Automated collateral management via the Jupiter UI."""

from typing import Optional

from playwright.sync_api import sync_playwright

# When executed as a script, ``__package__`` is ``None`` and relative imports
# fail. Adjust ``sys.path`` to make ``auto_core`` importable so the relative
# import below succeeds.
if __name__ == "__main__" and __package__ is None:
    import os
    import sys

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    __package__ = "auto_core"

from . import phantom_workflow as pwf


class AutoCore:
    """High level workflows using Playwright and Phantom."""

    def __init__(
        self,
        phantom_path: str,
        profile_dir: str,
        headless: bool = False,
        *,
        extension_id: Optional[str] = None,
        user_agent: Optional[str] = None,
        slow_mo: Optional[int] = None,
    ) -> None:
        self.phantom_path = phantom_path
        self.profile_dir = profile_dir
        self.headless = headless
        self.extension_id = extension_id
        self.user_agent = user_agent
        self.slow_mo = slow_mo

    # ------------------------------------------------------------------
    def _launch_context(self):
        pw = sync_playwright().start()
        args = [
            f"--disable-extensions-except={self.phantom_path}",
            f"--load-extension={self.phantom_path}",
        ]
        if self.headless:
            args.insert(0, "--headless=new")

        context = pw.chromium.launch_persistent_context(
            self.profile_dir,
            channel="chromium",
            headless=self.headless,
            args=args,
            user_agent=self.user_agent,
            slow_mo=self.slow_mo,
        )
        page = context.new_page()
        page.goto("https://jup.ag/perps")
        if self.headless:
            pwf.open_extension_popup(context, self.extension_id)
        return pw, context, page

    def _close(self, pw, context):
        context.close()
        pw.stop()

    # ------------------------------------------------------------------
    def deposit_collateral(self, amount: float) -> None:
        """Automate collateral deposit via the UI."""
        pw, ctx, page = self._launch_context()
        try:
            pwf.connect_wallet(page)
            page.fill("input[type=number]", str(amount))
            page.click("button:has-text('Deposit')")
            pwf.approve_popup(page)
            pwf.confirm_transaction(page)
        finally:
            self._close(pw, ctx)

    def withdraw_collateral(self, amount: float) -> None:
        """Automate collateral withdrawal via the UI."""
        pw, ctx, page = self._launch_context()
        try:
            pwf.connect_wallet(page)
            page.fill("input[type=number]", str(amount))
            page.click("button:has-text('Withdraw')")
            pwf.approve_popup(page)
            pwf.confirm_transaction(page)
        finally:
            self._close(pw, ctx)

