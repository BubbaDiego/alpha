# monitor/api/monitor_api.py

from flask import Flask, jsonify
from monitor_core import MonitorCore
from monitor_registry import MonitorRegistry
from price_monitor import PriceMonitor
from operations_monitor import OperationsMonitor
from position_monitor import PositionMonitor
from latency_monitor import LatencyMonitor
from core.logging import log

app = Flask(__name__)

# Setup core + registry
registry = MonitorRegistry()
registry.register("price_monitor", PriceMonitor())
registry.register("operations_monitor", OperationsMonitor())
registry.register("position_monitor", PositionMonitor())
registry.register("latency_monitor", LatencyMonitor())

core = MonitorCore(registry=registry)

@app.route("/monitors", methods=["GET"])
def list_monitors():
    log.route("📜 Listing all registered monitors", source="API")
    return jsonify(sorted(registry.get_all_monitors().keys()))

@app.route("/monitor/<name>", methods=["POST"])
def run_monitor(name):
    log.banner(f"🚨 API Triggered: {name}")
    if name not in registry.get_all_monitors():
        log.warning(f"❌ Unknown monitor: {name}", source="API")
        return jsonify({"error": f"Monitor '{name}' not found"}), 404

    try:
        monitor = registry.get(name)
        monitor.run_cycle()
        log.success(f"✅ Monitor '{name}' executed via API", source="API")
        return jsonify({"status": "success", "monitor": name})
    except Exception as e:
        log.error(f"❌ Failed to run monitor '{name}'", source="API", payload={"error": str(e)})
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/monitor/all", methods=["POST"])
def run_all_monitors():
    log.banner("🚦 API Trigger: Running ALL Monitors")
    try:
        core.run_all()
        log.success("✅ All monitors ran successfully via API", source="API")
        return jsonify({"status": "success", "monitors": list(registry.get_all_monitors().keys())})
    except Exception as e:
        log.error("❌ Core execution failure", source="API", payload={"error": str(e)})
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    log.banner("🌐 Starting Monitor API Server")
    log.print_dashboard_link()
    app.run(host="0.0.0.0", port=5001)
