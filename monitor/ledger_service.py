import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import os
import json
from datetime import datetime, timezone
from core.logging import log

class LedgerService:
    def __init__(self, ledger_dir="monitor"):
        self.ledger_dir = os.path.abspath(ledger_dir)
        os.makedirs(self.ledger_dir, exist_ok=True)

    def _get_path(self, filename: str) -> str:
        return os.path.join(self.ledger_dir, filename)

    def write_entry(self, filename: str, entry: dict):
        """Append a JSON line to a ledger file."""
        path = self._get_path(filename)
        try:
            with open(path, 'a', encoding='utf-8') as f:
                json.dump(entry, f)
                f.write("\n")
            log.success(f"Ledger write: {filename}", source="LedgerService")
        except Exception as e:
            log.error(f"Ledger write error: {e}", source="LedgerService")

    def read_last_entry(self, filename: str) -> dict:
        """Return the last JSON object from a ledger file."""
        path = self._get_path(filename)
        try:
            if not os.path.exists(path):
                return {}

            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if not lines:
                    return {}

                return json.loads(lines[-1])
        except Exception as e:
            log.error(f"Ledger read error: {e}", source="LedgerService")
            return {}

    def get_status(self, monitor_name: str) -> dict:
        filename = f"{monitor_name}_ledger.json"
        entry = self.read_last_entry(filename)
        if not entry or not entry.get("timestamp"):
            return {"age_seconds": 9999, "last_timestamp": None}

        try:
            last_ts = datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            age = (now - last_ts).total_seconds()
            return {
                "last_timestamp": last_ts.isoformat(),
                "age_seconds": round(age),
                "status": entry.get("status")
            }
        except Exception as e:
            print(f"[ERROR] Timestamp parse failed for {monitor_name}: {e}")
            return {"age_seconds": 9999, "last_timestamp": None}
