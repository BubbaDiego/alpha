"""
hedge_manager.py

This module defines the HedgeManager class which is responsible for:
  - Scanning positions for hedge links (via hedge_buddy_id).
  - Creating Hedge instances that represent grouped positions.
  - Aggregating metrics such as total long size, total short size, long/short heat indices,
    and total heat index.
  - Providing access to hedge data via methods like get_hedges().
  - Logging operations using ConsoleLogger.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from typing import List, Optional, TYPE_CHECKING

# Avoid circular import at runtime; only import DataLocker when type checking or
# inside methods.
if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from data.data_locker import DataLocker
from data.models import Hedge
from core.core_imports import DB_PATH
from hedge_core.hedge_core import HedgeCore


class HedgeManager:
    """Backwards compatible wrapper around :class:`HedgeCore`."""

    def __init__(self, positions: Optional[List[dict]] = None, data_locker: "DataLocker" = None):
        if data_locker is None:
            from data.data_locker import DataLocker as _DataLocker
            data_locker = _DataLocker(str(DB_PATH))
        self.dl = data_locker
        self.core = HedgeCore(self.dl)
        self.positions = positions if positions is not None else []
        self.hedges: List[Hedge] = []
        if positions is not None:
            self.build_hedges()

    def build_hedges(self):
        self.hedges = self.core.build_hedges(self.positions)

    def update_positions(self, positions: List[dict]):
        self.positions = positions
        self.build_hedges()

    def get_hedges(self) -> List[Hedge]:
        return self.hedges

    @staticmethod
    def find_hedges(db_path: str = DB_PATH) -> List[list]:
        from data.data_locker import DataLocker as _DataLocker
        dl = _DataLocker(str(db_path))
        core = HedgeCore(dl)
        return core.link_hedges()

    @staticmethod
    def clear_hedge_data(db_path: str = DB_PATH) -> None:
        from data.data_locker import DataLocker as _DataLocker
        dl = _DataLocker(str(db_path))
        core = HedgeCore(dl)
        core.unlink_hedges()

