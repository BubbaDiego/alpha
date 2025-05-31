from __future__ import annotations

from typing import Optional

from jupiter_core.phantom_manager import PhantomManager
from jupiter_core.jupiter_perps_flow import JupiterPerpsFlow


class JupiterEngineCore:
    """Async wrapper around :class:`PhantomManager` and :class:`JupiterPerpsFlow`."""

    def __init__(
        self,
        extension_path: str,
        dapp_url: str,
        *,
        phantom_password: Optional[str] = None,
        headless: bool = False,
    ) -> None:
        self.extension_path = extension_path
        self.dapp_url = dapp_url
        self.phantom_password = phantom_password
        self.headless = headless

        self.pm: Optional[PhantomManager] = None
        self.jp: Optional[JupiterPerpsFlow] = None
        self.page = None

    # ------------------------------------------------------------------
    async def launch(self) -> None:
        """Launch the browser and initialise helpers."""
        self.pm = PhantomManager(extension_path=self.extension_path, headless=self.headless)
        await self.pm.launch_browser()
        self.page = self.pm.page
        self.jp = JupiterPerpsFlow(self.pm)

    async def close(self) -> None:
        if self.pm:
            await self.pm.close()

    # Context manager helpers -----------------------------------------
    async def __aenter__(self) -> "JupiterEngineCore":
        await self.launch()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()
