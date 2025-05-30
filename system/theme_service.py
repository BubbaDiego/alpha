import sys
import os
import json
from core.logging import log
from core.constants import THEME_CONFIG_PATH  # Optional fallback path

class ThemeService:
    def __init__(self, data_locker, config_path=THEME_CONFIG_PATH):
        self.dl = data_locker
        self.config_path = config_path
        self.logger = log

    # 🌗 Theme mode (light/dark)
    def get_theme_mode(self) -> str:
        try:
            return self.dl.system.get_theme_mode()
        except Exception as e:
            self.logger.warn(f"Failed to get theme mode: {e}", source="ThemeService")
            return "light"

    def set_theme_mode(self, mode: str):
        try:
            current_mode = self.get_theme_mode()
            if current_mode == mode:
                self.logger.debug(f"Theme mode already '{mode}', skipping update.", source="ThemeService")
                return
            self.dl.system.set_theme_mode(mode)
            self.logger.info(f"Theme mode set to {mode}", source="ThemeService")
        except Exception as e:
            self.logger.error(f"Failed to set theme mode: {e}", source="ThemeService")
            raise

    # === Legacy JSON support (optional fallback) ===
    def load_theme_config(self) -> dict:
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r") as f:
                    return json.load(f)
            return {}
        except Exception as e:
            self.logger.error(f"Error loading theme config: {e}")
            return {}

    def save_theme_config(self, config: dict):
        try:
            with open(self.config_path, "w") as f:
                json.dump(config, f, indent=2)
            self.logger.success("Theme config saved.")
        except Exception as e:
            self.logger.error(f"Failed to save theme config: {e}")
            raise

    # === 🧠 Dynamic Theme Profiles (DB-based) ===

    def get_all_profiles(self) -> dict:
        try:
            return self.dl.system.get_theme_profiles()
        except Exception as e:
            self.logger.error(f"Failed to load profiles: {e}", source="ThemeService")
            return {}

    def save_profile(self, name: str, config: dict):
        try:
            self.dl.system.insert_or_update_theme_profile(name, config)
            self.logger.success(f"Theme profile '{name}' saved.")
        except Exception as e:
            self.logger.error(f"Failed to save profile '{name}': {e}")
            raise

    def delete_profile(self, name: str):
        try:
            self.dl.system.delete_theme_profile(name)
            self.logger.info(f"Deleted theme profile '{name}'")
        except Exception as e:
            self.logger.error(f"Error deleting profile '{name}': {e}")

    def set_active_profile(self, name: str):
        try:
            self.dl.system.set_active_theme_profile(name)
            self.logger.success(f"Theme profile '{name}' set as active")
        except Exception as e:
            self.logger.error(f"Error activating profile '{name}': {e}")
            raise

    def get_active_profile(self) -> dict:
        try:
            return self.dl.system.get_active_theme_profile()
        except Exception as e:
            self.logger.error(f"Failed to get active profile: {e}")
            return {}
