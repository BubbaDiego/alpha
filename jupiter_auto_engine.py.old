from typing import Optional
from jupiter_core.phantom_manager import PhantomManager
from jupiter_core.jupiter_perps_flow import JupiterPerpsFlow


class JupiterAutoEngine:
    """Minimal automation engine for Jupiter perps demo."""

    def __init__(self, extension_path: str, dapp_url: str, *, phantom_password: Optional[str] = None, headless: bool = False) -> None:
        self.extension_path = extension_path
        self.dapp_url = dapp_url
        self.phantom_password = phantom_password
        self.headless = headless

        self.pm = PhantomManager(extension_path=self.extension_path, headless=self.headless)
        self.pm.launch_browser()
        self.jp = JupiterPerpsFlow(self.pm)

    # ------------------------------------------------------------------
    def step_connect_wallet(self) -> None:
        self.pm.connect_wallet(dapp_url=self.dapp_url, phantom_password=self.phantom_password)

    def step_unlock_wallet(self) -> None:
        if self.phantom_password:
            self.pm.unlock_phantom(self.phantom_password)

    def step_set_position_type(self, position_type: str) -> None:
        self.jp.select_position_type(position_type)

    def step_set_payment_asset(self, asset: str) -> None:
        self.jp.select_payment_asset(asset)

    def step_set_leverage(self, leverage: str) -> None:
        self.jp.set_leverage(leverage)

    def step_set_position_size(self, size: str) -> None:
        self.jp.set_position_size(size)

    def step_switch_to_isolated_margin(self) -> None:
        self.jp.switch_to_isolated_margin()

    def step_approve_transaction(self) -> None:
        self.pm.approve_transaction("text=Confirm")

    def step_capture_order_payload(self, keyword: str):
        return self.pm.capture_order_payload(keyword)
