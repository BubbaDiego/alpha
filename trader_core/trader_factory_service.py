"""Utility service for creating Trader instances from personas."""

from typing import Optional

from trader.trader import Trader
from .trader_core import TraderCore


class TraderFactoryService:
    """Simple wrapper around TraderCore for factory UIs."""

    def __init__(self, core: TraderCore):
        self.core = core

    def build_trader(self, name: str) -> Optional[Trader]:
        """Create and return a Trader using the provided core."""
        return self.core.create_trader(name)
