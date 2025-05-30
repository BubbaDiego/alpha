# data_locker/database.py

import sqlite3
import os
from core.core_imports import log
from system.death_nail_service import DeathNailService

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None

    def connect(self):
        if self.conn is None:
            try:
                dir_name = os.path.dirname(self.db_path)
                if dir_name and dir_name.strip() != "":
                    os.makedirs(dir_name, exist_ok=True)

                try:
                    self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
                except sqlite3.DatabaseError as e:
                    if "file is not a database" in str(e) or "database disk image is malformed" in str(e):
                        try:
                            os.remove(self.db_path)
                            wal = f"{self.db_path}-wal"
                            shm = f"{self.db_path}-shm"
                            if os.path.exists(wal):
                                os.remove(wal)
                            if os.path.exists(shm):
                                os.remove(shm)
                        except OSError:
                            pass
                        DeathNailService(log).trigger({
                            "message": "Database corruption detected during connect",
                            "payload": {"error": str(e), "db": self.db_path},
                        })
                        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
                    else:
                        raise

                self.conn.row_factory = sqlite3.Row
                try:
                    self.conn.execute("PRAGMA journal_mode=WAL;")
                except sqlite3.DatabaseError as e:
                    # Handle corruption or non-database files gracefully
                    if "file is not a database" in str(e) or "database disk image is malformed" in str(e):
                        self.conn.close()
                        try:
                            os.remove(self.db_path)
                            wal = f"{self.db_path}-wal"
                            shm = f"{self.db_path}-shm"
                            if os.path.exists(wal):
                                os.remove(wal)
                            if os.path.exists(shm):
                                os.remove(shm)
                        except OSError:
                            pass
                        DeathNailService(log).trigger({
                            "message": "Database corruption detected during connect",
                            "payload": {"error": str(e), "db": self.db_path},
                        })
                        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
                        self.conn.row_factory = sqlite3.Row
                        self.conn.execute("PRAGMA journal_mode=WAL;")
                    else:
                        log.error(f"Failed to set WAL mode: {e}", source="DatabaseManager")
            except Exception as e:
                log.error(f"❌ Failed to connect to database: {e}", source="DatabaseManager")
                self.conn = None
        return self.conn

    def recover_database(self):
        """Recreate the database file if it's corrupt."""
        if self.conn:
            try:
                self.conn.close()
            finally:
                self.conn = None
        DeathNailService(log).trigger({
            "message": "Database recovery triggered",
            "payload": {"db": self.db_path},
        })
        try:
            os.remove(self.db_path)
        except OSError:
            pass
        # Fresh connection will recreate the DB file
        self.connect()

    def get_cursor(self):
        """Return a database cursor, recovering the DB if corruption is detected."""
        try:
            conn = self.connect()
            if conn is None:
                return None
            return conn.cursor()
        except sqlite3.DatabaseError as e:
            if "file is not a database" in str(e) or "database disk image is malformed" in str(e):
                self.recover_database()
                return self.conn.cursor() if self.conn else None
            log.error(f"Failed to get cursor: {e}", source="DatabaseManager")
            return None
        except Exception as e:
            log.error(f"Unexpected cursor error: {e}", source="DatabaseManager")
            return None

    def commit(self):
        try:
            conn = self.connect()
            if conn:
                conn.commit()
        except Exception as e:
            log.error(f"Commit failed: {e}", source="DatabaseManager")

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    # New helper methods
    def list_tables(self) -> list:
        """Return a list of user-defined table names."""
        cursor = self.get_cursor()
        if not cursor:
            return []
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
        return [row[0] for row in cursor.fetchall()]

    def fetch_all(self, table_name: str) -> list:
        """Return all rows from a table as a list of dictionaries."""
        cursor = self.get_cursor()
        if not cursor:
            return []
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        return [dict(r) for r in rows]
