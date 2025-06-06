"""
📁 Module: wallet.py
📌 Purpose: Defines the core Wallet object used internally throughout the system.
🔐 This is NOT tied to DB schema or I/O — it's your internal data contract.
"""

from typing import List, Optional
from enum import Enum

try:
    from pydantic import BaseModel, Field
    if not hasattr(BaseModel, "__fields__"):
        raise ImportError("stub")
except Exception:  # pragma: no cover - optional dependency or stub detected
    class BaseModel:
        """Simple fallback when pydantic is not installed."""

        def __init__(self, **data):
            for key, value in data.items():
                setattr(self, key, value)

        def dict(self) -> dict:  # type: ignore[override]
            return self.__dict__

    def Field(default=None, **_):  # type: ignore
        return default

# 💬 Optional wallet types for grouping or behavior flags
class WalletType(str, Enum):
    PERSONAL = "personal"
    BOT = "bot"
    EXCHANGE = "exchange"
    TEST = "test"

class Wallet(BaseModel):
    """
    💼 Represents a single crypto wallet in the system.

    🎯 Used in:
    - UI rendering
    - Position enrichment (wallet lookup)
    - Alert linking
    - Portfolio breakdowns
    """

    name: str                              # 🔑 Unique wallet name (e.g. "VaderVault")
    public_address: str                    # 🌐 On-chain public address (used in queries)
    chrome_profile: Optional[str] = "Default"  # 🌐 Chrome profile for Jupiter links
    private_address: Optional[str] = None  # 🔒 Optional private key (DEV/TEST only)
    image_path: Optional[str] = None       # 🖼️ Avatar for UI representation
    balance: float = 0.0                   # 💰 Current USD balance (optional sync)
    tags: List[str] = Field(default_factory=list)  # 🏷️ Arbitrary tags (e.g. ["test", "hedge"])
    is_active: bool = True                 # ✅ Status flag — soft delete/use toggle
    type: WalletType = WalletType.PERSONAL # 📂 Usage category

    def __repr__(self):
        return (
            f"Wallet(name={self.name!r}, public_address={self.public_address!r}, "
            f"balance={self.balance}, tags={self.tags}, is_active={self.is_active}, "
            f"type={self.type})"
        )
