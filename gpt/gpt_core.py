
import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from openai import OpenAI

from data.data_locker import DataLocker
from core.constants import DB_PATH
from .create_gpt_context_service import create_gpt_context_service
from oracle_core import OracleCore


class GPTCore:
    """Core utilities for interacting with GPT."""

    def __init__(self, db_path: str = DB_PATH):
        load_dotenv()
        self.logger = logging.getLogger(__name__)
        self.data_locker = DataLocker(str(db_path))
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPEN_AI_KEY")

        if not api_key:
            self.logger.error(
                "OpenAI API key not found in 'OPENAI_API_KEY' or 'OPEN_AI_KEY'"
            )
            raise EnvironmentError(
                "Missing OpenAI API key. Set OPENAI_API_KEY or OPEN_AI_KEY."
            )

        self.client = OpenAI(api_key=api_key)

    def _fetch_snapshots(self) -> Dict[str, Optional[dict]]:
        current = self.data_locker.portfolio.get_latest_snapshot()
        history = self.data_locker.get_portfolio_history()
        previous = history[-2] if len(history) >= 2 else None
        return {"current": current, "previous": previous}

    def build_payload(self, instructions: str = "") -> Dict[str, Any]:
        snaps = self._fetch_snapshots()
        payload = {
            "type": "gpt_analysis_bundle",
            "version": "1.0",
            "generated": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "meta": {
                "type": "meta",
                "version": "1.0",
                "owner": "Geno",
                "strategy": "hedged, automated trading",
                "goal": "optimize exposure while minimizing risk",
                "notes": "Background context",
            },
            "definitions": {
                "type": "definitions",
                "metrics": {
                    "travel_percent": "Defines change from entry to current price",
                    "heat_index": "Composite risk metric",
                },
            },
            "alert_thresholds": {
                "alert_ranges": {
                    "heat_index_ranges": {
                        "enabled": True,
                        "low": 7.0,
                        "medium": 33.0,
                        "high": 66.0,
                    }
                }
            },
            "module_references": {
                "modules": {
                    "PositionCore": {"role": "Manages enrichment, snapshots, sync"},
                    "HedgeCalcServices": {"role": "Suggests hedge rebalancing"},
                }
            },
            "current_snapshot": snaps.get("current"),
            "previous_snapshot": snaps.get("previous"),
            "instructions_for_ai": instructions or "Analyze portfolio risk and improvements",
        }
        return payload

    def analyze(self, instructions: str = "") -> str:
        self.logger.debug("Preparing analysis context for GPT")
        messages = create_gpt_context_service(self, "analysis", instructions)
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo", messages=messages
            )
            reply = response.choices[0].message.content.strip()
            self.logger.debug("Received reply from GPT")
            return reply
        except Exception as e:  # pragma: no cover - depends on OpenAI API
            self.logger.exception(f"GPT analysis failed: {e}")
            return f"Error: {e}"

    def ask_oracle(self, topic: str, strategy_name: Optional[str] = None) -> str:
        """Query GPT for a specific topic using :class:`OracleCore`."""
        if strategy_name in (None, "", "none"):
            strategy_name = None
        oracle = OracleCore(self.data_locker)
        oracle.client = self.client
        try:
            return oracle.ask(topic, strategy_name)
        except Exception as e:  # pragma: no cover - depends on OpenAI API
            self.logger.exception(f"GPT oracle query failed: {e}")
            return f"Error: {e}"

    def ask_gpt_about_portfolio(self) -> str:
        """Backward-compatible wrapper around :meth:`ask_oracle`."""
        return self.ask_oracle("portfolio")

    def ask_gpt_about_alerts(self) -> str:
        """Backward-compatible wrapper around :meth:`ask_oracle`."""
        return self.ask_oracle("alerts")

    def ask_gpt_about_prices(self) -> str:
        """Backward-compatible wrapper around :meth:`ask_oracle`."""
        return self.ask_oracle("prices")

    def ask_gpt_about_system(self) -> str:
        """Backward-compatible wrapper around :meth:`ask_oracle`."""
        return self.ask_oracle("system")

