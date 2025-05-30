# monitor/monitors/latency_monitor.py

from monitor.base_monitor import BaseMonitor
import requests
from datetime import datetime, timezone

class LatencyMonitor(BaseMonitor):
    """
    Measures HTTP ping latency to key services (e.g., CoinGecko).
    """
    TARGETS = {
        "CoinGecko": "https://api.coingecko.com/api/v3/ping",
        "Jupiter": "https://quote-api.jup.ag/v6/ping"
    }

    def __init__(self):
        super().__init__(name="latency_monitor", ledger_filename="latency_ledger.json")

    def _do_work(self):
        latencies = {}
        for name, url in self.TARGETS.items():
            try:
                start = datetime.now()
                r = requests.get(url, timeout=5)
                r.raise_for_status()
                duration = (datetime.now() - start).total_seconds()
                latencies[name] = round(duration * 1000, 2)  # ms
            except Exception as e:
                latencies[name] = f"ERROR: {e}"
        return latencies
