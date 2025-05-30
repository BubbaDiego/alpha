# dl_system_data.py
"""
Author: BubbaDiego
Module: DLSystemDataManager
Description:
    Manages global system data including theme mode, update timestamps,
    total balances, and strategy performance metadata.
"""

import json
from datetime import datetime
from core.core_imports import log
from data.models import SystemVariables



class DLSystemDataManager:
    def __init__(self, db):
        self.db = db
        log.debug("DLSystemDataManager initialized.", source="DLSystemDataManager")

    # === Theme Mode ===
    def get_theme_mode(self) -> str:
        try:
            cursor = self.db.get_cursor()
            cursor.execute("SELECT theme_mode FROM system_vars WHERE id = 'main'")
            row = cursor.fetchone()
            theme = row["theme_mode"] if row and row["theme_mode"] else "light"
            log.debug(f"Theme mode retrieved: {theme}", source="DLSystemDataManager")
            return theme
        except Exception as e:
            log.error(f"Error fetching theme mode: {e}", source="DLSystemDataManager")
            return "light"

    def set_theme_mode(self, mode: str):
        try:
            cursor = self.db.get_cursor()
            cursor.execute("UPDATE system_vars SET theme_mode = ? WHERE id = 'main'", (mode,))
            self.db.commit()
            log.success(f"Theme mode updated to: {mode}", source="DLSystemDataManager")
        except Exception as e:
            log.error(f"Failed to update theme mode: {e}", source="DLSystemDataManager")

    # === System Vars (timestamps etc) ===
    def get_last_update_times(self) -> SystemVariables:
        cursor = self.db.get_cursor()
        cursor.execute("""
            SELECT last_update_time_positions, last_update_positions_source,
                   last_update_time_prices, last_update_prices_source,
                   last_update_time_jupiter, theme_mode,
                   strategy_start_value, strategy_description
            FROM system_vars
            WHERE id = 'main'
            LIMIT 1
        """)
        row = cursor.fetchone()
        cursor.close()
        return SystemVariables(**dict(row)) if row else SystemVariables()

    def set_last_update_times(self, updates: dict):
        updates.setdefault("last_update_time_jupiter", datetime.now().isoformat())
        updates.setdefault("last_update_jupiter_source", "sync_engine")

        cursor = self.db.get_cursor()
        cursor.execute("""
            UPDATE system_vars
               SET last_update_time_positions = :last_update_time_positions,
                   last_update_positions_source = :last_update_positions_source,
                   last_update_time_prices = :last_update_time_prices,
                   last_update_prices_source = :last_update_prices_source,
                   last_update_time_jupiter = :last_update_time_jupiter,
                   last_update_jupiter_source = :last_update_jupiter_source
               WHERE id = 'main'
        """, updates)
        self.db.commit()
        cursor.close()

    # === Theme Profile Management ===
    def insert_or_update_theme_profile(self, name: str, config: dict):
        try:
            cursor = self.db.get_cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS theme_profiles (
                    name TEXT PRIMARY KEY,
                    config TEXT
                )
            """)
            config_json = json.dumps(config)
            cursor.execute("""
                INSERT INTO theme_profiles (name, config)
                VALUES (?, ?)
                ON CONFLICT(name) DO UPDATE SET config = excluded.config
            """, (name, config_json))
            self.db.commit()
            log.success(f"✅ Theme profile saved: {name}", source="DLSystemDataManager")
        except Exception as e:
            log.error(f"❌ Failed to save theme profile '{name}': {e}", source="DLSystemDataManager")

    def get_theme_profiles(self) -> dict:
        try:
            cursor = self.db.get_cursor()
            rows = cursor.execute("SELECT name, config FROM theme_profiles").fetchall()
            return {row["name"]: json.loads(row["config"]) for row in rows}
        except Exception as e:
            log.error(f"Failed to fetch theme profiles: {e}", source="DLSystemDataManager")
            return {}

    def delete_theme_profile(self, name: str):
        try:
            cursor = self.db.get_cursor()
            cursor.execute("DELETE FROM theme_profiles WHERE name = ?", (name,))
            self.db.commit()
        except Exception as e:
            log.error(f"❌ Failed to delete theme profile '{name}': {e}", source="DLSystemDataManager")

    def set_active_theme_profile(self, name: str):
        try:
            cursor = self.db.get_cursor()
            cursor.execute("UPDATE system_vars SET theme_active_profile = ? WHERE id = 'main'", (name,))
            self.db.commit()
        except Exception as e:
            log.error(f"❌ Failed to set active theme profile '{name}': {e}", source="DLSystemDataManager")

    def get_active_theme_profile(self) -> dict:
        try:
            cursor = self.db.get_cursor()
            row = cursor.execute("SELECT theme_active_profile FROM system_vars WHERE id = 'main'").fetchone()
            if not row or not row["theme_active_profile"]:
                return {}
            active_name = row["theme_active_profile"]
            all_profiles = self.get_theme_profiles()
            return all_profiles.get(active_name, {})
        except Exception as e:
            log.error(f"❌ Failed to retrieve active theme profile: {e}", source="DLSystemDataManager")
            return {}

    def get_var(self, key: str) -> dict:
        try:
            cursor = self.db.get_cursor()
            cursor.execute("SELECT value FROM global_config WHERE key = ?", (key,))
            row = cursor.fetchone()
            if row:
                return json.loads(row["value"])
            return {}
        except Exception as e:
            log.error(f"❌ Failed to read system var '{key}': {e}", source="DLSystemDataManager")
            return {}

    def set_var(self, key: str, value: dict):
        """
        Sets or updates a system-wide variable in the global_config table.
        """
        try:
            cursor = self.db.get_cursor()
            cursor.execute("""
                INSERT INTO global_config (key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """, (key, json.dumps(value)))
            self.db.commit()
            log.success(f"✅ System var set: {key}", source="DLSystemDataManager")
        except Exception as e:
            log.error(f"❌ Failed to set system var '{key}': {e}", source="DLSystemDataManager")

