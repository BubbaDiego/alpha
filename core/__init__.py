# core/__init__.py
"""
Core export hub for Sonic Dashboard.
Keeps high-usage symbols centralized and importable from `core`.
"""

from core.logging import log, configure_console_log
from core.locker_factory import get_locker
from core.constants import DB_PATH, CONFIG_PATH, BASE_DIR
from utils.db_retry import retry_on_locked
__all__ = [
    "log",
    "configure_console_log",
    "get_locker",
    "DB_PATH",
    "CONFIG_PATH",
    "BASE_DIR",
    "retry_on_locked",
    "JsonManager",
]


def __getattr__(name):
    """Lazily import optional utilities to avoid circular imports."""
    if name == "JsonManager":
        from utils.json_manager import JsonManager

        return JsonManager
    raise AttributeError(f"module {__name__} has no attribute {name}")
