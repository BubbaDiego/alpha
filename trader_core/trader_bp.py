
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Blueprint, current_app, jsonify, render_template, redirect, request
from utils.console_logger import ConsoleLogger as log

trader_bp = Blueprint("trader_bp", __name__, url_prefix="/trader")

@trader_bp.route("/shop", endpoint="trader_shop")
def trader_shop():
    return render_template("trader_shop.html")


@trader_bp.route("/api/wallets", methods=["GET"])
def trader_wallets():
    """Return wallets for dropdown selections."""
    try:
        wallets = current_app.data_locker.read_wallets()
        simple = [
            {"name": w.get("name"), "balance": w.get("balance", 0.0)} for w in wallets
        ]
        return jsonify({"success": True, "wallets": simple})
    except Exception as e:
        log.error(f"❌ Failed to list wallets: {e}", source="API")
        return jsonify({"success": False, "error": str(e)}), 500

@trader_bp.route("/api/traders/create", methods=["POST"])
def create_trader():
    try:
        data = request.get_json()
        log.debug("Received create trader payload", source="API", payload=data)

        if not data or "name" not in data:
            log.warning("Missing 'name' in trader creation request", source="API")
            return jsonify({"success": False, "error": "Trader name required"}), 400

        # Try to parse strategy_weights if needed
        if isinstance(data.get("strategy_weights"), str):
            try:
                import json
                weights = json.loads(data["strategy_weights"])
                if isinstance(weights, dict):
                    data["strategy_weights"] = weights
                    log.debug("Parsed strategy_weights as JSON dict", source="API", payload=weights)
                else:
                    raise ValueError("strategy_weights is not a dict")
            except Exception as e:
                log.warning(f"⚠️ Could not parse strategy_weights: {e}", source="API")
                data["strategy_weights"] = {}

        # Call DLTraderManager directly
        manager = current_app.data_locker.traders
        manager.create_trader(data)

        log.success(f"✅ Trader created: {data['name']}", source="API")
        return jsonify({"success": True})

    except Exception as e:
        import traceback
        log.error(f"❌ Exception in trader creation: {e}", source="API")
        log.debug(traceback.format_exc(), source="API")
        return jsonify({"success": False, "error": str(e)}), 500

@trader_bp.route("/api/traders/<name>", methods=["GET"])
def get_trader(name):
    try:
        log.info(f"Fetching trader: {name}", source="API")
        trader = current_app.data_locker.traders.get_trader_by_name(name)
        if not trader:
            log.warning(f"Trader not found: {name}", source="API")
            return jsonify({"success": False, "error": "Trader not found"}), 404
        return jsonify({"success": True, "trader": trader})
    except Exception as e:
        log.error(f"❌ Failed to fetch trader: {e}", source="API")
        return jsonify({"success": False, "error": str(e)}), 500

@trader_bp.route("/api/traders", methods=["GET"])
def list_traders():
    try:
        log.info("Listing all traders", source="API")
        traders = current_app.data_locker.traders.list_traders()
        for t in traders:
            wallet_name = t.get("wallet")
            if wallet_name:
                w = current_app.data_locker.get_wallet_by_name(wallet_name)
                if w:
                    t["wallet_balance"] = w.get("balance", 0.0)
        return jsonify({"success": True, "traders": traders})
    except Exception as e:
        log.error(f"❌ Failed to list traders: {e}", source="API")
        return jsonify({"success": False, "error": str(e)}), 500

@trader_bp.route("/api/traders/<name>", methods=["PUT"])
def update_trader(name):
    try:
        fields = request.get_json()
        log.debug(f"Updating trader {name}", source="API", payload=fields)
        current_app.data_locker.traders.update_trader(name, fields)
        return jsonify({"success": True})
    except Exception as e:
        log.error(f"❌ Failed to update trader: {e}", source="API")
        return jsonify({"success": False, "error": str(e)}), 500

@trader_bp.route("/api/traders/<name>/delete", methods=["DELETE"])
def delete_trader(name):
    try:
        log.info(f"Deleting trader: {name}", source="API")
        current_app.data_locker.traders.delete_trader(name)
        return jsonify({"success": True})
    except Exception as e:
        log.error(f"❌ Failed to delete trader: {e}", source="API")
        return jsonify({"success": False, "error": str(e)}), 500
