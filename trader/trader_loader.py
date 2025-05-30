"""Utility to build Trader objects from live data."""

from typing import Optional

import importlib

StrategyManager = importlib.import_module("oracle_core.strategy_manager").StrategyManager
PersonaManager = importlib.import_module("oracle_core.persona_manager").PersonaManager
OracleDataService = importlib.import_module("oracle_core.oracle_data_service").OracleDataService
CalcServices = importlib.import_module("calc_core.calc_services").CalcServices
from .trader import Trader
from .mood_engine import evaluate_mood


class TraderLoader:
    def __init__(
        self,
        persona_manager: Optional[PersonaManager] = None,
        strategy_manager: Optional[StrategyManager] = None,
        data_locker: Optional[object] = None,
    ):
        self.persona_manager = persona_manager or PersonaManager()
        self.strategy_manager = strategy_manager or StrategyManager()
        self.data_service = OracleDataService(data_locker)
        self.data_locker = data_locker

    def load_trader(self, name: str) -> Trader:
        persona = self.persona_manager.get(name)
        wallet_name = persona.name + "Vault"
        wallet_data = None
        if self.data_locker and getattr(self.data_locker, "wallets", None):
            wallet_data = self.data_locker.wallets.get_wallet_by_name(wallet_name)
        positions = self.data_service.fetch_positions() or []
        portfolio = self.data_service.fetch_portfolio() or {}
        totals = CalcServices().calculate_totals(positions)
        avg_heat = totals.get("avg_heat_index", 0.0)
        mood = evaluate_mood(avg_heat, getattr(persona, "moods", {}))
        score = int(100 - abs(avg_heat - 30))
        return Trader(
            name=persona.name,
            avatar=getattr(persona, "avatar", ""),
            persona=getattr(persona, "profile", persona.name),
            origin_story=getattr(persona, "origin_story", ""),
            risk_profile=getattr(persona, "risk_profile", ""),
            mood=mood,
            moods=getattr(persona, "moods", {}),
            strategies=persona.strategy_weights,
            wallet=wallet_data.get("name") if isinstance(wallet_data, dict) else wallet_name,
            portfolio=portfolio,
            positions=positions,
            hedges=[],
            performance_score=score,
            heat_index=avg_heat,
        )
