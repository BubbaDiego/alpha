import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from threading import Condition
from data.alert import AlertType
from data.alert import NotificationType
from data.alert import Condition
from core.logging import log




# 🚀 Batch normalizer for full Alert object
def normalize_alert_fields(alert):
    """
    Normalize key enum fields on an Alert object (alert_type, condition, notification_type).
    Accepts either Alert model or dict.
    """
    if isinstance(alert, dict):
        if "alert_type" in alert:
            alert["alert_type"] = normalize_alert_type(alert["alert_type"])
        if "condition" in alert:
            alert["condition"] = normalize_condition(alert["condition"])
        if "notification_type" in alert:
            alert["notification_type"] = normalize_notification_type(alert["notification_type"])
        return alert

    # Assume it's a Pydantic model or similar
    if hasattr(alert, "alert_type") and alert.alert_type:
        alert.alert_type = normalize_alert_type(alert.alert_type)
    if hasattr(alert, "condition") and alert.condition:
        alert.condition = normalize_condition(alert.condition)
    if hasattr(alert, "notification_type") and alert.notification_type:
        alert.notification_type = normalize_notification_type(alert.notification_type)

    return alert

def normalize_condition(condition_input):
    """
    Normalize incoming condition input to Condition Enum.
    """
    if isinstance(condition_input, Condition):
        return condition_input

    if isinstance(condition_input, str):
        cleaned = condition_input.strip().replace("_", "").replace(" ", "").lower()

        mapping = {
            "above": Condition.ABOVE,
            "below": Condition.BELOW,
        }

        if cleaned in mapping:
            return mapping[cleaned]
        else:
            raise ValueError(f"Invalid condition string: {condition_input}")

    raise TypeError(f"Invalid condition input: {type(condition_input)}")

def resolve_wallet_metadata(alert, data_locker=None):
    """
    Given an Alert object, resolve the wallet info (name, image_path) by following:
    alert → position_reference_id → position.wallet_name → wallet → image_path
    """
    if not alert or not alert.position_reference_id:
        return {"wallet_name": None, "wallet_image": None, "wallet_id": None}

    if not data_locker:
        data_locker = get_locker()

    position = data_locker.get_position_by_reference_id(alert.position_reference_id)
    if not position:
        return {"wallet_name": None, "wallet_image": None, "wallet_id": None}

    wallet_name = position.get("wallet_name") or position.get("wallet")
    wallet_id = position.get("wallet_id")

    wallet = data_locker.get_wallet_by_name(wallet_name) if wallet_name else None

    return {
        "wallet_name": wallet.get("name") if wallet else wallet_name,
        "wallet_image": wallet.get("image_path") if wallet else f"/static/images/{wallet_name.lower()}.jpg",
        "wallet_id": wallet_id
    }


def normalize_alert_type(alert_type_input):
    """
    Normalize incoming alert_type input:
    - If already an AlertType Enum, return as-is
    - If string, try to convert to AlertType Enum
    """
    if isinstance(alert_type_input, AlertType):
        return alert_type_input

    if isinstance(alert_type_input, str):
        cleaned = alert_type_input.strip().replace("_", "").replace(" ", "").lower()

        mapping = {
            "pricethreshold": AlertType.PriceThreshold,
            "profit": AlertType.Profit,
            "travelpercentliquid": AlertType.TravelPercentLiquid,
            "heatindex": AlertType.HeatIndex,
            "deathnail": AlertType.DeathNail,
            "totalvalue": AlertType.TotalValue,
            "totalsize": AlertType.TotalSize,
            "avgleverage": AlertType.AvgLeverage,
            "avgtravelpercent": AlertType.AvgTravelPercent,
            "valuetocollateralratio": AlertType.ValueToCollateralRatio,
            "totalheat": AlertType.TotalHeat
        }

        if cleaned in mapping:
            return mapping[cleaned]
        else:
            raise ValueError(
                f"Invalid alert_type string: {alert_type_input}. "
                f"Expected one of: {list(mapping.keys())}"
            )

    raise TypeError(f"Invalid alert_type input: {type(alert_type_input)}")




def normalize_notification_type(notification_input):
    """
    Normalize incoming notification_type input to NotificationType Enum.
    """
    if isinstance(notification_input, NotificationType):
        return notification_input

    if isinstance(notification_input, str):
        cleaned = notification_input.strip().replace("_", "").replace(" ", "").lower()

        mapping = {
            "sms": NotificationType.SMS,
            "email": NotificationType.EMAIL,
            "phonecall": NotificationType.PHONECALL,
        }

        if cleaned in mapping:
            return mapping[cleaned]
        else:
            raise ValueError(f"Invalid notification_type string: {notification_input}")

    raise TypeError(f"Invalid notification_type input: {type(notification_input)}")

def log_alert_summary(alert):
    """
    Print a clean, emoji-annotated summary of a created alert.
    """

    alert_type = alert.get("alert_type") if isinstance(alert, dict) else getattr(alert, "alert_type", None)
    alert_class = alert.get("alert_class") if isinstance(alert, dict) else getattr(alert, "alert_class", None)
    trigger_value = alert.get("trigger_value") if isinstance(alert, dict) else getattr(alert, "trigger_value", None)

    print(f"📦 Alert Created → 🧭 Class: {alert_class} | 🏷️ Type: {alert_type} | 🎯 Trigger: {trigger_value}")

    if isinstance(alert, dict):
        alert_type = alert.get("alert_type")
        alert_class = alert.get("alert_class")
        trigger_value = alert.get("trigger_value")

        log.info(
            f"📦 Alert Created → 🧭 Class: {alert_class} | 🏷️ Type: {alert_type} | 🎯 Trigger: {trigger_value}",
            source="CreateAlert"
        )


def load_alert_thresholds_from_file(data_locker):
    """Manually import alert_thresholds from disk into the database."""
    from config.config_loader import load_config
    from core.constants import ALERT_THRESHOLDS_PATH

    config = load_config(str(ALERT_THRESHOLDS_PATH))
    if not config:
        raise RuntimeError("🛑 Config file is invalid or empty")

    data_locker.system.set_var("alert_thresholds", config)
    log.success(
        "✅ Loaded alert_thresholds config into DB from file",
        source="ConfigImport",
    )
    return config
