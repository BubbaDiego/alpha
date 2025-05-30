import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from datetime import datetime
from core.logging import log




# === Config ===
LOG_DIR = "logs/travel_percent"
os.makedirs(LOG_DIR, exist_ok=True)

def _get_txt_path():
    today = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(LOG_DIR, f"travel_drift_{today}.txt")

def log_travel_percent_comparison(alert_id, jupiter_value, calculated_value, format="txt"):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        variance = abs(jupiter_value - calculated_value)
        percent_diff = (variance / max(abs(jupiter_value), 0.0001)) * 100

        log_line = f"[{timestamp}] Alert: {alert_id} | Jupiter: {jupiter_value:.2f} | Calc: {calculated_value:.2f} | Diff: {percent_diff:.2f}%\n"

        with open(_get_txt_path(), "a") as f:
            f.write(log_line)

    except Exception as e:
        from core.logging import log
        log.error(f"💥 TravelPercent log error: {e}", source="TravelLogger")
