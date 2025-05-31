"""JupiterTriggerService
=====================
HTTP client for interacting with Jupiter Perpetuals trigger order API.
"""
from __future__ import annotations

try:
    import requests
except Exception:  # pragma: no cover - optional dependency
    requests = None

from core.logging import log
from core.constants import JUPITER_API_BASE


class JupiterTriggerService:
    """Wrapper around Jupiter trigger order endpoints."""

    def __init__(self, api_base: str = JUPITER_API_BASE):
        self.api_base = api_base.rstrip("/")

    # --------------------------------------------------------------
    def create_trigger_order(
        self,
        wallet: str,
        market: str,
        trigger_price: float,
        size: float,
        is_long: bool,
    ) -> dict:
        """Create a new trigger order."""
        url = f"{self.api_base}/v1/create_trigger_order"
        payload = {
            "wallet": wallet,
            "market": market,
            "trigger_price": trigger_price,
            "size": size,
            "is_long": is_long,
        }
        log.debug(f"POST {url} {payload}", source="JupiterTriggerService")
        if not requests:
            log.debug(
                "HTTP client unavailable; skipping API call",
                source="JupiterTriggerService",
            )
            return {}
        try:
            res = requests.post(url, json=payload, timeout=10)
            res.raise_for_status()
            return res.json()
        except Exception as exc:  # pragma: no cover - network failures
            log.error(f"CreateTriggerOrder failed: {exc}", source="JupiterTriggerService")
            raise

    # --------------------------------------------------------------
    def cancel_trigger_order(self, wallet: str, order_id: str) -> dict:
        """Cancel an existing trigger order."""
        url = f"{self.api_base}/v1/cancel_trigger_order"
        payload = {"wallet": wallet, "order_id": order_id}
        log.debug(f"POST {url} {payload}", source="JupiterTriggerService")
        if not requests:
            log.debug(
                "HTTP client unavailable; skipping API call",
                source="JupiterTriggerService",
            )
            return {}
        try:
            res = requests.post(url, json=payload, timeout=10)
            res.raise_for_status()
            return res.json()
        except Exception as exc:  # pragma: no cover - network failures
            log.error(f"CancelTriggerOrder failed: {exc}", source="JupiterTriggerService")
            raise

    # --------------------------------------------------------------
    def get_trigger_orders(self, wallet: str) -> dict:
        """Return all trigger orders for ``wallet``."""
        url = f"{self.api_base}/v1/trigger_orders"
        params = {"wallet": wallet}
        log.debug(f"GET {url} {params}", source="JupiterTriggerService")
        if not requests:
            log.debug(
                "HTTP client unavailable; skipping API call",
                source="JupiterTriggerService",
            )
            return {}
        try:
            res = requests.get(url, params=params, timeout=10)
            res.raise_for_status()
            return res.json()
        except Exception as exc:  # pragma: no cover - network failures
            log.error(f"GetTriggerOrders failed: {exc}", source="JupiterTriggerService")
            raise

