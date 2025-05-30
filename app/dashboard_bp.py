import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import asyncio
from flask import Blueprint, render_template, jsonify, request, current_app
from jinja2 import ChoiceLoader, FileSystemLoader
from typing import Optional
from data.models import AlertThreshold
from data.data_locker import DataLocker
from positions.position_core import PositionCore
from core.core_imports import DB_PATH
from cyclone.cyclone_engine import Cyclone

from datetime import datetime
from zoneinfo import ZoneInfo
from dashboard.dashboard_service import get_dashboard_context
from utils.fuzzy_wuzzy import fuzzy_match_key
from core.constants import THEME_CONFIG_PATH
from core.logging import log
from utils.route_decorators import route_log_alert
from dashboard.dashboard_logger import log_dashboard_full, list_positions_verbose

dashboard_bp = Blueprint(
    'dashboard',
    __name__,
    template_folder='dashboard',
    static_folder='dashboard',
    static_url_path='/dashboard_static'
)

# Ensure templates in the project root are also discovered when this blueprint
# is used in isolated test apps where the Flask application's template folder
# may not point to the repository root.
ROOT_TEMPLATES = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
dashboard_bp.jinja_loader = ChoiceLoader([
    FileSystemLoader(os.path.join(os.path.dirname(__file__), 'dashboard')),
    FileSystemLoader(ROOT_TEMPLATES),
])

@dashboard_bp.route("/new_dashboard")
def new_dashboard():
    return render_template("sonic_dashboard.html")



# Main dashboard page
@dashboard_bp.route("/dash")
@route_log_alert
def dash_page():
    context = get_dashboard_context(current_app.data_locker, current_app.system_core)
    return render_template("sonic_dashboard.html", **context)

# ✅ NEW WALLET IMAGE MAP
WALLET_IMAGE_MAP = {
    "ObiVault": "obivault.jpg",
    "R2Vault": "r2vault.jpg",
    "LandoVault": "landovault.jpg",
    "VaderVault": "vadervault.jpg",
    "LandoVaultz": "landovault.jpg",
}
DEFAULT_WALLET_IMAGE = "unknown_wallet.jpg"

# ---------------------------------
# Main Dashboard Helpers
# ---------------------------------
def format_monitor_time(iso_str):
    if not iso_str:
        log.debug("iso_str is None or empty")
        return "N/A"
    try:
        log.debug(f"Raw iso_str received: {iso_str}")
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        pacific = dt.astimezone(ZoneInfo("America/Los_Angeles"))

        # Manual components to strip leading 0s
        hour = pacific.strftime("%I").lstrip('0') or '0'
        minute = pacific.strftime("%M")
        ampm = pacific.strftime("%p")
        month = str(pacific.month)
        day = str(pacific.day)

        formatted = f"{hour}:{minute} {ampm}\n{month}/{day}"
        log.debug(f"Parsed and formatted time: {formatted}")
        return formatted
    except Exception as e:
        log.debug(f"Exception occurred in format_monitor_time: {e}")
        return "N/A"

def apply_color(metric_name: str, value: float, thresholds: dict) -> str:
    try:
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
        print(f"❌ apply_color failed: {e}")
        return "red"

def get_alert_label(alert_type):
    labels = {
        "AvgLeverage": "Total Leverage",
        "AvgTravelPercent": "Total Travel Percent",
        "TotalHeat": "Total Heat",
        "TotalValue": "Total Value",
        "TotalSize": "Total Size",
        "ValueToCollateralRatio": "Total Ratio",
    }
    return labels.get(alert_type, alert_type)

def get_alert_icon(alert_type):
    icons = {
        "AvgLeverage": "⚖️",
        "AvgTravelPercent": "✈️",
        "TotalHeat": "🔥",
        "TotalValue": "💰",
        "TotalSize": "📊",
        "ValueToCollateralRatio": "📐",
    }
    return icons.get(alert_type, "🔔")

# ---------------------------------
# API: Graph Data (Real portfolio history)
# ---------------------------------
@dashboard_bp.route("/api/graph_data")
@route_log_alert
def api_graph_data():
    """Return portfolio snapshot totals for the history line chart."""
    context = get_dashboard_context(current_app.data_locker, current_app.system_core)
    graph = context.get("graph_data", {})
    return jsonify(graph)

# ---------------------------------
# API: Size Composition Pie (Real positions)
# ---------------------------------
@dashboard_bp.route("/api/size_composition")
@route_log_alert
def api_size_composition():
    try:
        core = PositionCore(current_app.data_locker)
        positions = core.get_active_positions() or []

        long_total = sum(float(p.get("size", 0)) for p in positions if str(p.get("position_type", "")).upper() == "LONG")
        short_total = sum(float(p.get("size", 0)) for p in positions if str(p.get("position_type", "")).upper() == "SHORT")
        total = long_total + short_total

        if total > 0:
            series = [round(long_total / total * 100), round(short_total / total * 100)]
        else:
            print("⚠️ No LONG/SHORT positions found for size pie.")
            series = [0, 0]

        return jsonify({"series": series})

    except Exception as e:
        print(f"[Pie Chart Error] Size composition: {e}")
        return jsonify({"error": str(e)}), 500

# ---------------------------------
# API: Collateral Composition Pie (Real positions)
# ---------------------------------
@dashboard_bp.route("/api/collateral_composition")
@route_log_alert
def api_collateral_composition():
    try:
        core = PositionCore(current_app.data_locker)
        positions = core.get_active_positions() or []

        long_total = sum(float(p.get("collateral", 0)) for p in positions if str(p.get("position_type", "")).upper() == "LONG")
        short_total = sum(float(p.get("collateral", 0)) for p in positions if str(p.get("position_type", "")).upper() == "SHORT")
        total = long_total + short_total

        if total > 0:
            series = [round(long_total / total * 100), round(short_total / total * 100)]
        else:
            print("⚠️ No LONG/SHORT positions found for collateral pie.")
            series = [0, 0]

        return jsonify({"series": series})

    except Exception as e:
        print(f"[Pie Chart Error] Collateral composition: {e}")
        return jsonify({"error": str(e)}), 500

@dashboard_bp.route("/api/ledger_ages")
def api_ledger_ages():
    ls = current_app.data_locker.ledger
    return jsonify({
        "age_price": ls.get_status("price_monitor")["age_seconds"],
        "last_price_time": ls.get_status("price_monitor")["last_timestamp"],
        "age_positions": ls.get_status("position_monitor")["age_seconds"],
        "last_positions_time": ls.get_status("position_monitor")["last_timestamp"],
        "age_cyclone": ls.get_status("sonic_monitor")["age_seconds"],
        "last_cyclone_time": ls.get_status("sonic_monitor")["last_timestamp"]
    })

@dashboard_bp.route("/test/desktop")
def test_desktop_dashboard():
    mock_context = {
        "monitor_items": [
            {"title": "Price", "icon": "📈", "value": "3:45 PM", "color": "green", "raw_value": 100},
            {"title": "Positions", "icon": "📊", "value": "3:41 PM", "color": "yellow", "raw_value": 500},
            {"title": "Operations", "icon": "⚙️", "value": "3:39 PM", "color": "red", "raw_value": 1000},
            {"title": "Xcom", "icon": "🛰️", "value": "3:20 PM", "color": "red", "raw_value": 5000},
        ],
        "status_items": [
            {"title": "Value", "icon": "💰", "value": "$23,450", "color": "yellow", "raw_value": 23450},
            {"title": "Leverage", "icon": "⚖️", "value": "3.5", "color": "green", "raw_value": 3.5},
            {"title": "Size", "icon": "📊", "value": "$12,000", "color": "green", "raw_value": 12000},
            {"title": "Ratio", "icon": "📐", "value": "1.4", "color": "green", "raw_value": 1.4},
            {"title": "Travel", "icon": "✈️", "value": "-4.5%", "color": "yellow", "raw_value": -4.5},
        ],
        "portfolio_limits": {
            "price": {"low": 300, "medium": 600, "high": 900},
            "positions": {"low": 300, "medium": 600, "high": 900},
            "operations": {"low": 300, "medium": 600, "high": 900},
            "xcom": {"low": 300, "medium": 600, "high": 900},
            "value": {"low": 10000, "medium": 25000, "high": 50000},
            "leverage": {"low": 2.0, "medium": 5.0, "high": 10.0},
            "size": {"low": 1000, "medium": 5000, "high": 10000},
            "ratio": {"low": 1.1, "medium": 1.5, "high": 2.0},
            "travel": {"low": -10.0, "medium": -5.0, "high": 0.0},
        },
        "profit_badge_value": 123
    }
    return render_template("sonic_dashboard.html", **mock_context)

@dashboard_bp.route("/api/dashboard_cards", methods=["GET"])
def api_dashboard_cards():
    context = get_dashboard_context(current_app.data_locker, current_app.system_core)
    rendered_cards = render_template("dashboard_top.html", **context)
    return jsonify({"success": True, "html": rendered_cards})

@dashboard_bp.route('/cyclone_market_update', methods=['POST'])
def cyclone_market_update():
    try:
        asyncio.run(current_app.cyclone.run_market_updates())
        # Refresh the main DataLocker connection so new data is visible
        current_app.data_locker.db.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@dashboard_bp.route('/cyclone_sync', methods=['POST'])
def cyclone_sync():
    try:
        asyncio.run(current_app.cyclone.run_composite_position_pipeline())
        current_app.data_locker.db.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@dashboard_bp.route('/cyclone_full_cycle', methods=['POST'])
def cyclone_full_cycle():
    try:
        asyncio.run(current_app.cyclone.run_cycle())
        current_app.data_locker.db.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@dashboard_bp.route('/cyclone_wipe_all', methods=['POST'])
def cyclone_wipe_all():
    try:
        asyncio.run(current_app.cyclone.run_clear_all_data())
        current_app.data_locker.db.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
