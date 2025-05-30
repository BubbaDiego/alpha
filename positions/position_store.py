# positions/position_store.py

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from positions.position_enrichment_service import validate_enriched_position
from core.core_imports import log
from uuid import uuid4
from datetime import datetime

class PositionStore:
    def __init__(self, data_locker):
        self.dl = data_locker

    def get_all(self) -> list:
        try:
            rows = self.dl.positions.get_all_positions()
            log.success(f"✅ Loaded {len(rows)} positions", source="PositionStore")
            return rows
        except Exception as e:
            log.error(f"❌ Failed to load positions: {e}", source="PositionStore")
            return []

    def get_all_positions(self):
        return self.get_all()

    def get_active_positions(self) -> list:
        try:
            cursor = self.dl.db.get_cursor()  # ✅ FIXED: Use DataLocker’s db
            cursor.execute("SELECT * FROM positions WHERE status = 'ACTIVE'")
            rows = cursor.fetchall()
            log.debug(f"📊 Pulled {len(rows)} ACTIVE positions", source="PositionStore")
            return [dict(row) for row in rows]
        except Exception as e:
            log.error(f"❌ Failed to get active positions: {e}", source="PositionStore")
            return []

    def get_by_id(self, pos_id: str) -> dict:
        return self.dl.positions.get_position_by_id(pos_id)

    def insert(self, position: dict) -> bool:
        try:
            position.setdefault("id", str(uuid4()))
            position.setdefault("last_updated", datetime.now().isoformat())
            self.dl.positions.create_position(position)
            log.success(f"📝 Inserted position {position['id']}", source="PositionStore")
            return True
        except Exception as e:
            log.error(f"❌ Insert failed: {e}", source="PositionStore")
            return False

    def delete(self, pos_id: str) -> bool:
        try:
            self.dl.positions.delete_position(pos_id)
            log.success(f"🗑 Deleted position {pos_id}", source="PositionStore")
            return True
        except Exception as e:
            log.error(f"❌ Failed to delete {pos_id}: {e}", source="PositionStore")
            return False

    def delete_all(self):
        try:
            self.dl.positions.delete_all_positions()
            log.success("🧹 All positions cleared", source="PositionStore")
        except Exception as e:
            log.error(f"❌ Failed to delete all positions: {e}", source="PositionStore")
