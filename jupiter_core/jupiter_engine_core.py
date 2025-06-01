
from __future__ import annotations

from typing import Optional, Literal

from jupiter_core.phantom_manager import PhantomManager
from jupiter_core.solflare_manager import SolflareManager
from jupiter_core.jupiter_perps_flow import JupiterPerpsFlow

WalletType = Literal["phantom", "solflare"]


class JupiterEngineCore:
    """Wallet-agnostic async wrapper around Phantom/Solflare + JupiterPerpsFlow."""

    def __init__(
        self,
        extension_path: str,
        dapp_url: str,
        *,
        phantom_password: Optional[str] = None,
        solflare_password: Optional[str] = None,
        headless: bool = False,
        wallet_type: WalletType = "phantom"
    ) -> None:
        self.extension_path = extension_path
        self.dapp_url = dapp_url
        self.headless = headless
        self.wallet_type = wallet_type
        self.phantom_password = phantom_password
        self.solflare_password = solflare_password

        self.pm: Optional[PhantomManager | SolflareManager] = None
        self.jp: Optional[JupiterPerpsFlow] = None
        self.page = None

    async def launch(self) -> None:
        """Launch the browser and initialise helpers."""
        if self.wallet_type == "phantom":
            self.pm = PhantomManager(extension_path=self.extension_path, headless=self.headless)
            await self.pm.launch_browser()
            if self.phantom_password:
                await self.pm.unlock_phantom(self.phantom_password)
        elif self.wallet_type == "solflare":
            self.pm = SolflareManager(extension_path=self.extension_path, headless=self.headless)
            await self.pm.launch_browser()
            if self.solflare_password:
                await self.pm.unlock_wallet(self.solflare_password)
        else:
            raise ValueError(f"Unsupported wallet type: {self.wallet_type}")

        self.page = self.pm.page
        self.jp = JupiterPerpsFlow(self.pm)

    async def close(self) -> None:
        if self.pm:
            await self.pm.close()

    async def __aenter__(self) -> JupiterEngineCore:
        await self.launch()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()
