
# sonic_labs_bp.py

from flask import Blueprint, jsonify, current_app, request, render_template
import os
from jinja2 import ChoiceLoader, FileSystemLoader
import json
from positions.position_sync_service import PositionSyncService  # noqa: F401
from positions.position_core_service import PositionCoreService  # noqa: F401
from core.core_imports import retry_on_locked
from calc_core.calc_services import CalcServices
from app.system_bp import hedge_calculator_page, hedge_report_page

# Mapping tables for simple icon lookups used on the UI
ASSET_IMAGE_MAP = {
    "BTC": "btc_logo.png",
    "ETH": "eth_logo.png",
    "SOL": "sol_logo.png",
}
DEFAULT_ASSET_IMAGE = "unknown.png"

WALLET_IMAGE_MAP = {
    "ObiVault": "obivault.jpg",
    "R2Vault": "r2vault.jpg",
    "C3P0Vault": "c3povault.jpg",
    "JabbaVault": "jabbavault.jpg",
    "ChewieVault": "chewbaccavault.jpg",
    "PalpatineVault": "jabbavault.jog",
    "LukeVault": "lukevault.jg",
    "LandoVault": "landovault.jpg",
    "VaderVault": "vadervault.jpg",
    "YodaVault": "yodavault.jpg",
    "BobaVault": "bobavault.jpg",
    "LeiaVault": "leiavault.jpg",
    "LandoVaultz": "landovault.jpg",
}
DEFAULT_WALLET_IMAGE = "unknown_wallet.jpg"

sonic_labs_bp = Blueprint("sonic_labs", __name__, template_folder="templates")

# Allow this blueprint to locate templates when used in isolation
ROOT_TEMPLATES = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
sonic_labs_bp.jinja_loader = ChoiceLoader([
    FileSystemLoader(ROOT_TEMPLATES),
])

@sonic_labs_bp.route("/hedge_calculator", methods=["GET"])
@retry_on_locked()
def hedge_calculator():
    """Delegate to the system blueprint implementation."""
    return hedge_calculator_page()


@sonic_labs_bp.route("/hedge_report", methods=["GET"])
@retry_on_locked()
def hedge_report():
    """Delegate to the system blueprint implementation for hedge report."""
    return hedge_report_page()

@sonic_labs_bp.route("/sonic_sauce", methods=["GET"])
def get_sonic_sauce():
    try:
        dl = current_app.data_locker
        hedge_mods = dl.modifiers.get_all_modifiers("hedge_modifiers")
        heat_mods = dl.modifiers.get_all_modifiers("heat_modifiers")
        return jsonify({"hedge_modifiers": hedge_mods, "heat_modifiers": heat_mods}), 200
    except Exception as e:
        current_app.logger.error(f"Error loading sonic sauce: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@sonic_labs_bp.route("/sonic_sauce", methods=["POST"])
def update_sonic_sauce():
    try:
        data = request.get_json() or {}
        if not isinstance(data, dict):
            return jsonify({"error": "Invalid payload"}), 400
        dl = current_app.data_locker
        for group, mods in data.items():
            if not isinstance(mods, dict):
                continue
            for key, value in mods.items():
                dl.modifiers.set_modifier(key, float(value), group=group)
        return jsonify({"success": True}), 200
    except Exception as e:
        current_app.logger.error(f"Error saving sonic sauce: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@sonic_labs_bp.route("/hedge_labs", methods=["GET"])
@retry_on_locked()
def hedge_labs_page():
    """Render the Hedge Labs UI."""
    dl = current_app.data_locker
    hedges = dl.hedges.get_hedges() or []

    def hedge_to_dict(h):
        asset_img = DEFAULT_ASSET_IMAGE
        wallet_img = DEFAULT_WALLET_IMAGE
        long_pos = None
        short_pos = None
        if h.positions:
            for pid in h.positions:
                pos = dl.positions.get_position_by_id(pid)
                if not pos:
                    continue
                ptype = str(pos.get("position_type") or "").lower()
                if ptype == "long" and long_pos is None:
                    long_pos = pos
                elif ptype == "short" and short_pos is None:
                    short_pos = pos
            ref_pos = long_pos or short_pos
            if ref_pos:
                asset_key = str(ref_pos.get("asset_type") or "").upper()
                asset_img = ASSET_IMAGE_MAP.get(asset_key, DEFAULT_ASSET_IMAGE)
                wallet_name = ref_pos.get("wallet_name") or ref_pos.get("wallet")
                wallet_img = WALLET_IMAGE_MAP.get(wallet_name, DEFAULT_WALLET_IMAGE)
        total_size = abs(h.total_long_size) + abs(h.total_short_size)
        long_ratio = int(round(abs(h.total_long_size) / total_size * 100)) if total_size else 0
        short_ratio = int(round(abs(h.total_short_size) / total_size * 100)) if total_size else 0
        return {
            "id": h.id,
            "positions": h.positions,
            "total_long_size": h.total_long_size,
            "total_short_size": h.total_short_size,
            "long_size_ratio": long_ratio,
            "short_size_ratio": short_ratio,
            "long_heat_index": h.long_heat_index,
            "short_heat_index": h.short_heat_index,
            "total_heat_index": h.total_heat_index,
            "long_leverage": float(long_pos.get("leverage", 0.0)) if long_pos else 0.0,
            "short_leverage": float(short_pos.get("leverage", 0.0)) if short_pos else 0.0,
            "total_value": (
                (float(long_pos.get("value", 0.0)) if long_pos else 0.0)
                + (float(short_pos.get("value", 0.0)) if short_pos else 0.0)
            ),
            "asset_image": asset_img,
            "wallet_image": wallet_img,
            "created_at": h.created_at.isoformat() if hasattr(h.created_at, "isoformat") else h.created_at,
            "updated_at": h.updated_at.isoformat() if hasattr(h.updated_at, "isoformat") else h.updated_at,
            "notes": h.notes,
        }

    hedges_data = [hedge_to_dict(h) for h in hedges]
    theme_config = dl.system.get_active_theme_profile() or {}
    return render_template(
        "hedge_labs.html",
        hedges=hedges_data,
        theme=theme_config,
    )


@sonic_labs_bp.route("/api/hedges", methods=["GET"])
@retry_on_locked()
def api_get_hedges():
    """Return current hedges as JSON."""
    dl = current_app.data_locker
    hedges = dl.hedges.get_hedges() or []

    def hedge_info(h):
        asset_img = DEFAULT_ASSET_IMAGE
        wallet_img = DEFAULT_WALLET_IMAGE
        long_pos = None
        short_pos = None
        if h.positions:
            for pid in h.positions:
                pos = dl.positions.get_position_by_id(pid)
                if not pos:
                    continue
                ptype = str(pos.get("position_type") or "").lower()
                if ptype == "long" and long_pos is None:
                    long_pos = pos
                elif ptype == "short" and short_pos is None:
                    short_pos = pos
            ref_pos = long_pos or short_pos
            if ref_pos:
                asset_key = str(ref_pos.get("asset_type") or "").upper()
                asset_img = ASSET_IMAGE_MAP.get(asset_key, DEFAULT_ASSET_IMAGE)
                wallet_name = ref_pos.get("wallet_name") or ref_pos.get("wallet")
                wallet_img = WALLET_IMAGE_MAP.get(wallet_name, DEFAULT_WALLET_IMAGE)
        total_size = abs(h.total_long_size) + abs(h.total_short_size)
        long_ratio = int(round(abs(h.total_long_size) / total_size * 100)) if total_size else 0
        short_ratio = int(round(abs(h.total_short_size) / total_size * 100)) if total_size else 0
        return {
            "id": h.id,
            "positions": h.positions,
            "total_long_size": h.total_long_size,
            "total_short_size": h.total_short_size,
            "long_size_ratio": long_ratio,
            "short_size_ratio": short_ratio,
            "total_heat_index": h.total_heat_index,
            "long_leverage": float(long_pos.get("leverage", 0.0)) if long_pos else 0.0,
            "short_leverage": float(short_pos.get("leverage", 0.0)) if short_pos else 0.0,
            "total_value": (
                (float(long_pos.get("value", 0.0)) if long_pos else 0.0)
                + (float(short_pos.get("value", 0.0)) if short_pos else 0.0)
            ),
            "asset_image": asset_img,
            "wallet_image": wallet_img,
        }

    data = [hedge_info(h) for h in hedges]
    return jsonify({"hedges": data})


@sonic_labs_bp.route("/api/link_hedges", methods=["POST"])
@retry_on_locked()
def api_link_hedges():
    """Link hedges using HedgeCore."""
    try:
        from hedge_core.hedge_core import HedgeCore

        core = HedgeCore(current_app.data_locker)
        groups = core.link_hedges()
        return jsonify({"linked": len(groups)})
    except Exception as e:
        current_app.logger.error(f"Error linking hedges: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@sonic_labs_bp.route("/api/unlink_hedges", methods=["POST"])
@retry_on_locked()
def api_unlink_hedges():
    """Unlink all hedges."""
    try:
        from hedge_core.hedge_core import HedgeCore

        core = HedgeCore(current_app.data_locker)
        core.unlink_hedges()
        return jsonify({"unlinked": True})
    except Exception as e:
        current_app.logger.error(f"Error unlinking hedges: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@sonic_labs_bp.route("/api/test_calcs", methods=["GET"])
@retry_on_locked()
def api_test_calcs():
    """Run basic calculation tests and return results."""
    try:
        from calc_core.calculation_core import CalculationCore

        dl = current_app.data_locker
        positions = dl.positions.get_active_positions() or []
        core = CalculationCore(dl)
        totals = core.calculate_totals(positions)
        return jsonify({"totals": totals})
    except Exception as e:
        current_app.logger.error(f"Error running test calcs: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@sonic_labs_bp.route("/api/hedge_positions", methods=["GET"])
@retry_on_locked()
def api_get_hedge_positions():
    """Return position data for a specific hedge."""
    hedge_id = request.args.get("hedge_id")
    if not hedge_id:
        return jsonify({"error": "hedge_id required"}), 400

    dl = current_app.data_locker
    hedges = dl.hedges.get_hedges() or []
    hedge = next((h for h in hedges if str(h.id) == hedge_id), None)
    if not hedge:
        return jsonify({"error": "Hedge not found"}), 404

    pos_list = []
    for pid in hedge.positions:
        pos = dl.positions.get_position_by_id(pid)
        if pos:
            pos_list.append(dict(pos))

    return jsonify({"positions": pos_list})


@sonic_labs_bp.route("/api/evaluate_hedge", methods=["GET"])
@retry_on_locked()
def api_evaluate_hedge():
    """Evaluate hedge positions at a specific price."""
    hedge_id = request.args.get("hedge_id")
    price = request.args.get("price")
    if not hedge_id or price is None:
        return jsonify({"error": "hedge_id and price required"}), 400

    try:
        price = float(price)
    except ValueError:
        return jsonify({"error": "invalid price"}), 400

    dl = current_app.data_locker
    hedges = dl.hedges.get_hedges() or []
    hedge = next((h for h in hedges if str(h.id) == hedge_id), None)
    if not hedge:
        return jsonify({"error": "Hedge not found"}), 404

    calc = CalcServices()
    results = {}
    eval_positions = []

    for pid in hedge.positions:
        pos = dl.positions.get_position_by_id(pid)
        if not pos:
            continue
        eval_data = calc.evaluate_at_price(pos, price)
        ptype = str(pos.get("position_type", "")).lower()
        results[ptype] = {
            "id": pid,
            **{k: round(v, 6) if isinstance(v, float) else v for k, v in eval_data.items()},
        }
        pos_copy = dict(pos)
        pos_copy.update(eval_data)
        eval_positions.append(pos_copy)

    totals = calc.calculate_totals(eval_positions)

    return jsonify({"long": results.get("long"), "short": results.get("short"), "totals": totals})


# -----------------------------------------------------------
# Playwright Test Page and API
# -----------------------------------------------------------

@sonic_labs_bp.route("/playwright_test", methods=["GET"])
def playwright_test_page():
    """Render the Phantom/Playwright test page."""
    return render_template("playwright_test.html")


@sonic_labs_bp.route("/api/run_playwright_test", methods=["POST"])
def api_run_playwright_test():
    """Execute a simple Playwright workflow using Phantom."""
    phantom_path = current_app.config.get("PHANTOM_PATH")
    profile_dir = current_app.config.get("PW_PROFILE_DIR", "/tmp/playwright-profile")
    if not phantom_path:
        return jsonify({"error": "Phantom path not configured"}), 400

    try:
        from auto_core import AutoCore
    except Exception as e:  # ModuleNotFoundError for missing playwright
        current_app.logger.error(
            f"Playwright dependencies missing: {e}", exc_info=True
        )
        return jsonify({"error": "Playwright is not installed"}), 500

    try:
        core = AutoCore(phantom_path, profile_dir, headless=True)
        core.deposit_collateral(0.01)
        return jsonify({"message": "Playwright test executed"})
    except Exception as e:
        current_app.logger.error(f"Playwright test failed: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


# -----------------------------------------------------------
# Order Factory Page
# -----------------------------------------------------------

@sonic_labs_bp.route("/order_factory", methods=["GET"])
def order_factory_page():
    """Render the OrderCore layout demo."""
    return render_template("order_factory.html")


def get_order_core():
    """Return or create the shared OrderCore instance."""
    core = getattr(current_app, "order_core", None)
    if core is None:
        from order_core.order_core import OrderCore
        from config.config_loader import load_config

        core = OrderCore(current_app.data_locker, load_config)
        current_app.order_core = core
    return core


@sonic_labs_bp.route("/api/order_core_launch", methods=["POST"])
def api_order_core_launch():
    """Launch OrderCore with the configured wallet."""
    data = request.get_json() or {}
    extension_path = data.get("extension_path") or current_app.config.get("PHANTOM_PATH")
    wallet_type = data.get("wallet_type", "phantom")
    phantom_password = data.get("phantom_password")
    solflare_password = data.get("solflare_password")
    headless = data.get("headless", True)

    core = get_order_core()
    try:
        import asyncio

        asyncio.run(
            core.launch(
                extension_path=extension_path,
                headless=headless,
                phantom_password=phantom_password,
                solflare_password=solflare_password,
            )
        )
        return jsonify({"message": "OrderCore launched"})
    except Exception as e:
        current_app.logger.error(f"OrderCore launch failed: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@sonic_labs_bp.route("/api/order_engine_action", methods=["POST"])
def api_order_engine_action():
    """Execute a single OrderEngine action."""
    data = request.get_json() or {}
    action = data.get("action")
    value = data.get("value")

    if not action:
        return jsonify({"error": "Missing action"}), 400

    core = get_order_core()
    engine = getattr(core, "engine", None)
    if engine is None:
        return jsonify({"error": "OrderCore not launched"}), 400

    func = getattr(engine, action, None)
    if func is None:
        return jsonify({"error": f"Unknown action: {action}"}), 400

    try:
        import asyncio

        if asyncio.iscoroutinefunction(func):
            if value is not None:
                asyncio.run(func(value))
            else:
                asyncio.run(func())
        else:
            if value is not None:
                func(value)
            else:
                func()
        return jsonify({"message": f"{action} executed"})
    except Exception as e:
        current_app.logger.error(f"OrderEngine action error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@sonic_labs_bp.route("/api/order_sequence", methods=["POST"])
def api_order_sequence():
    """Run a composite OrderSequencer flow."""
    data = request.get_json() or {}
    flow = data.get("flow")
    params = data.get("params") or {}

    if not flow:
        return jsonify({"error": "Missing flow"}), 400

    core = get_order_core()
    seq = getattr(core, "sequencer", None)
    if seq is None:
        return jsonify({"error": "OrderCore not launched"}), 400

    func = getattr(seq, flow, None)
    if func is None:
        return jsonify({"error": f"Unknown flow: {flow}"}), 400

    try:
        import asyncio

        if asyncio.iscoroutinefunction(func):
            result = asyncio.run(func(**params))
        else:
            result = func(**params)
        return jsonify({"message": "flow executed", "result": str(result)})
    except Exception as e:
        current_app.logger.error(f"OrderSequencer flow error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
