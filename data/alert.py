try:
    from pydantic import BaseModel
    if not hasattr(BaseModel, "__fields__"):
        raise ImportError("stub")
except Exception:  # pragma: no cover - optional dependency or stub detected
    class BaseModel:
        """Simplistic fallback when pydantic is not installed."""

        def __init__(self, **data):
            for key, value in data.items():
                setattr(self, key, value)

        def dict(self) -> dict:
            return self.__dict__
from typing import Optional
from datetime import datetime
from enum import Enum

# === ENUMS ===

class AlertType(str, Enum):
    # 🔥 Position-level alert types
    HeatIndex = "HeatIndex"
    Profit = "Profit"
    TravelPercentLiquid = "TravelPercentLiquid"
    DeathNail = "DeathNail"

    # 📈 Market-level alert types
    PriceThreshold = "PriceThreshold"

    # 🧮 Portfolio-level alert types
    TotalValue = "TotalValue"
    TotalSize = "TotalSize"
    AvgLeverage = "AvgLeverage"
    AvgTravelPercent = "AvgTravelPercent"
    ValueToCollateralRatio = "ValueToCollateralRatio"
    TotalHeat = "TotalHeat"

class Condition(str, Enum):
    ABOVE = "ABOVE"
    BELOW = "BELOW"

class AlertLevel(str, Enum):
    NORMAL = "Normal"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class Status(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"

class NotificationType(str, Enum):
    SMS = "SMS"
    EMAIL = "EMAIL"
    PHONECALL = "PHONECALL"

# === MAIN MODEL ===

class Alert(BaseModel):
    id: str
    alert_type: AlertType
    alert_class: Optional[str] = "Unknown"
    asset: Optional[str] = None
    trigger_value: Optional[float] = None
    condition: Condition
    evaluated_value: Optional[float] = 0.0
    position_reference_id: Optional[str] = None
    position_type: Optional[str] = None
    notification_type: Optional[NotificationType] = NotificationType.SMS
    level: Optional[AlertLevel] = AlertLevel.NORMAL
    last_triggered: Optional[datetime] = None
    status: Optional[Status] = Status.ACTIVE
    frequency: Optional[int] = 1
    counter: Optional[int] = 0
    liquidation_distance: Optional[float] = 0.0
    travel_percent: Optional[float] = 0.0
    liquidation_price: Optional[float] = 0.0
    starting_value: Optional[float] = None  # 🧱 Used to represent bar start on UI
    notes: Optional[str] = ""
    description: Optional[str] = ""

    class Config:
        use_enum_values = True  # serialize enums into their string values (not Enum objects)
