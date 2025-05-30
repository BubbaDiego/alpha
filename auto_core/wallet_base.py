from abc import ABC, abstractmethod
from playwright.sync_api import Page, BrowserContext

class WalletManager(ABC):
    @abstractmethod
    def connect_wallet(self, page: Page, dapp_url: str) -> None:
        """Connect wallet via the dApp interface."""
        pass

    @abstractmethod
    def unlock(self, popup: Page, password: str) -> None:
        """Unlock the wallet using a password."""
        pass

    @abstractmethod
    def approve_transaction(self, page: Page, confirm_selector: str = "text=Confirm") -> None:
        """Approve a transaction popup triggered by the dApp."""
        pass

    @abstractmethod
    def open_popup(self, context: BrowserContext) -> Page:
        """Open the extension popup window."""
        pass

    @abstractmethod
    def handle_onboarding(self, popup: Page) -> None:
        """Handle onboarding for first-time wallet setup."""
        pass

    @abstractmethod
    def handle_wallet_selection(self, popup: Page) -> None:
        """Choose which wallet to use if prompted."""
        pass