"""Simple in-memory store for Trader objects."""

from typing import Dict, List, Optional

from trader.trader import Trader


class TraderStore:
    """Provide basic persistence for Trader metadata."""

    def __init__(self):
        self._store: Dict[str, Trader] = {}

    def save(self, trader: Trader) -> bool:
        self._store[trader.name] = trader
        return True

    def get(self, name: str) -> Optional[Trader]:
        return self._store.get(name)

    def list(self) -> List[Trader]:
        return list(self._store.values())

    def delete(self, name: str) -> bool:
        return self._store.pop(name, None) is not None
