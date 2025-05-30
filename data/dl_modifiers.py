import json
from datetime import datetime
from core.logging import log

class DLModifierManager:
    def __init__(self, db):
        self.db = db
        log.debug("DLModifierManager initialized.", source="DLModifierManager")

    def ensure_table(self):
        cursor = self.db.get_cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS modifiers (
                key TEXT PRIMARY KEY,
                group_name TEXT NOT NULL,
                value REAL NOT NULL,
                last_modified TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.db.commit()
        log.debug("modifiers table ensured", source="DLModifierManager")

    def set_modifier(self, key: str, value: float, group: str = "heat_modifiers"):
        cursor = self.db.get_cursor()
        cursor.execute("""
            INSERT INTO modifiers (key, group_name, value, last_modified)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value, last_modified = excluded.last_modified
        """, (key, group, value, datetime.now().isoformat()))
        self.db.commit()
        log.success(f"✅ Modifier set: {key} = {value}", source="DLModifierManager")

    def get_modifier(self, key: str) -> float:
        cursor = self.db.get_cursor()
        row = cursor.execute("SELECT value FROM modifiers WHERE key = ?", (key,)).fetchone()
        return float(row["value"]) if row else None

    def get_all_modifiers(self, group: str = None) -> dict:
        cursor = self.db.get_cursor()
        if group:
            rows = cursor.execute("SELECT key, value FROM modifiers WHERE group_name = ?", (group,)).fetchall()
        else:
            rows = cursor.execute("SELECT key, value FROM modifiers", ()).fetchall()
        return {row["key"]: float(row["value"]) for row in rows}

    def export_to_json(self) -> str:
        cursor = self.db.get_cursor()
        rows = cursor.execute("SELECT group_name, key, value FROM modifiers").fetchall()
        grouped = {}
        for row in rows:
            group = row["group_name"]
            grouped.setdefault(group, {})[row["key"]] = float(row["value"])
        return json.dumps(grouped, indent=2)

    def import_from_json(self, json_data: str):
        data = json.loads(json_data)
        for group, modifiers in data.items():
            for key, value in modifiers.items():
                self.set_modifier(key, float(value), group=group)
        log.success("📦 Modifiers imported from JSON", source="DLModifierManager")
