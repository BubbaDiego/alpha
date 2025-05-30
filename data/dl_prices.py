# dl_prices.py
from uuid import uuid4
from datetime import datetime
from core.core_imports import log

class DLPriceManager:
    def __init__(self, db):
        self.db = db
        log.debug("DLPriceManager initialized.", source="DLPriceManager")

    def insert_price(self, price_data: dict):
        try:
            cursor = self.db.get_cursor()
            if "id" not in price_data:
                price_data["id"] = str(uuid4())
            if "last_update_time" not in price_data:
                price_data["last_update_time"] = datetime.now().isoformat()

            cursor.execute("""
                INSERT INTO prices (
                    id, asset_type, current_price, previous_price,
                    last_update_time, previous_update_time, source
                ) VALUES (
                    :id, :asset_type, :current_price, :previous_price,
                    :last_update_time, :previous_update_time, :source
                )
            """, price_data)

            self.db.commit()
            log.success(f"Inserted price for {price_data['asset_type']}", source="DLPriceManager")
        except Exception as e:
            log.error(f"Failed to insert price: {e}", source="DLPriceManager")

    def get_latest_price(self, asset_type: str) -> dict:
        try:
            cursor = self.db.get_cursor()
            cursor.execute("""
                SELECT * FROM prices
                WHERE asset_type = ?
                ORDER BY last_update_time DESC
                LIMIT 1
            """, (asset_type,))
            row = cursor.fetchone()
            return dict(row) if row else {}
        except Exception as e:
            log.error(f"Error retrieving price for {asset_type}: {e}", source="DLPriceManager")
            return {}

    def get_all_prices(self) -> list:
        try:
            cursor = self.db.get_cursor()
            cursor.execute("SELECT * FROM prices ORDER BY last_update_time DESC")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            log.error(f"Failed to retrieve all prices: {e}", source="DLPriceManager")
            return []

    def clear_prices(self):
        try:
            cursor = self.db.get_cursor()
            cursor.execute("DELETE FROM prices")
            self.db.commit()
            log.warning("🧹 All price entries cleared.", source="DLPriceManager")
        except Exception as e:
            log.error(f"Failed to clear prices: {e}", source="DLPriceManager")

