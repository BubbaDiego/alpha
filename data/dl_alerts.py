from core.core_imports import log
# dl_alerts.py
"""
Author: BubbaDiego
Module: DLAlertManager
Description:
    Handles creation, retrieval, and deletion of alert records in the SQLite database.
    This module is part of the modular DataLocker architecture and is focused purely
    on alert-related persistence operations.

Dependencies:
    - DatabaseManager from database.py
    - ConsoleLogger from console_logger.py
"""


class DLAlertManager:
    def __init__(self, db):
        self.db = db
        log.debug("DLAlertManager initialized.", source="DLAlertManager")

    def create_alert(self, alert: dict) -> bool:
        try:
            cursor = self.db.get_cursor()
            cursor.execute(
                """
                INSERT INTO alerts (
                    id, created_at, alert_type, alert_class, asset_type,
                    trigger_value, condition, notification_type, level,
                    last_triggered, status, frequency, counter,
                    liquidation_distance, travel_percent, liquidation_price,
                    notes, description, position_reference_id, evaluated_value,
                    position_type
                ) VALUES (
                    :id, :created_at, :alert_type, :alert_class, :asset_type,
                    :trigger_value, :condition, :notification_type, :level,
                    :last_triggered, :status, :frequency, :counter,
                    :liquidation_distance, :travel_percent, :liquidation_price,
                    :notes, :description, :position_reference_id, :evaluated_value,
                    :position_type
                )
                """,
                alert,
            )
            self.db.commit()
            log.success(f"Alert created: {alert['id']}", source="DLAlertManager")
            return True
        except Exception as e:
            log.error(f"Failed to create alert: {e}", source="DLAlertManager")
            return False

    def get_alert(self, alert_id: str) -> dict:
        cursor = self.db.get_cursor()
        cursor.execute("SELECT * FROM alerts WHERE id = ?", (alert_id,))
        row = cursor.fetchone()
        if row:
            log.debug(f"Fetched alert {alert_id}", source="DLAlertManager")
        else:
            log.warning(f"No alert found with ID {alert_id}", source="DLAlertManager")
        return dict(row) if row else {}

    def delete_alert(self, alert_id: str) -> None:
        cursor = self.db.get_cursor()
        cursor.execute("DELETE FROM alerts WHERE id = ?", (alert_id,))
        self.db.commit()
        log.info(f"Deleted alert {alert_id}", source="DLAlertManager")

    def get_all_alerts(self) -> list:
        """
        Retrieves all alert records from the database.
        """
        try:
            cursor = self.db.get_cursor()
            cursor.execute("SELECT * FROM alerts ORDER BY created_at DESC")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            log.error(f"Failed to retrieve all alerts: {e}", source="DLAlertManager")
            return []

    def clear_all_alerts(self) -> None:
        cursor = self.db.get_cursor()
        cursor.execute("DELETE FROM alerts")
        self.db.commit()
        log.success("🧹 All alerts deleted", source="DLAlertManager")

    def delete_all_alerts(self):
        return self.clear_all_alerts()

