"""Seed default data into the SQLite database.

This script ensures the database schema is initialized and then
inserts the default alert thresholds defined in :mod:`data.threshold_seeder`.
Run from the project root:

    python -m data.seed_database
"""



# Allow running this file directly.


from core.core_imports import configure_console_log
from core.constants import DB_PATH
from data.data_locker import DataLocker
from data.threshold_seeder import AlertThresholdSeeder


def seed_database():
    """Bootstrap database tables and seed default alert thresholds."""
    configure_console_log()
    dl = DataLocker(str(DB_PATH))
    seeder = AlertThresholdSeeder(dl.db)
    created, updated = seeder.seed_all()
    print(f"✅ Seed complete → {created} created, {updated} updated.")
    dl.close()


if __name__ == "__main__":
    seed_database()
