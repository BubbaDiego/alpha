import json
import os
from pathlib import Path
from core.core_imports import ALERT_THRESHOLDS_PATH, log
from core.locker_factory import get_locker
from typing import Optional


def _deep_merge(base: dict, overrides: dict) -> dict:
    """Recursively merge ``overrides`` into ``base`` returning a new dict."""
    result = dict(base)
    for key, value in overrides.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result

def load_config(filename=None):
    """Load alert configuration.

    If ``filename`` is provided, the JSON file at that path is loaded.
    Otherwise the configuration is read from the ``global_config`` table
    via :func:`~data.dl_system_data.DLSystemDataManager.get_var` using the
    ``"alert_thresholds"`` key.
    """

    if filename:
        if not os.path.isabs(filename):
            filename = os.path.abspath(filename)

        if os.path.exists(filename):
            log.info(
                f"✅ [ConfigLoader] Loading config from: {filename}",
                source="ConfigLoader",
            )
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)

        log.error(
            f"❌ [ConfigLoader] Config not found at: {filename}",
            source="ConfigLoader",
        )
        return {}

    # Default: load from database
    locker = get_locker()
    config = locker.system.get_var("alert_thresholds") or {}
    log.info("✅ [ConfigLoader] Loaded config from DB", source="ConfigLoader")
    return config


def update_config(new_config: dict, filename: Optional[str] = None) -> dict:
    """Merge ``new_config`` into the existing config and persist the result."""

    if filename:
        filename = (
            str(ALERT_THRESHOLDS_PATH)
            if Path(filename).name == "alert_thresholds.json"
            else os.path.abspath(filename)
        )

        current = load_config(filename)
        merged = _deep_merge(current, new_config)
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(merged, f, indent=2)
        return merged

    # Default: update database entry
    locker = get_locker()
    current = locker.system.get_var("alert_thresholds") or {}
    merged = _deep_merge(current, new_config)
    locker.system.set_var("alert_thresholds", merged)
    return merged




