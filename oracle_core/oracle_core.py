import json
import os
from typing import Dict, List, Optional

try:
    from openai import OpenAI
except Exception:  # pragma: no cover - optional dependency
    OpenAI = None

from .strategy_manager import StrategyManager, Strategy
from .persona_manager import PersonaManager
from trader.trader_loader import TraderLoader
from .portfolio_topic_handler import PortfolioTopicHandler
from .alerts_topic_handler import AlertsTopicHandler
from .prices_topic_handler import PricesTopicHandler
from .system_topic_handler import SystemTopicHandler
from .positions_topic_handler import PositionsTopicHandler


class OracleCore:
    """Main orchestrator for GPT oracle queries."""

    DEFAULT_SYSTEM_MESSAGES = {
        "portfolio": "You are a portfolio analysis assistant.",
        "alerts": "You summarize alert information.",
        "prices": "You summarize price information.",
        "system": "You report system status.",
        "positions": "You summarize position information.",
    }

    DEFAULT_INSTRUCTIONS = {
        "portfolio": "Provide a portfolio analysis summary.",
        "alerts": "Summarize the current alert state.",
        "prices": "Summarize the market trends.",
        "system": "Summarize the system health status.",
        "positions": "Provide a summary of open positions.",
    }

    def __init__(self, data_locker):
        self.data_locker = data_locker
        if OpenAI:
            api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPEN_AI_KEY") or ""
            self.client = OpenAI(api_key=api_key) if api_key else None
        else:
            self.client = None
        # Load built-in strategies and personas automatically
        self.strategy_manager = StrategyManager()
        self.persona_manager = PersonaManager()
        self.handlers: Dict[str, object] = {}
        self.register_topic_handler("portfolio", PortfolioTopicHandler(data_locker))
        self.register_topic_handler("alerts", AlertsTopicHandler(data_locker))
        self.register_topic_handler("prices", PricesTopicHandler(data_locker))
        self.register_topic_handler("system", SystemTopicHandler(data_locker))
        self.register_topic_handler("positions", PositionsTopicHandler(data_locker))

    # public API
    def register_topic_handler(self, name: str, handler: object):
        self.handlers[name] = handler

    def build_prompt(self, topic: str, context: Dict, instructions: str) -> List[Dict]:
        system_msg = self.DEFAULT_SYSTEM_MESSAGES.get(topic, "You assist the user.")
        return [
            {"role": "system", "content": system_msg},
            {"role": "system", "content": json.dumps(context)},
            {"role": "user", "content": instructions},
        ]

    def query_gpt(self, messages: List[Dict]) -> str:
        if self.client is None:
            raise RuntimeError("OpenAI client not configured")
        response = self.client.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
        return response.choices[0].message.content.strip()

    def _get_context_and_instructions(
        self, topic: str, strategy_name: Optional[str]
    ) -> tuple[Dict, str]:
        """Return the context and instructions for a query."""
        if topic not in self.handlers:
            raise ValueError(f"Unsupported topic: {topic}")
        handler = self.handlers[topic]
        context = handler.get_context()
        instructions = self.DEFAULT_INSTRUCTIONS.get(topic, "Assist the user.")

        if topic == "positions" and not strategy_name:
            try:
                default_strat = self.strategy_manager.get("heat_control")
                context = default_strat.apply(context)
                instructions = default_strat.instructions or instructions
            except KeyError:  # pragma: no cover - defensive
                pass

        if strategy_name:
            try:
                strategy = self.strategy_manager.get(strategy_name)
                context = strategy.apply(context)
                instructions = strategy.instructions or instructions
            except KeyError:
                persona = self.persona_manager.get(strategy_name)
                weighted = [
                    (self.strategy_manager.get(n).modifiers, w)
                    for n, w in persona.strategy_weights.items()
                ]
                merged = Strategy.merge_modifiers(weighted)
                if merged:
                    context = dict(context)
                    context["strategy_modifiers"] = merged
                inst_parts = [persona.instructions] + [
                    self.strategy_manager.get(n).instructions
                    for n in persona.strategy_weights
                ]
                instructions = " ".join(i for i in inst_parts if i) or instructions

        return context, instructions

    def ask(self, topic: str, strategy_name: Optional[str] = None) -> str:
        context, instructions = self._get_context_and_instructions(topic, strategy_name)
        messages = self.build_prompt(topic, context, instructions)
        return self.query_gpt(messages)

    def to_dict(self, topic: str, strategy_name: Optional[str] = None) -> Dict:
        context, instructions = self._get_context_and_instructions(topic, strategy_name)
        messages = self.build_prompt(topic, context, instructions)
        return {"topic": topic, "messages": messages}

    def ask_trader(self, topic: str, trader_name: str) -> str:
        """Query GPT for a trader persona."""
        loader = TraderLoader(self.persona_manager, self.strategy_manager, self.data_locker)
        trader = loader.load_trader(trader_name)
        weighted = [
            (self.strategy_manager.get(n).modifiers, w)
            for n, w in trader.strategies.items()
        ]
        merged = Strategy.merge_modifiers(weighted)
        context = {
            "portfolio": trader.portfolio,
            "positions": trader.positions,
            "strategy_modifiers": merged,
            "mood": trader.mood,
        }
        instructions = self.persona_manager.get(trader_name).instructions or self.DEFAULT_INSTRUCTIONS.get(topic, "Assist the user.")
        messages = self.build_prompt(topic, context, instructions)
        return self.query_gpt(messages)
