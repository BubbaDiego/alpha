import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import pytz
from datetime import datetime, timedelta
from flask import (
    Blueprint, request, jsonify, render_template,
    redirect, url_for, flash, current_app
)
from core.logging import log
from positions.position_core import PositionCore
from calc_core.calculation_core import CalculationCore
from calc_core.calc_services import CalcServices
from utils.route_decorators import route_log_alert


positions_bp = Blueprint("positions", __name__, template_folder="../templates/positions")


def _convert_iso_to_pst(iso_str):
    if not iso_str or iso_str == "N/A":
        return "N/A"
    if "T" not in iso_str:
        return iso_str
    pst = pytz.timezone("US/Pacific")
    try:
        dt_obj = datetime.fromisoformat(iso_str)
        dt_pst = dt_obj.astimezone(pst)
        return dt_pst.strftime("%m/%d/%Y %I:%M:%S %p %Z")
    except Exception as e:
        log.error(f"Error converting timestamp: {e}")
        return "N/A"


@positions_bp.route("/", methods=["GET"])
@route_log_alert
def list_positions():
    try:
        core = PositionCore(current_app.data_locker)
        positions = core.get_active_positions()

        config_data = current_app.data_locker.system.get_var("alert_thresholds") or {}
        alert_dict = config_data.get("alert_ranges", {})

        def get_alert_class(value, low, med, high):
            try: low = float(low) if low not in (None, "") else float('-inf')
            except: low = float('-inf')
            try: med = float(med) if med not in (None, "") else float('inf')
            except: med = float('inf')
            try: high = float(high) if high not in (None, "") else float('inf')
            except: high = float('inf')
            if value >= high: return "alert-high"
            elif value >= med: return "alert-medium"
            elif value >= low: return "alert-low"
            return ""

        liqd_cfg = alert_dict.get("liquidation_distance_ranges", {})
        hi_cfg = alert_dict.get("heat_index_ranges", {})
        for pos in positions:
            liqd = float(pos.get("liquidation_distance") or 0.0)
            heat = float(pos.get("heat_index") or 0.0)
            pos["liqdist_alert_class"] = get_alert_class(liqd, liqd_cfg.get("low"), liqd_cfg.get("medium"), liqd_cfg.get("high"))
            pos["heat_alert_class"] = get_alert_class(heat, hi_cfg.get("low"), hi_cfg.get("medium"), hi_cfg.get("high"))

        totals = CalcServices().calculate_totals(positions)
        times = current_app.data_locker.get_last_update_times() or {}
        pos_time = _convert_iso_to_pst(times.get("last_update_time_positions", "N/A"))

        return render_template("positions.html",
                               positions=positions,
                               totals=totals,
                               portfolio_value=totals.get("total_value", 0),
                               last_update_positions=pos_time,
                               last_update_positions_source=times.get("last_update_positions_source", "N/A"))

    except Exception as e:
        log.error(f"Error in listing positions: {e}")
        return jsonify({"error": str(e)}), 500


@positions_bp.route("/table", methods=["GET"])
@route_log_alert
def positions_table():
    try:
        core = PositionCore(current_app.data_locker)
        positions = core.get_active_positions()
        totals = CalcServices().calculate_totals(positions)
        return render_template("positions_table.html", positions=positions, totals=totals)
    except Exception as e:
        log.error(f"Error in positions_table: {e}")
        return jsonify({"error": str(e)}), 500


@positions_bp.route("/upload", methods=["POST"])
@route_log_alert
def upload_positions():
    try:
        core = PositionCore(current_app.data_locker)
        file = request.files.get("file")
        if not file:
            return jsonify({"error": "No file part in request"}), 400
        content = file.read().decode("utf-8").strip()
        if not content:
            return jsonify({"error": "Uploaded file is empty"}), 400
        items = json.loads(content)
        if not isinstance(items, list):
            return jsonify({"error": "Expected a list of positions"}), 400
        for item in items:
            if "wallet_name" in item:
                item["wallet"] = item["wallet_name"]
            core.create_position(item)
        return jsonify({"message": "Positions uploaded successfully"}), 200
    except Exception as e:
        log.error(f"Error uploading positions: {e}")
        return jsonify({"error": str(e)}), 500


@positions_bp.route("/edit/<position_id>", methods=["POST"])
@route_log_alert
def edit_position(position_id):
    return jsonify({"error": "Edit not yet implemented in PositionCore"}), 501


@positions_bp.route("/delete/<position_id>", methods=["POST"])
@route_log_alert
def delete_position(position_id):
    try:
        core = PositionCore(current_app.data_locker)
        core.delete_position(position_id)
        return redirect(url_for("positions.list_positions"))
    except Exception as e:
        log.error(f"Error deleting position {position_id}: {e}")
        return jsonify({"error": str(e)}), 500


@positions_bp.route("/delete-all", methods=["POST"])
@route_log_alert
def delete_all_positions():
    try:
        core = PositionCore(current_app.data_locker)
        core.clear_all_positions()
        return redirect(url_for("positions.list_positions"))
    except Exception as e:
        log.error(f"Error deleting all positions: {e}")
        return jsonify({"error": str(e)}), 500


@positions_bp.route("/update_jupiter", methods=["GET", "POST"])
@route_log_alert
def update_jupiter():
    try:
        core = PositionCore(current_app.data_locker)
        result = core.update_positions_from_jupiter(source="user")
        if "error" in result:
            return jsonify(result), 500
        return jsonify(result), 200
    except Exception as e:
        log.error(f"💥 update_jupiter route failed: {e}")
        return jsonify({"error": str(e)}), 500


@positions_bp.route("/api/data", methods=["GET"])
@route_log_alert
def positions_data_api():
    try:
        core = PositionCore(current_app.data_locker)
        positions = core.get_active_positions()
        mini_prices = []
        for asset in ["BTC", "ETH", "SOL"]:
            row = current_app.data_locker.get_latest_price(asset)
            if row:
                mini_prices.append({
                    "asset_type": row["asset_type"],
                    "current_price": float(row["current_price"])
                })
        totals = CalcServices().calculate_totals(positions)
        return jsonify({
            "mini_prices": mini_prices,
            "positions": positions,
            "totals": totals
        })
    except Exception as e:
        log.error(f"Error in positions_data_api: {e}")
        return jsonify({"error": str(e)}), 500
