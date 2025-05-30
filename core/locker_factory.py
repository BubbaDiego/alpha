
from core.constants import DB_PATH
from core.logging import log

_locker_instance = None


def get_locker(db_override=None):
    """
    Lazily import DataLocker to avoid circular import.
    Allows optional override of DB path.
    """
    global _locker_instance
    from data.data_locker import DataLocker

    selected_path = str(db_override or DB_PATH)
    log.info(f"🔐 get_locker() → DB Path in use: {selected_path}", source="LockerFactory")

    if _locker_instance is None:
        _locker_instance = DataLocker(selected_path)
        log.success(f"🧠 DataLocker instantiated at {selected_path}", source="LockerFactory")

    return _locker_instance

