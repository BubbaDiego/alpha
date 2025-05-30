"""JupiterService
===============
Utility wrapper for interacting with Jupiter Perpetuals API.
"""
from __future__ import annotations

try:
    import requests
except Exception:  # pragma: no cover - optional dependency
    requests = None

from core.logging import log
from core.constants import JUPITER_API_BASE


class JupiterService:
    """Simple HTTP client for Jupiter collateral endpoints."""

    def __init__(self, api_base: str = JUPITER_API_BASE):
        self.api_base = api_base.rstrip("/")

    def increase_position(self, wallet: str, market: str, collateral_delta: float) -> dict:
        """Call Jupiter's increasePosition endpoint."""
        url = f"{self.api_base}/v1/increase_position"
        payload = {
            "wallet": wallet,
            "market": market,
            "collateral_delta": collateral_delta,
            "size_usd_delta": 0,
        }
        log.debug(f"POST {url} {payload}", source="JupiterService")
        if not requests:
            log.debug("HTTP client unavailable; skipping API call", source="JupiterService")
            return {}
        try:
            res = requests.post(url, json=payload, timeout=10)
            res.raise_for_status()
            return res.json()
        except Exception as exc:  # pragma: no cover - network failures
            log.error(f"IncreasePosition failed: {exc}", source="JupiterService")
            raise

    def decrease_position(self, wallet: str, market: str, collateral_delta: float) -> dict:
        """Call Jupiter's decreasePosition endpoint."""
        url = f"{self.api_base}/v1/decrease_position"
        payload = {
            "wallet": wallet,
            "market": market,
            "collateral_delta": collateral_delta,
            "size_usd_delta": 0,
        }
        log.debug(f"POST {url} {payload}", source="JupiterService")
        if not requests:
            log.debug("HTTP client unavailable; skipping API call", source="JupiterService")
            return {}
        try:
            res = requests.post(url, json=payload, timeout=10)
            res.raise_for_status()
            return res.json()
        except Exception as exc:  # pragma: no cover - network failures
            log.error(f"DecreasePosition failed: {exc}", source="JupiterService")
            raise
