
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Blueprint, current_app, jsonify, render_template, redirect, request
from datetime import datetime
from utils.console_logger import ConsoleLogger as log
from trader_core.mood_engine import evaluate_mood
from calc_core.calc_services import CalcServices
from oracle_core.persona_manager import PersonaManager
from wallets.wallet_core import WalletCore


def _enrich_trader(trader: dict, dl, pm: PersonaManager, calc: CalcServices) -> dict:
    """Add wallet balance, heat index, performance and mood."""
    name = trader.get("name")
    try:
        persona = pm.get(name)
    except KeyError:
        log.warning(f"Persona not found for trader: {name}", source="TraderBP")
        persona = None
    wallet_name = trader.get("wallet") or (
        (persona.name + "Vault") if persona else f"{name}Vault"
    )

    wallet_info = None
    if hasattr(dl, "get_wallet_by_name"):
        try:
            wallet_info = dl.get_wallet_by_name(wallet_name)
        except Exception as exc:
            log.debug(f"Wallet lookup failed: {exc}", source="TraderBP")
    if wallet_info:
        trader["public_address"] = wallet_info.get("public_address", "")

    positions = []
    if hasattr(dl, "positions"):
        pos_mgr = dl.positions
        if hasattr(pos_mgr, "get_active_positions_by_wallet"):
            positions = pos_mgr.get_active_positions_by_wallet(wallet_name) or []
        else:
            positions = pos_mgr.get_all_positions() or []

    try:
        balance = sum(float(p.get("value") or 0.0) for p in positions)
        profit = sum(calc.calculate_profit(p) for p in positions)
        trader["wallet_balance"] = round(balance, 2)
        trader["profit"] = round(profit, 2)
    except Exception as exc:
        trader["wallet_balance"] = 0.0
        trader["profit"] = 0.0
        log.debug(f"Balance/profit calculation failed: {exc}", source="TraderBP")

    avg_heat = calc.calculate_weighted_heat_index(positions)
    trader["heat_index"] = avg_heat
    trader["performance_score"] = max(0, int(100 - avg_heat))
    trader["mood"] = evaluate_mood(avg_heat, getattr(persona, "moods", {}))
    return trader

trader_bp = Blueprint("trader_bp", __name__, url_prefix="/trader")

@trader_bp.route("/shop", endpoint="trader_shop")
def trader_shop():
    return render_template("trader_shop.html")


@trader_bp.route("/api/wallets", methods=["GET"])
def trader_wallets():
    """Return wallets for dropdown selections."""
    try:
        wc = getattr(getattr(current_app, "system_core", None), "wallet_core", None) or WalletCore()
        try:
            wc.refresh_wallet_balances()
        except Exception as exc:
            log.debug(f"Wallet refresh failed: {exc}", source="TraderBP")

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

        # Add creation timestamp and initial collateral
        data["born_on"] = datetime.now().isoformat()
        wallet_name = data.get("wallet")
        wallet = current_app.data_locker.get_wallet_by_name(wallet_name) if wallet_name else None
        data["initial_collateral"] = wallet.get("balance", 0.0) if wallet else 0.0

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

        pm = PersonaManager()
        calc = CalcServices()
        trader = _enrich_trader(trader, current_app.data_locker, pm, calc)

        return jsonify({"success": True, "trader": trader})
    except Exception as e:
        log.error(f"❌ Failed to fetch trader: {e}", source="API")
        return jsonify({"success": False, "error": str(e)}), 500

@trader_bp.route("/api/traders", methods=["GET"])
def list_traders():
    try:
        log.info("Listing all traders", source="API")
        wc = getattr(getattr(current_app, "system_core", None), "wallet_core", None) or WalletCore()
        try:
            wc.refresh_wallet_balances()
        except Exception as exc:
            log.debug(f"Wallet refresh failed: {exc}", source="TraderBP")

        traders = current_app.data_locker.traders.list_traders()
        pm = PersonaManager()
        calc = CalcServices()
        enriched = [_enrich_trader(t, current_app.data_locker, pm, calc) for t in traders]
        return jsonify({"success": True, "traders": enriched})
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
        deleted = current_app.data_locker.traders.delete_trader(name)
        if not deleted:
            log.warning(f"Trader not found for deletion: {name}", source="API")
            return jsonify({"success": False, "error": "Trader not found"}), 404
        return jsonify({"success": True})
    except Exception as e:
        log.error(f"❌ Failed to delete trader: {e}", source="API")
        return jsonify({"success": False, "error": str(e)}), 500
