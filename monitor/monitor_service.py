# monitor/core/monitor_service.py

import subprocess
import requests
from datetime import datetime
from core.core_imports import log

class MonitorService:
    def fetch_prices(self):
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {"ids": "bitcoin,ethereum,solana", "vs_currencies": "usd"}
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return {
                "BTC": data.get("bitcoin", {}).get("usd"),
                "ETH": data.get("ethereum", {}).get("usd"),
                "SOL": data.get("solana", {}).get("usd"),
            }
        except Exception as e:
            log.error(f"[PriceFetch] failed: {e}")
            return {}

    def run_post_tests(self, test_path="tests/test_alert_controller.py"):
        result = subprocess.run(
            ["pytest", test_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout.decode(),
            "stderr": result.stderr.decode(),
            "timestamp": datetime.utcnow().isoformat()
        }

    def check_xcom(self):
        return {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Stubbed XCOM check passed"
        }
