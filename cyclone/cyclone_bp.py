import asyncio
import os
from flask import Blueprint, jsonify, render_template, current_app
# Access the shared Cyclone instance attached to the Flask app
from core.core_imports import BASE_DIR, log
from threading import Thread
import inspect

cyclone_bp = Blueprint("cyclone", __name__, template_folder=".", url_prefix="/cyclone")

# --- Smart Background Runner ---
def run_in_background(task_func, name="UnnamedTask"):
    app = current_app._get_current_object()

    def wrapper():
        try:
            log.info(f"🧵 Starting background task: {name}", source="AsyncRunner")

            with app.app_context():
                if inspect.iscoroutinefunction(task_func):
                    asyncio.run(task_func())
                else:
                    result = task_func()
                    if inspect.iscoroutine(result):
                        asyncio.run(result)

            log.success(f"✅ Completed background task: {name}", source="AsyncRunner")

        except Exception as e:
            log.error(f"🔥 Task '{name}' crashed: {e}", source="AsyncRunner")

    Thread(target=wrapper, name=name).start()

# --- Dashboard View (Optional) ---
@cyclone_bp.route("/dashboard", methods=["GET"])
def cyclone_dashboard():
    return render_template("cyclone.html")

# --- API Endpoints ---
@cyclone_bp.route("/run_market_updates", methods=["POST"])
def run_market_updates():
    try:
        run_in_background(lambda: asyncio.run(current_app.cyclone.run_market_updates()),
                          name="MarketUpdate")
        return jsonify({"message": "Market Updates Started."}), 202
    except Exception as e:
        log.error(f"Market Updates Error: {e}", source="CycloneAPI")
        return jsonify({"error": str(e)}), 500

@cyclone_bp.route("/run_position_updates", methods=["POST"])
def run_position_updates():
    try:
        run_in_background(lambda: asyncio.run(current_app.cyclone.run_position_updates()),
                          name="JupiterUpdate")
        return jsonify({"message": "Position Updates Started."}), 202
    except Exception as e:
        log.error(f"Position Updates Error: {e}", source="CycloneAPI")
        return jsonify({"error": str(e)}), 500

@cyclone_bp.route("/run_dependent_updates", methods=["POST"])
def run_dependent_updates():
    try:
        run_in_background(lambda: asyncio.run(current_app.cyclone.run_enrich_positions()),
                          name="DependentUpdate")
        return jsonify({"message": "Dependent Updates Started."}), 202
    except Exception as e:
        log.error(f"Dependent Updates Error: {e}", source="CycloneAPI")
        return jsonify({"error": str(e)}), 500

@cyclone_bp.route("/run_alert_evaluations", methods=["POST"])
def run_alert_evaluations():
    try:
        run_in_background(lambda: asyncio.run(current_app.cyclone.run_alert_updates()),
                          name="AlertEval")
        return jsonify({"message": "Alert Evaluations Started."}), 202
    except Exception as e:
        log.error(f"Alert Evaluations Error: {e}", source="CycloneAPI")
        return jsonify({"error": str(e)}), 500

@cyclone_bp.route("/run_system_updates", methods=["POST"])
def run_system_updates():
    try:
        run_in_background(lambda: asyncio.run(current_app.cyclone.run_system_updates()),
                          name="SystemUpdate")
        return jsonify({"message": "System Updates Started."}), 202
    except Exception as e:
        log.error(f"System Updates Error: {e}", source="CycloneAPI")
        return jsonify({"error": str(e)}), 500

@cyclone_bp.route("/run_full_cycle", methods=["POST"])
def run_full_cycle():
    try:
        run_in_background(lambda: asyncio.run(current_app.cyclone.run_cycle()),
                          name="FullCycle")
        return jsonify({"message": "Full Cycle Started."}), 202
    except Exception as e:
        log.error(f"Full Cycle Error: {e}", source="CycloneAPI")
        return jsonify({"error": str(e)}), 500

@cyclone_bp.route("/clear_all_data", methods=["POST"])
def clear_all_data():
    try:
        run_in_background(lambda: asyncio.run(current_app.cyclone.run_clear_all_data()),
                          name="ClearAllData")
        return jsonify({"message": "Clear All Data Started."}), 202
    except Exception as e:
        log.error(f"Clear All Data Error: {e}", source="CycloneAPI")
        return jsonify({"error": str(e)}), 500

# --- Alert Management Endpoints ---
@cyclone_bp.route("/run_create_alerts", methods=["POST"])
def run_create_alerts():
    try:
        run_in_background(lambda: asyncio.run(current_app.cyclone.alert_core.create_all_alerts()),
                          name="CreateAlerts")
        return jsonify({"message": "Alert creation started."}), 202
    except Exception as e:
        log.error(f"Create Alerts Error: {e}", source="CycloneAPI")
        return jsonify({"error": str(e)}), 500

@cyclone_bp.route("/clear_alerts", methods=["POST"])
def clear_alerts():
    try:
        run_in_background(current_app.cyclone.clear_alerts_backend,
                          name="ClearAlerts")
        return jsonify({"message": "Alert deletion started."}), 202
    except Exception as e:
        log.error(f"Clear Alerts Error: {e}", source="CycloneAPI")
        return jsonify({"error": str(e)}), 500

@cyclone_bp.route("/cyclone_logs", methods=["GET"])
def api_cyclone_logs():
    try:
        log_file = os.path.join(BASE_DIR, "monitor", "operations_log.txt")
        if not os.path.exists(log_file):
            return jsonify({"logs": []})
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        last_lines = lines[-50:]
        cleaned = [line.rstrip("\n") for line in last_lines]
        return jsonify({"logs": cleaned})
    except Exception as e:
        current_app.logger.exception("Error reading Cyclone logs:", exc_info=True)
        return jsonify({"error": str(e)}), 500
