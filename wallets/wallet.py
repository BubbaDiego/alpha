"""
📁 Module: wallet.py
📌 Purpose: Defines the core Wallet object used internally throughout the system.
🔐 This is NOT tied to DB schema or I/O — it's your internal data contract.
"""

from typing import List, Optional
from enum import Enum
from dataclasses import dataclass, field

# 💬 Optional wallet types for grouping or behavior flags
class WalletType(str, Enum):
    PERSONAL = "personal"
    BOT = "bot"
    EXCHANGE = "exchange"
    TEST = "test"

@dataclass
class Wallet:
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
    private_address: Optional[str] = None  # 🔒 Optional private key (DEV/TEST only)
    image_path: Optional[str] = None       # 🖼️ Avatar for UI representation
    balance: float = 0.0                   # 💰 Current USD balance (optional sync)
    tags: List[str] = field(default_factory=list)  # 🏷️ Arbitrary tags (e.g. ["test", "hedge"])
    is_active: bool = True                 # ✅ Status flag — soft delete/use toggle
    type: WalletType = WalletType.PERSONAL # 📂 Usage category

    def __repr__(self):
        return (
            f"Wallet(name={self.name!r}, public_address={self.public_address!r}, "
            f"balance={self.balance}, tags={self.tags}, is_active={self.is_active}, "
            f"type={self.type})"
        )
