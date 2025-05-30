import os
import json
from pathlib import Path
from config.config_loader import load_config, update_config
from core.constants import ALERT_THRESHOLDS_PATH, CONFIG_DIR
from core.core_imports import log


def save_config(filename: str, data: dict) -> None:
    """Save ``data`` to ``filename`` resolving default locations."""
    path = Path(filename)
    if path.name == "alert_thresholds.json":
        path = ALERT_THRESHOLDS_PATH
    elif not path.is_absolute():
        path = CONFIG_DIR / path
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    log.info(f"✅ [ConfigLoader] Saved config to: {path}", source="ConfigLoader")
