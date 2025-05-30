import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import logging
import asyncio
import os
from types import SimpleNamespace
from flask import current_app
from datetime import datetime
from alert_core.alert_utils import resolve_wallet_metadata
from dashboard.dashboard_service import WALLET_IMAGE_MAP, DEFAULT_WALLET_IMAGE

from flask import (
    Blueprint,
    jsonify,
    render_template,
    render_template_string,
    request,
    session,
    redirect,
    url_for,
)
from jinja2 import ChoiceLoader, FileSystemLoader
from config.config_loader import update_config as merge_config
from utils.alert_helpers import calculate_threshold_progress

APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app'))
ALERT_MONITOR_DIR = os.path.join(APP_DIR, 'alert_monitor')
TEMPLATE_PATH = os.path.join(ALERT_MONITOR_DIR, 'alert_monitor.html')



alerts_bp = Blueprint(
    'alerts_bp',
    __name__,
    url_prefix='/alerts',
    template_folder=ALERT_MONITOR_DIR,
    static_folder=ALERT_MONITOR_DIR,
    static_url_path='/alerts/static'
)

# Enable template resolution from the main project's template directory as well
# so tests creating a minimal Flask app can still locate shared templates.
ROOT_TEMPLATES = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
alerts_bp.jinja_loader = ChoiceLoader([
    FileSystemLoader(ALERT_MONITOR_DIR),
    FileSystemLoader(ROOT_TEMPLATES),
])




# --- Logger Setup ---
logger = logging.getLogger("AlertsBPLogger")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

# --- Utilities ---
def convert_types_in_dict(d):
    if isinstance(d, dict):
        return {k: convert_types_in_dict(v) for k, v in d.items()}
    elif isinstance(d, list):
        return [convert_types_in_dict(i) for i in d]
    elif isinstance(d, str):
        low = d.lower().strip()
        if low in ["true", "on"]:
            return True
        elif low in ["false", "off"]:
            return False
        else:
            try:
                return float(d)
            except ValueError:
                return d
    return d


# --- Routes ---

@alerts_bp.route('/refresh', methods=['POST'])
def refresh_alerts():
    """
    Reevaluate all alerts and process notifications.
    """
    try:
        service = AlertServiceManager.get_instance()
        asyncio.run(service.process_all_alerts())
        log.success("Alerts refreshed successfully.", source="AlertsBP")
        return jsonify({"success": True, "message": "Alerts refreshed."})
    except Exception as e:
        logger.error(f"Error refreshing alerts: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@alerts_bp.route('/create_all', methods=['POST'])
def create_all_alerts():
    """
    Create sample alerts for testing purposes.
    """
    try:
        data_locker = current_app.data_locker
        sample_alerts = [
            {
                "id": "alert-sample-1",
                "created_at": datetime.now().isoformat(),
                "alert_type": "PriceThreshold",
                "alert_class": "Market",
                "asset_type": "BTC",
                "trigger_value": 60000,
                "condition": "ABOVE",
                "notification_type": "SMS",
                "level": "Normal",
                "last_triggered": None,
                "status": "Active",
                "frequency": 1,
                "counter": 0,
                "liquidation_distance": 0.0,
                "travel_percent": -10.0,
                "liquidation_price": 50000,
                "notes": "Sample BTC price alert",
                "description": "Test alert for BTC above 60k",
                "position_reference_id": None,
                "evaluated_value": 59000
            }
        ]

        for alert in sample_alerts:
            data_locker.alerts.create_alert(alert)  # ✅ Use create_alert (not save_alert!)

        log.success("Sample alerts created successfully.", source="AlertsBP")
        return jsonify({"success": True, "message": "Sample alerts created."})
    except Exception as e:
        logger.error(f"Error creating sample alerts: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@alerts_bp.route('/delete_all', methods=['POST'])
def delete_all_alerts():
    """
    Delete all alerts from the database.
    """
    try:
        data_locker = current_app.data_locker
        data_locker.alerts.clear_all_alerts()
        log.success("All alerts deleted successfully.", source="AlertsBP")
        return jsonify({"success": True, "message": "All alerts cleared."})
    except Exception as e:
        logger.error(f"Error deleting alerts: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@alerts_bp.route('/alert_config_page', methods=['GET'])
def alert_config_page():

    """Render the alert thresholds configuration page with config data."""
    try:
        config_data = current_app.data_locker.system.get_var("alert_thresholds") or {}
        alert_ranges = config_data.get("alert_ranges", {})
        price_alerts = alert_ranges.get("price_alerts", {})
        portfolio_alerts = alert_ranges.get("portfolio_alerts", {})
        positions_alerts = alert_ranges.get("positions_alerts", {})
        global_alert_config = config_data.get("global_alert_config", {})
    except Exception as e:
        logger.error(f"Failed to load alert configuration: {e}", exc_info=True)
        price_alerts = {}
        portfolio_alerts = {}
        positions_alerts = {}
        global_alert_config = {}

    return render_template(
        "alert_thresholds_legacy.html",
        price_alerts=price_alerts,
        portfolio_alerts=portfolio_alerts,
        positions_alerts=positions_alerts,
        global_alert_config=global_alert_config,
    )


@alerts_bp.route('/alert_thresholds', methods=['GET'])
def alert_thresholds():
    """Redirect legacy alert thresholds URL to the new system page."""
    return redirect(url_for('system.list_alert_thresholds'))


@alerts_bp.route('/monitor_page', methods=['GET'])
def monitor_page():
    print("🧪 Rendering from:", TEMPLATE_PATH)
    if not os.path.exists(TEMPLATE_PATH):
        return "Template file not found", 404
    with open(TEMPLATE_PATH, encoding='utf-8') as f:
        html = f.read()
    return render_template("alert_monitor.html")


@alerts_bp.route('/status_page', methods=['GET'])
def alert_status_page():
    """Render the combined alert status panel."""
    alerts = []
    try:
        dl = current_app.data_locker
        raw_alerts = dl.alerts.get_all_alerts() or []

        ASSET_IMAGE_MAP = {
            "BTC": "btc_logo.png",
            "ETH": "eth_logo.png",
            "SOL": "sol_logo.png",
        }
        DEFAULT_ASSET_IMAGE = "unknown.png"

        enriched = []
        for a in raw_alerts:
            asset = a.get("asset") or a.get("asset_type")
            a["asset"] = asset
            asset_key = str(asset or "").upper()
            a["asset_image"] = ASSET_IMAGE_MAP.get(asset_key, DEFAULT_ASSET_IMAGE)

            meta = resolve_wallet_metadata(SimpleNamespace(**a), dl)
            wallet_path = meta.get("wallet_image") or ""
            wallet_path = wallet_path.replace("\\", "/").strip()

            wallet_name = meta.get("wallet_name")
            if wallet_name in WALLET_IMAGE_MAP:
                wallet_img = f"images/{WALLET_IMAGE_MAP[wallet_name]}"
            elif wallet_path.startswith("/static/"):
                wallet_img = wallet_path[len("/static/"):]
            elif wallet_path.startswith("static/"):
                wallet_img = wallet_path[len("static/"):]
            elif wallet_path:
                wallet_img = wallet_path.lstrip("/")
            else:
                wallet_img = f"images/{DEFAULT_WALLET_IMAGE}"

            a["wallet_image"] = wallet_img
            a["wallet_name"] = wallet_name
            start = a.get("starting_value")
            trigger = a.get("trigger_value", 0)
            current = a.get("evaluated_value", 0)

            progress = calculate_threshold_progress(start, trigger, current)
            a["threshold_progress"] = progress

            enriched.append(a)
        alerts = sorted(enriched, key=lambda x: abs(100 - x.get("threshold_progress", 0)))
    except Exception as e:
        logger.error(f"Failed to load alerts for status page: {e}", exc_info=True)

    return render_template('alert_status.html', alerts=alerts)


@alerts_bp.route('/alert_matrix', methods=['GET'])
def alert_matrix_page():
    """Render the Alert Matrix page."""
    alerts = []
    hedges = []
    try:
        dl = current_app.data_locker
        alerts = dl.alerts.get_all_alerts()
    except Exception as e:
        logger.error(f"Failed to load alerts for matrix: {e}", exc_info=True)
    # Hedging data may not be available yet; attempt if method exists
    try:
        if hasattr(dl, 'portfolio') and hasattr(dl.portfolio, 'get_hedges'):
            hedges = dl.portfolio.get_hedges()
    except Exception as e:
        logger.warning(f"Failed to load hedges: {e}")
    return render_template('alert_matrix.html', alerts=alerts, hedges=hedges)



@alerts_bp.route('/monitor', methods=['GET'])
def monitor_data():
    """
    API endpoint that returns all alerts for the monitor UI.
    """
    try:
        data_locker = current_app.data_locker
        alert_list = data_locker.alerts.get_all_alerts()
        logger.info(f"Fetched {len(alert_list)} alerts for monitor", extra={"source": "AlertsBP"})
        return jsonify({"alerts": alert_list})
    except Exception as e:
        logger.error(f"Failed to load alerts for monitor: {e}", exc_info=True)
        return jsonify({"alerts": [], "error": str(e)}), 500

@alerts_bp.route('/update_config', methods=['POST'])
def update_config():
    """Update alert thresholds configuration."""
    token = session.get('csrf_token')
    request_token = request.headers.get('X-CSRFToken') or request.form.get('csrf_token')
    if token and token != request_token:
        logger.warning("CSRF token mismatch on update_config")
        return jsonify({"success": False, "error": "Invalid CSRF token"}), 400

    try:
        form_data = request.form.to_dict(flat=False)
        parsed = _parse_nested_form(form_data)
        parsed = convert_types_in_dict(parsed)

        merge_config(parsed)

        return jsonify({"success": True, "message": "Configuration updated"})
    except Exception as e:
        logger.error(f"Failed to update alert config: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@alerts_bp.route('/export_config', methods=['GET'])
def export_config():
    """Export alert thresholds configuration as JSON."""
    try:
        cfg = current_app.data_locker.system.get_var("alert_thresholds") or {}
        return jsonify(cfg)
    except Exception as e:
        logger.error(f"Failed to export alert config: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


@alerts_bp.route('/import_config', methods=['POST'])
def import_config():
    """Import alert thresholds configuration from JSON payload."""
    try:
        payload = request.get_json(force=True)
        if not isinstance(payload, dict):
            return jsonify({"success": False, "error": "Expected JSON object"}), 400
        current_app.data_locker.system.set_var("alert_thresholds", payload)
        return jsonify({"success": True, "message": "Configuration imported"})
    except Exception as e:
        logger.error(f"Failed to import alert config: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500

# --- Internal helpers ---

def _parse_nested_form(form: dict) -> dict:
    updated = {}
    for full_key, value in form.items():
        if isinstance(value, list):
            value = value[-1]
        full_key = full_key.strip()
        keys = []
        part = ""
        for char in full_key:
            if char == "[":
                if part:
                    keys.append(part)
                    part = ""
            elif char == "]":
                if part:
                    keys.append(part)
                    part = ""
            else:
                part += char
        if part:
            keys.append(part)
        current = updated
        for i, key in enumerate(keys):
            if i == len(keys) - 1:
                if isinstance(value, str):
                    lower_val = value.lower().strip()
                    if lower_val == "true":
                        v = True
                    elif lower_val == "false":
                        v = False
                    else:
                        try:
                            v = float(value)
                        except ValueError:
                            v = value
                else:
                    v = value
                current[key] = v
            else:
                if key not in current:
                    current[key] = {}
                current = current[key]
    return updated
