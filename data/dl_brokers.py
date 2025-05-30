from core.core_imports import log
# dl_brokers.py
"""
Author: BubbaDiego
Module: DLBrokerManager
Description:
    Handles broker (exchange/platform) storage operations. Includes creation,
    reading, updating, and deletion of broker records.

Dependencies:
    - DatabaseManager from database.py
    - ConsoleLogger from console_logger.py
"""


class DLBrokerManager:
    def __init__(self, db):
        self.db = db
        log.debug("DLBrokerManager initialized.", source="DLBrokerManager")

    def create_broker(self, broker: dict):
        try:
            cursor = self.db.get_cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO brokers (
                    name, image_path, web_address, total_holding
                ) VALUES (?, ?, ?, ?)
            """, (
                broker["name"],
                broker.get("image_path", ""),
                broker.get("web_address", ""),
                broker.get("total_holding", 0.0)
            ))
            self.db.commit()
            log.success(f"Broker created: {broker['name']}", source="DLBrokerManager")
        except Exception as e:
            log.error(f"Failed to create broker: {e}", source="DLBrokerManager")

    def get_brokers(self) -> list:
        try:
            cursor = self.db.get_cursor()
            cursor.execute("SELECT * FROM brokers")
            brokers = [dict(row) for row in cursor.fetchall()]
            log.debug(f"Retrieved {len(brokers)} brokers", source="DLBrokerManager")
            return brokers
        except Exception as e:
            log.error(f"Failed to fetch brokers: {e}", source="DLBrokerManager")
            return []
