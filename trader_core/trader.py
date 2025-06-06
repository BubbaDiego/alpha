from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class Trader:
    """Unified trading persona and portfolio snapshot."""

    name: str
    avatar: str = ""
    persona: str = ""
    origin_story: str = ""
    risk_profile: str = ""
    born_on: str = ""
    initial_collateral: float = 0.0
    mood: str = "neutral"
    moods: Dict[str, str] = field(default_factory=dict)
    strategies: Dict[str, float] = field(default_factory=dict)
    wallet: str = ""
    wallet_balance: float = 0.0
    profit: float = 0.0
    portfolio: Dict = field(default_factory=dict)
    positions: List[Dict] = field(default_factory=list)
    hedges: List[Dict] = field(default_factory=list)
    performance_score: int = 0
    heat_index: float = 0.0

    def __repr__(self) -> str:
        return (
            f"Trader(name={self.name!r}, persona={self.persona!r}, mood={self.mood!r}, "
            f"born_on={self.born_on!r}, initial_collateral={self.initial_collateral}, "
            f"heat_index={self.heat_index}, wallet_balance={self.wallet_balance}, profit={self.profit})"
        )
