# dl_hedges.py
"""
Author: BubbaDiego
Module: DLHedgeManager
Description:
    Provides retrieval of hedge data from the database. This manager
    queries positions that have a ``hedge_buddy_id`` set and converts
    them into :class:`~data.models.Hedge` objects using
    :class:`~positions.hedge_manager.HedgeManager`.
"""

from positions.hedge_manager import HedgeManager
from core.core_imports import log


class DLHedgeManager:
    def __init__(self, db):
        self.db = db
        log.debug("DLHedgeManager initialized.", source="DLHedgeManager")

    def get_hedges(self) -> list:
        """Return a list of :class:`Hedge` objects from existing positions."""
        try:
            cursor = self.db.get_cursor()
            cursor.execute(
                "SELECT * FROM positions WHERE hedge_buddy_id IS NOT NULL"
            )
            rows = cursor.fetchall()
            positions = [dict(row) for row in rows]
            hedge_manager = HedgeManager(positions)
            hedges = hedge_manager.get_hedges()
            log.debug(f"Retrieved {len(hedges)} hedges", source="DLHedgeManager")
            return hedges
        except Exception as e:
            log.error(f"Failed to retrieve hedges: {e}", source="DLHedgeManager")
            return []
