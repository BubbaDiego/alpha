"""Oracle core package."""

from .strategy_manager import StrategyManager, Strategy
from .persona_manager import PersonaManager, Persona
from .oracle_data_service import OracleDataService
from .portfolio_topic_handler import PortfolioTopicHandler
from .alerts_topic_handler import AlertsTopicHandler
from .prices_topic_handler import PricesTopicHandler
from .system_topic_handler import SystemTopicHandler
from .positions_topic_handler import PositionsTopicHandler

__all__ = [
    "StrategyManager",
    "Strategy",
    "PersonaManager",
    "Persona",
    "OracleDataService",
    "PortfolioTopicHandler",
    "AlertsTopicHandler",
    "PricesTopicHandler",
    "SystemTopicHandler",
    "PositionsTopicHandler",
    "OracleCore",
]


def __getattr__(name):
    if name == "OracleCore":
        from .oracle_core import OracleCore
        return OracleCore
    raise AttributeError(name)
