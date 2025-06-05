"""
📁 Module: wallet_schema.py
📌 Purpose: Pydantic models for validating input/output for Wallet API and UI forms.
🔐 Keeps external I/O clean and safe while decoupling from internal logic model.
"""

from typing import Optional, List
try:
    from pydantic import BaseModel, Field
    if not hasattr(BaseModel, "__fields__"):
        raise ImportError("stub")
except Exception:  # pragma: no cover - optional dependency or stub detected
    class BaseModel:
        """Simple drop-in fallback when pydantic is unavailable."""

        def __init__(self, **data):
            for key, value in data.items():
                setattr(self, key, value)

        def dict(self) -> dict:
            return self.__dict__

    def Field(default=None, **_):  # type: ignore
        return default
from enum import Enum

# ♻️ Sync with wallet.py to ensure matching enum values
class WalletType(str, Enum):
    PERSONAL = "personal"
    BOT = "bot"
    EXCHANGE = "exchange"
    TEST = "test"

# 🔐 Used when creating or editing a wallet (form or API input)
class WalletIn(BaseModel):
    name: str = Field(..., example="VaderVault", description="Unique wallet name")
    public_address: str = Field(..., example="0xABC123...", description="Public wallet address")
    chrome_profile: Optional[str] = None
    private_address: Optional[str] = Field(None, description="Optional private key (only for dev)")
    chrome_profile: Optional[str] = Field("Default", description="Chrome profile for Jupiter links")
    image_path: Optional[str] = Field(None, example="/static/img/vader.png")
    balance: float = Field(0.0, ge=0.0)
    tags: List[str] = Field(default_factory=list)
    is_active: bool = True
    type: WalletType = WalletType.PERSONAL

# 📤 Output schema — used in API responses, UI lists, etc.
class WalletOut(BaseModel):
    name: str
    public_address: str
    chrome_profile: Optional[str] = None
    balance: float
    image_path: Optional[str]
    chrome_profile: Optional[str] = "Default"
    tags: List[str]
    is_active: bool
    type: WalletType
