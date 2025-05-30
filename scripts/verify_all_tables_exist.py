#!/usr/bin/env python3
"""Simple DB schema verifier.

Checks that all required tables exist in the SQLite database and exits
with a non-zero status if any are missing. When executed directly it
returns 0 on success and 1 on failure.
"""
from __future__ import annotations

import sqlite3

from core.constants import DB_PATH

try:  # Optional death signalling
    from system.system_core import SystemCore  # type: ignore
    from data.data_locker import DataLocker  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    SystemCore = None  # type: ignore
    DataLocker = None  # type: ignore


REQUIRED_TABLES = [
    "alerts",
    "alert_thresholds",
    "wallets",
    "brokers",
    "positions",
    "positions_totals_history",
    "modifiers",
    "prices",
    "monitor_heartbeat",
    "global_config",
    "system_vars",
    "monitor_ledger",
]


def verify_all_tables_exist(db_path: str = str(DB_PATH)) -> int:
    """Return ``0`` if all required tables exist, else ``1``."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing = {row[0] for row in cursor.fetchall()}

    missing = []
    for table in REQUIRED_TABLES:
        if table in existing:
            print(f"✅ {table}")
        else:
            print(f"❌ {table}")
            missing.append(table)

    if missing:
        msg = f"FATAL: Missing required tables → {', '.join(missing)}"
        print(msg)
        if SystemCore and DataLocker:
            try:
                core = SystemCore(DataLocker(db_path))
                core.death({"missing_tables": missing})
            except Exception as exc:  # pragma: no cover - best effort
                print(f"⚠️ SystemCore.death failed: {exc}")
        return 1

    print("✅ All required tables exist")
    return 0


if __name__ == "__main__":
    raise SystemExit(verify_all_tables_exist())
