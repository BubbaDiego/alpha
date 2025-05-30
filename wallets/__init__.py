"""Wallet domain package."""

__all__ = ["WalletService", "WalletCore"]


def __getattr__(name):
    """Lazily provide access to heavy modules to avoid circular imports."""
    if name == "WalletService":
        from .wallet_service import WalletService as svc
        return svc
    if name == "WalletCore":
        from .wallet_core import WalletCore as core
        return core
    raise AttributeError(name)



