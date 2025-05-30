#!/usr/bin/env python3
"""Initialize or reset the SQLite database and seed optional default data.

This tool consolidates the various seeder scripts. By default it simply
ensures the database exists and all tables are created.

Examples:
    # Create tables only
    python scripts/initialize_database.py

    # Reset the database then seed thresholds and wallets
    python scripts/initialize_database.py --reset --seed-wallets --seed-thresholds

    # Run every initialization task
    python scripts/initialize_database.py --all
"""
from __future__ import annotations

import argparse
import json
import os

from core.constants import DB_PATH, BASE_DIR
from core.core_imports import configure_console_log
from data.data_locker import DataLocker
from data.reset_database import reset_database
from data.threshold_seeder import AlertThresholdSeeder
from typing import List, Optional


def seed_wallets(locker: DataLocker) -> None:
    """Seed wallets from ``wallets.json`` if present."""
    json_path = os.path.join(BASE_DIR, "wallets.json")
    if not os.path.exists(json_path):
        print(f"⚠️ wallets.json not found at {json_path}")
        return
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            wallets = json.load(f)
        for w in wallets:
            try:
                locker.wallets.create_wallet(w)
                print(f"✅ Inserted wallet: {w.get('name')}")
            except Exception as e:  # pragma: no cover - best effort
                print(f"❌ Failed to insert {w.get('name')}: {e}")
    except Exception as e:  # pragma: no cover - best effort
        print(f"❌ Wallet seeding failed: {e}")


def seed_thresholds(locker: DataLocker) -> None:
    """Populate default alert thresholds."""
    seeder = AlertThresholdSeeder(locker.db)
    created, updated = seeder.seed_all()
    print(f"✅ Thresholds seeded → {created} created, {updated} updated")


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Database initialization helper")
    parser.add_argument("--reset", action="store_true", help="Delete the existing database before creating tables")
    parser.add_argument("--seed-wallets", action="store_true", help="Seed wallets from wallets.json")
    parser.add_argument("--seed-thresholds", action="store_true", help="Seed default alert thresholds")
    parser.add_argument("--seed-modifiers", action="store_true", help="Seed modifiers from sonic_sauce.json")
    parser.add_argument("--all", action="store_true", help="Run all seeding tasks after initialization")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    configure_console_log()

    if args.reset:
        reset_database(str(DB_PATH))

    locker = DataLocker(str(DB_PATH))

    if args.all:
        args.seed_wallets = True
        args.seed_thresholds = True
        args.seed_modifiers = True

    if args.seed_modifiers:
        locker._seed_modifiers_if_empty()
    if args.seed_wallets:
        seed_wallets(locker)
    if args.seed_thresholds:
        seed_thresholds(locker)

    locker.close()
    print(f"✅ Database initialized at: {DB_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
