# order_core/order_model.py

from dataclasses import dataclass
from typing import Optional


@dataclass
class OrderModel:
    """
    Internal representation of a trading order constructed by the OrderEngine.
    Can be passed to brokers, exported to DB, or used in summaries.
    """
    id: str                          # Unique identifier (can be generated later)
    asset: str                       # e.g., SOL, ETH
    position_type: str              # "long" or "short"
    collateral_asset: str           # e.g., SOL
    leverage: float                 # e.g., 5.0
    position_size: float            # e.g., 0.1
    order_type: str                 # "market" or "limit"
    status: str                     # pending, submitted, confirmed, failed
    entry_price: Optional[float] = None
    fees: Optional[float] = None
    source: str = "jupiter"         # Origin of this order
