import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.logging import log
from positions.position_core import PositionCore
from data.data_locker import DataLocker
from utils.json_manager import JsonManager, JsonType
from xcom.xcom_core import get_latest_xcom_monitor_entry
#from monitor.ledger_service import LedgerService

from data.data_locker import DataLocker
from core.core_imports import DB_PATH
from alert_core.threshold_service import ThresholdService
from datetime import datetime
from zoneinfo import ZoneInfo
from system.system_core import SystemCore
from utils.fuzzy_wuzzy import fuzzy_match_key
from calc_core.calculation_core import CalculationCore
from core.core_imports import DB_PATH

# Mapping of wallet names to icon filenames
WALLET_IMAGE_MAP = {
    "ObiVault": "obivault.jpg",
    "R2Vault": "r2vault.jpg",
    "LandoVault": "landovault.jpg",
    "VaderVault": "vadervault.jpg",
    "YodaVault": "yodavault.jpg",
    "BobaVault": "bobavault.jpg",
    "LeiaVault": "leiavault.jpg",
    "BobaVault": "bobavault.jpg",
    "LandoVaultz": "landovault.jpg",
}
DEFAULT_WALLET_IMAGE = "unknown_wallet.jpg"

def format_monitor_time(iso_str):
    if not iso_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        pacific = dt.astimezone(ZoneInfo("America/Los_Angeles"))
        # format time on one line and date on the next
        return pacific.strftime("%I:%M %p\n%m/%d").lstrip("0")
    except Exception as e:
        log.error(f"Time formatting failed: {e}", source="DashboardContext")
        return "N/A"

def determine_color(age):
    if age < 300:
        return "green"
    elif age < 900:
        return "yellow"
    return "red"

ALERT_KEY_ALIASES = {
    "value": ["total_value_limits"],
    "leverage": ["avg_leverage_limits"],
    "size": ["total_size_limits"],
    "ratio": ["value_to_collateral_ratio_limits"],
    "travel": ["avg_travel_percent_limits"],
    "heat": ["total_heat_limits"]
}

def apply_color(metric_name, value, limits):
    """Return a color string based on metric thresholds.

    The logic mirrors the front-end card logic and respects the threshold
    condition (``"ABOVE"`` or ``"BELOW"``).  Values above ``high`` trigger
    ``red`` while those between ``medium`` and ``high`` trigger ``yellow``
    when the condition is ``"ABOVE"``.  For ``"BELOW"`` the comparisons are
    inverted.
    """
    try:
        thresholds = limits.get(metric_name.lower())
        if thresholds is None:
            matched_key = fuzzy_match_key(metric_name, limits,
                                          aliases=ALERT_KEY_ALIASES,
                                          threshold=40.0)
            thresholds = limits.get(matched_key)

        if not thresholds or value is None:
            return "red"

        val = float(value)
        cond = str(thresholds.get("condition", "ABOVE")).upper()

        high = thresholds.get("high")
        med = thresholds.get("medium")
        low = thresholds.get("low")

        if cond == "ABOVE":
            if high is not None and val >= float(high):
                return "red"
            if med is not None and val >= float(med):
                return "yellow"
            return "green"
        elif cond == "BELOW":
            if low is not None and val <= float(low):
                return "red"
            if med is not None and val <= float(med):
                return "yellow"
            return "green"
        else:
            return "green"

    except Exception as e:
        log.error(f"apply_color failed: {e}", source="DashboardContext")
        return "red"

import json

def format_short_time(iso_str):
    if not iso_str:
        return "—"
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        pacific = dt.astimezone(ZoneInfo("America/Los_Angeles"))
        return pacific.strftime("%-I:%M %p").replace(" 0", " ")
    except Exception:
        return "—"

def get_latest_price_monitor_history(dl):
    # For demo: pull BTC/ETH/SOL from your price DB or a sample row
    # Replace with real price table fetch if you have one
    price_rows = []
    try:
        # Example for a table: dl.prices.get_latest_all()
        price_rows = dl.prices.get_latest_all()
    except Exception:
        # Fallback to canned values if not implemented
        price_rows = [
            {"symbol": "BTC", "price": 63125.00},
            {"symbol": "ETH", "price": 2995.00},
            {"symbol": "SOL", "price": 156.23}
        ]
    icons = {"BTC": "🟡", "ETH": "🔷", "SOL": "🟣"}
    show_cents = {"BTC": False, "ETH": False, "SOL": True}
    history = []
    for row in price_rows:
        symbol = (row.get("symbol") or row.get("asset") or "BTC").upper()
        val = float(row.get("price", 0))
        history.append({
            "label": symbol,
            "icon": icons.get(symbol, "💲"),
            "value": val,
            "show_cents": show_cents.get(symbol, False)
        })
    return history

def get_latest_positions_monitor_history(dl):
    try:
        entry = dl.ledger.get_last_entry("position_monitor")
        if not entry: return []
        meta = entry.get("metadata")
        if isinstance(meta, str):
            meta = json.loads(meta)
        # Default to "Monitor" if not set
        who = meta.get("initiator", "Monitor")
        return [{
            "imported": meta.get("imported", 0),
            "skipped": meta.get("skipped", 0),
            "errors": meta.get("errors", 0),
            "timestamp": format_short_time(entry.get("timestamp")),
            "source": who if who in ("Manual", "Monitor") else "Monitor"
        }]
    except Exception:
        return []

def get_latest_operations_monitor_history(dl):
    try:
        entry = dl.ledger.get_last_entry("operations_monitor")
        if not entry: return []
        meta = entry.get("metadata")
        if isinstance(meta, str):
            meta = json.loads(meta)
        return [{
            "post_success": entry.get("status", "Error") == "Success",
            "duration_seconds": meta.get("duration_seconds", 0),
            "timestamp": format_short_time(entry.get("timestamp")),
            "error": meta.get("error")
        }]
    except Exception:
        return []

def get_latest_xcom_monitor_history(dl):
    try:
        entry = get_latest_xcom_monitor_entry(dl)
        if not entry:
            return []
        return [entry]
    except Exception:
        return []

def get_profit_badge_value(data_locker, system_core=None):
    """Return the highest profit across active positions.

    If a Profit threshold exists, its ``low`` value is used as the minimum
    qualifying profit.  When no threshold is found, ``0`` is used so the badge
    still appears when any position is in profit.
    """
    try:
        threshold_service = ThresholdService(data_locker.db)
        profit_threshold = threshold_service.get_thresholds(
            "Profit", "Position", "ABOVE"
        )
        low_limit = profit_threshold.low if profit_threshold else 0

        positions = PositionCore(data_locker).get_active_positions() or []
        profits = [float(p.get("pnl_after_fees_usd") or 0.0) for p in positions]
        above = [p for p in profits if p >= low_limit]
        if above:
            return round(max(above))
    except Exception as e:
        log.error(f"Profit badge calc failed: {e}", source="ProfitBadge")
    return None

def get_dashboard_context(data_locker, system_core=None):

    log.info("📊 Assembling dashboard context", source="DashboardContext")
    core = CalculationCore(data_locker)
    positions = PositionCore(data_locker).get_active_positions() or []
    positions = core.aggregate_positions_and_update(positions, DB_PATH)
    totals = core.calc_services.calculate_totals(positions)

    for pos in positions:
        wallet_name = pos.get("wallet") or pos.get("wallet_name") or "Unknown"
        pos["wallet_image"] = WALLET_IMAGE_MAP.get(wallet_name, DEFAULT_WALLET_IMAGE)

    core_sys = system_core or SystemCore(data_locker)
    portfolio_limits = core_sys.get_portfolio_thresholds()

    # ---- Profit Badge Calculation ----
    profit_badge_value = get_profit_badge_value(data_locker, core_sys)

    ls = data_locker.ledger
    ledger_info = {
        "age_price": ls.get_status("price_monitor").get("age_seconds", 9999),
        "last_price_time": ls.get_status("price_monitor").get("last_timestamp"),
        "age_positions": ls.get_status("position_monitor").get("age_seconds", 9999),
        "last_positions_time": ls.get_status("position_monitor").get("last_timestamp"),
        "age_operations": ls.get_status("operations_monitor").get("age_seconds", 9999),
        "last_operations_time": ls.get_status("operations_monitor").get("last_timestamp"),
        "age_xcom": ls.get_status("xcom_monitor").get("age_seconds", 9999),
        "last_xcom_time": ls.get_status("xcom_monitor").get("last_timestamp"),
    }

    monitor_statuses = {
        "price": ls.get_status("price_monitor").get("status", "Unknown"),
        "positions": ls.get_status("position_monitor").get("status", "Unknown"),
        "operations": ls.get_status("operations_monitor").get("status", "Unknown"),
        "xcom": ls.get_status("xcom_monitor").get("status", "Unknown"),
    }

    # Monitor card data (real, not canned)
    price_monitor_history = get_latest_price_monitor_history(data_locker)
    positions_monitor_history = get_latest_positions_monitor_history(data_locker)
    operations_monitor_history = get_latest_operations_monitor_history(data_locker)
    xcom_monitor_history = get_latest_xcom_monitor_history(data_locker)

    universal_items = [
        {"title": "Price", "icon": "📈", "value": format_monitor_time(ledger_info["last_price_time"]),
         "color": determine_color(ledger_info["age_price"]), "raw_value": ledger_info["age_price"]},
        {"title": "Positions", "icon": "📊", "value": format_monitor_time(ledger_info["last_positions_time"]),
         "color": determine_color(ledger_info["age_positions"]), "raw_value": ledger_info["age_positions"]},
        {"title": "Operations", "icon": "⚙️", "value": format_monitor_time(ledger_info["last_operations_time"]),
         "color": determine_color(ledger_info["age_operations"]), "raw_value": ledger_info["age_operations"]},
        {"title": "Xcom", "icon": "🛰️", "value": format_monitor_time(ledger_info["last_xcom_time"]),
         "color": determine_color(ledger_info["age_xcom"]), "raw_value": ledger_info["age_xcom"]},

        {"title": "Value", "icon": "💰", "value": "${:,.0f}".format(totals["total_value"]),
         "color": apply_color("total_value", totals["total_value"], portfolio_limits),
         "raw_value": totals["total_value"]},
        {"title": "Leverage", "icon": "⚖️", "value": "{:.2f}".format(totals["avg_leverage"]),
         "color": apply_color("avg_leverage", totals["avg_leverage"], portfolio_limits),
         "raw_value": totals["avg_leverage"]},
        {"title": "Size", "icon": "📊", "value": "${:,.0f}".format(totals["total_size"]),
         "color": apply_color("total_size", totals["total_size"], portfolio_limits),
         "raw_value": totals["total_size"]},
        {"title": "Ratio", "icon": "📐",
         "value": "{:.2f}".format(totals["total_value"] / totals["total_collateral"]) if totals["total_collateral"] > 0 else "N/A",
         "color": apply_color("value_to_collateral_ratio",
                              (totals["total_value"] / totals["total_collateral"]) if totals["total_collateral"] > 0 else None,
                              portfolio_limits),
         "raw_value": (totals["total_value"] / totals["total_collateral"]) if totals["total_collateral"] > 0 else None},
        {"title": "Travel", "icon": "✈️", "value": "{:.2f}%".format(totals["avg_travel_percent"]),
         "color": apply_color("avg_travel_percent", totals["avg_travel_percent"], portfolio_limits),
         "raw_value": totals["avg_travel_percent"]}
    ]

    monitor_titles = {"Price", "Positions", "Operations", "Xcom"}
    monitor_items = [item for item in universal_items if item["title"] in monitor_titles]
    status_items = [item for item in universal_items if item["title"] not in monitor_titles]

    # Build graph data from portfolio snapshots
    snapshots = data_locker.portfolio.get_snapshots() or []
    timestamps = []
    values = []
    collateral = []

    for snap in snapshots:
        timestamps.append(snap.get("snapshot_time"))
        values.append(int(round(float(snap.get("total_value", 0)))) )
        collateral.append(int(round(float(snap.get("total_collateral", 0)))) )

    current_value_int = int(round(totals["total_value"]))
    if values:
        if values[-1] != current_value_int:
            values[-1] = current_value_int

    current_collateral_int = int(round(totals["total_collateral"]))
    if collateral:
        if collateral[-1] != current_collateral_int:
            collateral[-1] = current_collateral_int

    graph_data = {
        "timestamps": timestamps,
        "values": values,
        "collateral": collateral,
    }

    long_total = sum(float(p.get("size", 0)) for p in positions if str(p.get("position_type", "")).upper() == "LONG")
    short_total = sum(float(p.get("size", 0)) for p in positions if str(p.get("position_type", "")).upper() == "SHORT")
    total = long_total + short_total
    size_composition = (
        {"series": [round(long_total / total * 100), round(short_total / total * 100)]}
        if total > 0 else {"series": [0, 0], "label": "No position data"}
    )

    long_collat = sum(float(p.get("collateral", 0)) for p in positions if str(p.get("position_type", "")).upper() == "LONG")
    short_collat = sum(float(p.get("collateral", 0)) for p in positions if str(p.get("position_type", "")).upper() == "SHORT")
    total_collat = long_collat + short_collat
    collateral_composition = (
        {"series": [round(long_collat / total_collat * 100), round(short_collat / total_collat * 100)]}
        if total_collat > 0 else {"series": [0, 0], "label": "No collateral data"}
    )

    wallets = []
    try:
        wallets = data_locker.read_wallets() or []
    except Exception as e:  # pragma: no cover - DB error extremely rare
        log.error(f"Failed to read wallets: {e}", source="DashboardContext")

    return {
        "theme_mode": data_locker.system.get_theme_mode(),
        "positions": positions,
        "liquidation_positions": positions,
        "portfolio_value": "${:,.2f}".format(totals["total_value"]),
        "portfolio_change": "N/A",
        "totals": totals,
        "ledger_info": ledger_info,
        "status_items": status_items,
        "monitor_items": monitor_items,
        "portfolio_limits": portfolio_limits,
        "profit_badge_value": profit_badge_value,
        "graph_data": graph_data,
        "size_composition": size_composition,
        "collateral_composition": collateral_composition,
        "price_monitor_history": price_monitor_history,
        "positions_monitor_history": positions_monitor_history,
        "operations_monitor_history": operations_monitor_history,
        "xcom_monitor_history": xcom_monitor_history,
        "price_monitor_status": monitor_statuses["price"],
        "positions_monitor_status": monitor_statuses["positions"],
        "operations_monitor_status": monitor_statuses["operations"],
        "xcom_monitor_status": monitor_statuses["xcom"],
        "wallets": wallets,
    }
