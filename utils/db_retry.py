# utils/db_retry.py or inside your database.py
import sqlite3
import time
from functools import wraps

def retry_on_locked(retries=3, delay=0.25):
    """
    Retries a SQLite operation if 'database is locked' occurs.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except sqlite3.OperationalError as e:
                    if "database is locked" in str(e):
                        time.sleep(delay)
                    else:
                        raise
            raise sqlite3.OperationalError(f"[retry_on_locked] Max retries reached for {func.__name__}")
        return wrapper
    return decorator
