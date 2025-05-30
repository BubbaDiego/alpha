import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from datetime import datetime
from data.models import AlertThreshold
from data.dl_thresholds import DLThresholdManager
from core.logging import log


class ThresholdService:
    def __init__(self, db):
        self.repo = DLThresholdManager(db)  # 🔌 Inject DL layer (not raw DB access)

    def get_thresholds(self, alert_type: str, alert_class: str, condition: str) -> AlertThreshold:
        threshold = self.repo.get_by_type_and_class(alert_type, alert_class, condition)
        if not threshold:
            log.warning(f"⚠️ No threshold match: {alert_type}/{alert_class}/{condition}", source="ThresholdService")
        return threshold

    def create_threshold(self, threshold: AlertThreshold) -> bool:
        try:
            if not threshold.id:
                threshold.id = str(uuid4())
            return self.repo.insert(threshold)
        except Exception as e:
            log.error(f"❌ Failed to create threshold: {e}", source="ThresholdService")
            return False

    def update_threshold(self, threshold_id: str, updates: dict) -> bool:
        try:
            return self.repo.update(threshold_id, updates)
        except Exception as e:
            log.error(f"❌ Failed to update threshold {threshold_id}: {e}", source="ThresholdService")
            return False

    def delete_threshold(self, threshold_id: str) -> bool:
        try:
            return self.repo.delete(threshold_id)
        except Exception as e:
            log.error(f"❌ Failed to delete threshold {threshold_id}: {e}", source="ThresholdService")
            return False

    def list_all_thresholds(self) -> list:
        try:
            return self.repo.get_all()
        except Exception as e:
            log.error(f"❌ Failed to list thresholds: {e}", source="ThresholdService")
            return []
