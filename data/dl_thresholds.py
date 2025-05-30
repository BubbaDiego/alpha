# dl_thresholds.py
import os
from core.core_imports import log
from core.constants import CONFIG_DIR
from datetime import datetime, timezone
from data.models import AlertThreshold
from uuid import uuid4
from datetime import datetime
import json

ALERT_THRESHOLDS_JSON_PATH = str(CONFIG_DIR / "alert_thresholds.json")

class DLThresholdManager:
    def __init__(self, db):
        self.db = db
        log.debug("DLThresholdManager initialized.", source="DLThresholdManager")

    def get_all(self) -> list:
        cursor = self.db.get_cursor()
        rows = cursor.execute("SELECT * FROM alert_thresholds ORDER BY alert_type").fetchall()
        return [AlertThreshold(**dict(row)) for row in rows]

    def get_by_type_and_class(self, alert_type: str, alert_class: str, condition: str) -> AlertThreshold:
        cursor = self.db.get_cursor()
        row = cursor.execute("""
            SELECT * FROM alert_thresholds
            WHERE alert_type = ? AND alert_class = ? AND condition = ? AND enabled = 1
            ORDER BY last_modified DESC LIMIT 1
        """, (alert_type, alert_class, condition)).fetchone()
        return AlertThreshold(**dict(row)) if row else None

    def insert(self, threshold: AlertThreshold) -> bool:
        try:
            cursor = self.db.get_cursor()
            cursor.execute("""
                INSERT INTO alert_thresholds (
                    id, alert_type, alert_class, metric_key,
                    condition, low, medium, high, enabled, last_modified
                ) VALUES (
                    :id, :alert_type, :alert_class, :metric_key,
                    :condition, :low, :medium, :high, :enabled, :last_modified
                )
            """, threshold.to_dict())
            self.db.commit()
            self.export_to_json()
            return True
        except Exception as e:
            log.error(f"❌ Failed to insert threshold: {e}", source="DLThresholdManager")
            return False

    def update(self, threshold_id: str, fields: dict):
        try:
            # Sanitize: convert list fields to comma strings
            for k in ['low_notify', 'medium_notify', 'high_notify']:
                if k in fields and isinstance(fields[k], list):
                    fields[k] = ",".join(fields[k])

            # Filter out fields not present in DB schema
            cursor = self.db.get_cursor()
            cols = getattr(self, "_cols", None)
            if cols is None:
                cols = {row[1] for row in cursor.execute("PRAGMA table_info(alert_thresholds)")}
                self._cols = cols
            fields = {k: v for k, v in fields.items() if k in cols}

            # Set last_modified
            fields["last_modified"] = datetime.now(timezone.utc).isoformat()
            fields["id"] = threshold_id

            # Generate SQL SET clause dynamically
            updates = ", ".join(f"{key} = :{key}" for key in fields if key != "id")
            cursor = self.db.get_cursor()
            cursor.execute(f"""
                UPDATE alert_thresholds SET {updates} WHERE id = :id
            """, fields)
            self.db.commit()
            self.export_to_json()
            log.success(f"✅ Threshold {threshold_id} updated", source="DLThresholdManager")
            return True

        except Exception as e:
            log.error(f"❌ Failed to update threshold {threshold_id}: {e}", source="DLThresholdManager")
            return False

    def delete(self, threshold_id: str):
        try:
            cursor = self.db.get_cursor()
            cursor.execute("DELETE FROM alert_thresholds WHERE id = ?", (threshold_id,))
            self.db.commit()
            self.export_to_json()
            return True
        except Exception as e:
            log.error(f"❌ Failed to delete threshold {threshold_id}: {e}", source="DLThresholdManager")
            return False

    def get_by_id(self, threshold_id: str):
        """Return a threshold row by its ID or None."""
        cursor = self.db.get_cursor()
        row = cursor.execute(
            "SELECT * FROM alert_thresholds WHERE id = ?",
            (threshold_id,),
        ).fetchone()
        return AlertThreshold(**dict(row)) if row else None

    def export_to_json(self, path: str = ALERT_THRESHOLDS_JSON_PATH) -> None:
        """Write all thresholds to a JSON file with a source tag."""
        thresholds = self.get_all()
        data = {"source": "db", "thresholds": [t.to_dict() for t in thresholds]}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def import_from_json(self, path: str = ALERT_THRESHOLDS_JSON_PATH) -> int:
        """Import thresholds from JSON file, replacing existing ones."""
        if not os.path.exists(path):
            return 0

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict):
            thresholds = data.get("thresholds", [])
        else:
            thresholds = data

        if not isinstance(thresholds, list):
            return 0

        incoming_ids = {item.get("id") for item in thresholds if item.get("id")}
        existing_ids = {t.id for t in self.get_all()}

        # Remove thresholds that are no longer present
        for obsolete in existing_ids - incoming_ids:
            self.delete(obsolete)

        count = 0
        for item in thresholds:
            tid = item.get("id")
            if not tid:
                continue
            if self.get_by_id(tid):
                self.update(tid, item)
            else:
                self.insert(AlertThreshold(**item))
            count += 1

        self.export_to_json()
        return count
