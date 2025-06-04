# 🔌 system_bp.py — Blueprint for SystemCore wallet + theme endpoints

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json
from flask import (
    Blueprint,
    request,
    render_template,
    redirect,
    url_for,
    flash,
    jsonify,
    current_app,
)
from jinja2 import ChoiceLoader, FileSystemLoader
from werkzeug.utils import secure_filename

# from config.alert_thresholds_json import legacy_alert_thresholds  # Simulating legacy load

from system.system_core import SystemCore
from data.dl_thresholds import DLThresholdManager
from data.models import AlertThreshold
from wallets.wallet_schema import WalletIn
from positions.position_core import PositionCore
from positions.hedge_manager import HedgeManager
from utils.template_filters import short_datetime

UPLOAD_FOLDER = os.path.join("static", "uploads", "wallets")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

system_bp = Blueprint(
    "system",
    __name__,
    url_prefix="/system",
    template_folder="../templates",
)

# Register template filters when the blueprint is attached to an app.
system_bp.add_app_template_filter(short_datetime, "short_datetime")

# Allow this blueprint to find templates in the project's main templates
# directory when used within standalone test applications.
ROOT_TEMPLATES = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
system_bp.jinja_loader = ChoiceLoader([
    FileSystemLoader(ROOT_TEMPLATES),
])


def get_core():
    """Return the shared SystemCore instance."""
    core = getattr(current_app, "system_core", None)
    if core is None:
        core = SystemCore(current_app.data_locker)
        current_app.system_core = core
    return core


@system_bp.route("/test_xcom", methods=["POST"])
def test_xcom():
    try:
        from xcom.xcom_core import XComCore
        from xcom.sound_service import SoundService

        mode = request.form.get("mode")
        dl = current_app.data_locker
        xcom = XComCore(dl.system)

        msg = "📡 Live test from XCom Settings page."

        if mode == "sms":
            xcom.send_notification("MEDIUM", "Test SMS", msg)
        elif mode == "email":
            xcom.send_notification("LOW", "Test Email", msg)
        elif mode == "voice":
            from xcom.check_twilio_heartbeat_service import CheckTwilioHeartbeatService

            api_cfg = xcom.config_service.get_provider("api") or {}
            CheckTwilioHeartbeatService(api_cfg).check(dry_run=False)
        elif mode == "system":
            SoundService().play()

        flash(f"✅ XCom test ({mode}) dispatched.", "success")
    except Exception as e:
        flash(f"❌ Failed to send XCom test: {e}", "danger")

    return redirect(url_for("system.xcom_config_page"))


# 🌐 List meta data
@system_bp.route("/metadata", methods=["GET"])
def system_metadata():
    try:
        core = get_core()
        metadata = core.get_strategy_metadata()
        return jsonify(metadata)
    except Exception as e:
        log.error(f"Failed to fetch system metadata: {e}", source="SystemBP")
        return jsonify({"error": str(e)}), 500


# 🌐 List all wallets
@system_bp.route("/wallets", methods=["GET"])
def list_wallets():
    core = get_core()
    wallets = core.wallet_core.load_wallets()
    return render_template("wallets/wallet_manager.html", wallets=wallets)


# ➕ Add a wallet
@system_bp.route("/wallets/add", methods=["POST"])
def add_wallet():
    try:
        form = request.form
        file = request.files.get("image_file")
        filename = None

        if file and file.filename:
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

        image_path = (
            f"/static/uploads/wallets/{filename}"
            if filename
            else form.get("image_path")
        )

        data = WalletIn(
            name=form.get("name"),
            public_address=form.get("public_address"),
            private_address=form.get("private_address"),
            image_path=image_path,
            balance=float(form.get("balance", 0.0)),
            tags=[t.strip() for t in form.get("tags", "").split(",") if t.strip()],
            is_active=form.get("is_active", "off") == "on",
            type=form.get("type", "personal"),
        )

        get_core().wallets.create_wallet(data)
        flash("✅ Wallet added!", "success")

    except Exception as e:
        flash(f"❌ Failed to add wallet: {e}", "danger")

    return redirect(url_for("system.list_wallets"))


# 🗑️ Delete wallet
@system_bp.route("/wallets/delete/<name>", methods=["POST"])
def delete_wallet(name):
    try:
        get_core().wallets.delete_wallet(name)
        flash("🗑️ Wallet deleted.", "info")
    except Exception as e:
        flash(f"❌ Delete failed: {e}", "danger")
    return redirect(url_for("system.list_wallets"))


# 💾 Export wallets to JSON
@system_bp.route("/wallets/export", methods=["POST"])
def export_wallets():
    try:
        get_core().wallets.export_wallets()
        flash("💾 Exported to wallets.json", "success")
    except Exception as e:
        flash(f"❌ Export failed: {e}", "danger")
    return redirect(url_for("system.list_wallets"))


# ♻️ Import from JSON
@system_bp.route("/wallets/import", methods=["POST"])
def import_wallets():
    try:
        count = get_core().wallets.import_wallets()
        flash(f"♻️ Imported {count} wallets from JSON", "success")
    except Exception as e:
        flash(f"❌ Import failed: {e}", "danger")
    return redirect(url_for("system.list_wallets"))


# 💉 Inject wallets from backup JSON using insert_wallets script
@system_bp.route("/wallets/inject", methods=["POST"])
def inject_wallets():
    """Run the wallet DB injection script."""
    try:
        from scripts.insert_wallets import main as insert_wallets_main

        result = insert_wallets_main([])
        if result == 0:
            flash("💉 Wallets injected from backup.", "success")
        else:
            flash("⚠️ Wallet injection completed with errors.", "warning")
    except Exception as e:  # pragma: no cover - best effort
        flash(f"❌ Wallet injection failed: {e}", "danger")
    return redirect(url_for("system.list_wallets"))


# ✏️ Update wallet (from modal)
@system_bp.route("/wallets/update/<name>", methods=["POST"])
def update_wallet(name):
    try:
        form = request.form

        data = WalletIn(
            name=name,
            public_address=form.get("public_address"),
            private_address=form.get("private_address"),
            image_path=form.get("image_path"),
            balance=float(form.get("balance", 0.0)),
            tags=[t.strip() for t in form.get("tags", "").split(",") if t.strip()],
            is_active="is_active" in form,
            type=form.get("type", "personal"),
        )

        get_core().wallets.update_wallet(name, data)
        flash(f"💾 Updated wallet '{name}'", "success")
    except Exception as e:
        flash(f"❌ Failed to update wallet '{name}': {e}", "danger")
    return redirect(url_for("system.list_wallets"))


# 💵 Deposit collateral via Jupiter
@system_bp.route("/wallets/jupiter/deposit", methods=["POST"])
def deposit_collateral():
    try:
        wallet_name = request.form.get("wallet_name")
        market = request.form.get("market")
        amount = float(request.form.get("amount", 0.0))
        wallet = get_core().wallets.get_wallet(wallet_name)
        result = get_core().wallet_core.deposit_collateral(wallet, market, amount)
        sig = result.get("txSig") if isinstance(result, dict) else result
        flash(f"✅ Deposit transaction sent: {sig}", "success")
    except Exception as e:
        flash(f"❌ Deposit failed: {e}", "danger")
    return redirect(url_for("system.list_wallets"))


# 💸 Withdraw collateral via Jupiter
@system_bp.route("/wallets/jupiter/withdraw", methods=["POST"])
def withdraw_collateral():
    try:
        wallet_name = request.form.get("wallet_name")
        market = request.form.get("market")
        amount = float(request.form.get("amount", 0.0))
        wallet = get_core().wallets.get_wallet(wallet_name)
        result = get_core().wallet_core.withdraw_collateral(wallet, market, amount)
        sig = result.get("txSig") if isinstance(result, dict) else result
        flash(f"✅ Withdraw transaction sent: {sig}", "success")
    except Exception as e:
        flash(f"❌ Withdraw failed: {e}", "danger")
    return redirect(url_for("system.list_wallets"))


# === 🎨 Theme Profile Routes ===


# 🔍 GET: All saved theme profiles
@system_bp.route("/themes", methods=["GET"])
def list_themes():
    try:
        core = get_core()
        profiles = core.get_all_profiles()
        return jsonify(profiles)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 💾 POST: Save or update a theme profile
@system_bp.route("/themes", methods=["POST"])
def save_theme():
    try:
        data = request.get_json()
        if not isinstance(data, dict) or not data:
            return jsonify({"error": "Invalid theme payload"}), 400

        for name, config in data.items():
            get_core().save_profile(name, config)

        return jsonify({"message": "Profile(s) saved."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ❌ DELETE: Remove a theme profile
@system_bp.route("/themes/<name>", methods=["DELETE"])
def delete_theme(name):
    try:
        get_core().delete_profile(name)
        return jsonify({"message": f"Theme '{name}' deleted."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🌟 POST: Set a profile as active
@system_bp.route("/themes/activate/<name>", methods=["POST"])
def activate_theme(name):
    try:
        get_core().set_active_profile(name)
        return jsonify({"message": f"Theme '{name}' set as active."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🎯 GET: Active theme profile
@system_bp.route("/themes/active", methods=["GET"])
def get_active_theme():
    try:
        profile = get_core().get_active_profile()
        return jsonify(profile)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@system_bp.route("/themes/editor", methods=["GET"])
def theme_editor_page():
    try:
        core = get_core()
        profiles = core.get_all_profiles()
        active = core.get_active_profile()
        return render_template(
            "system/theme_builder.html", profiles=profiles, active=active
        )
    except Exception as e:
        return render_template("system/theme_builder.html", profiles={}, active={})


# 🌗 Get/set theme mode
@system_bp.route("/theme_mode", methods=["GET", "POST"])
def theme_mode():
    core = get_core()
    if request.method == "POST":
        data = request.get_json()
        core.set_theme_mode(data.get("theme_mode"))
        return jsonify(success=True)
    else:
        return jsonify(theme_mode=core.get_theme_mode())


# 🎨 Get/save theme config
@system_bp.route("/theme_config", methods=["GET", "POST"])
def theme_config():
    core = get_core()

    if request.method == "GET":
        try:
            profiles = core.get_all_profiles()
            return jsonify(profiles)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    elif request.method == "POST":
        try:
            payload = request.get_json()
            if not isinstance(payload, dict):
                return jsonify({"error": "Invalid theme config"}), 400

            for name, config in payload.items():
                core.save_profile(name, config)

            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"error": str(e)}), 500


@system_bp.route("/seed_all_thresholds", methods=["POST", "GET"])
def seed_all_thresholds():
    from data.dl_thresholds import DLThresholdManager
    from data.models import AlertThreshold
    from uuid import uuid4
    from datetime import datetime, timezone

    try:
        now = datetime.now(timezone.utc).isoformat()
        locker = current_app.data_locker
        dl_mgr = DLThresholdManager(locker.db)

        definitions = [
            # === Portfolio Metrics
            ("TotalValue", "Portfolio", "total_value", 10000, 25000, 50000, "ABOVE"),
            ("TotalSize", "Portfolio", "total_size", 10000, 50000, 100000, "ABOVE"),
            ("AvgLeverage", "Portfolio", "avg_leverage", 2, 5, 10, "ABOVE"),
            ("AvgTravelPercent", "Portfolio", "avg_travel_percent", -10, -5, 0, "ABOVE"),
            (
                "ValueToCollateralRatio",
                "Portfolio",
                "value_to_collateral_ratio",
                1.1,
                1.5,
                2.0,
                "BELOW",
            ),
            ("TotalHeat", "Portfolio", "total_heat_index", 30, 60, 90, "ABOVE"),
            # === Position Metrics
            ("Profit", "Position", "profit", 10, 25, 50, "ABOVE"),
            ("HeatIndex", "Position", "heat_index", 30, 60, 90, "ABOVE"),
            ("TravelPercentLiquid", "Position", "travel_percent_liquid", -20, -10, 0, "BELOW"),
            ("LiquidationDistance", "Position", "liquidation_distance", 10, 5, 2, "BELOW"),
            # === Market Metrics
            ("PriceThreshold", "Market", "current_price", 20000, 30000, 40000, "ABOVE"),
        ]

        created = 0
        for alert_type, alert_class, metric_key, low, med, high, condition in definitions:
            threshold = AlertThreshold(
                id=str(uuid4()),
                alert_type=alert_type,
                alert_class=alert_class,
                metric_key=metric_key,
                condition=condition,
                low=low,
                medium=med,
                high=high,
                enabled=True,
                last_modified=now,
            )
            if dl_mgr.insert(threshold):
                created += 1

        return jsonify({"status": "ok", "created": created})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@system_bp.route("/database_viewer", methods=["GET"])
def database_viewer():
    try:
        datasets = current_app.data_locker.get_all_tables_as_dict()
        return render_template("db_viewer.html", datasets=datasets)
    except Exception as e:
        flash(f"❌ Error loading DB viewer: {e}", "danger")
        return render_template("db_viewer.html", datasets={})


@system_bp.route("/modifiers/<group>", methods=["GET"])
def get_modifiers(group):
    """Return all modifiers for a group."""
    try:
        mods = current_app.data_locker.modifiers.get_all_modifiers(group)
        return jsonify(mods)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@system_bp.route("/modifiers/<group>", methods=["POST"])
def update_modifiers(group):
    """Update modifiers for a group."""
    try:
        payload = request.get_json() or {}
        if not isinstance(payload, dict):
            return jsonify({"error": "Invalid payload"}), 400
        dl = current_app.data_locker
        for key, value in payload.items():
            dl.modifiers.set_modifier(key, float(value), group=group)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@system_bp.route("/hedge_calculator", methods=["GET"])
def hedge_calculator_page():
    """Render the hedge calculator page."""
    try:
        dl = current_app.data_locker

        positions = []
        long_positions = []
        short_positions = []
        default_long_id = None
        default_short_id = None

        # Attempt to load active positions. Fallback to empty lists on failure.
        try:
            core = PositionCore(dl)
            positions = [
                p
                for p in (core.get_active_positions() or [])
                if str(p.get("status", "")).upper() == "ACTIVE"
            ]

            long_positions = [
                p
                for p in positions
                if str(p.get("position_type", "")).upper() == "LONG"
            ]
            short_positions = [
                p
                for p in positions
                if str(p.get("position_type", "")).upper() == "SHORT"
            ]

            hedges = HedgeManager(positions).get_hedges()
            if hedges:
                first = hedges[0]
                pos_map = {p.get("id"): p for p in positions}
                for pid in first.positions:
                    pos = pos_map.get(pid)
                    if not pos:
                        continue
                    ptype = str(pos.get("position_type", "")).upper()
                    if ptype == "LONG" and default_long_id is None:
                        default_long_id = pid
                    elif ptype == "SHORT" and default_short_id is None:
                        default_short_id = pid
                    if default_long_id and default_short_id:
                        break
        except Exception as e:
            current_app.logger.error(
                f"Failed to load positions for hedge calculator: {e}",
                exc_info=True,
            )

        # Load the active theme profile from the DB instead of a JSON file
        theme_config = {}
        if getattr(dl, "system", None) and hasattr(dl.system, "get_active_theme_profile"):
            try:
                theme_config = dl.system.get_active_theme_profile() or {}
            except Exception as e:
                current_app.logger.error(
                    f"Failed to load theme profile: {e}", exc_info=True
                )

        # Retrieve hedge and heat modifiers from the modifiers table
        hedge_mods = {}
        heat_mods = {}
        if getattr(dl, "modifiers", None) and hasattr(dl.modifiers, "get_all_modifiers"):
            try:
                hedge_mods = dl.modifiers.get_all_modifiers("hedge_modifiers")
                heat_mods = dl.modifiers.get_all_modifiers("heat_modifiers")
            except Exception as e:
                current_app.logger.error(
                    f"Failed to load modifiers: {e}", exc_info=True
                )
        modifiers = {"hedge_modifiers": hedge_mods, "heat_modifiers": heat_mods}

        return render_template(
            "hedge_modifiers.html",
            theme=theme_config,
            long_positions=long_positions,
            short_positions=short_positions,
            modifiers=modifiers,
            default_long_id=default_long_id,
            default_short_id=default_short_id,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@system_bp.route("/hedge_report", methods=["GET"])
def hedge_report_page():
    """Render the hedge report page with aggregated long/short data."""
    try:
        core = PositionCore(current_app.data_locker)
        positions = [
            p
            for p in (core.get_active_positions() or [])
            if str(p.get("status", "")).upper() == "ACTIVE"
        ]

        def build(group_positions, asset_name):
            from calc_core.calc_services import CalcServices
            totals = CalcServices().calculate_totals(group_positions)
            return {
                "asset": asset_name,
                "collateral": totals.get("total_collateral", 0.0),
                "value": totals.get("total_value", 0.0),
                "leverage": totals.get("avg_leverage", 0.0),
                "travel_percent": totals.get("avg_travel_percent", 0.0),
                "size": totals.get("total_size", 0.0),
            }

        heat_data = {}
        assets = ["BTC", "ETH", "SOL"]
        for asset in assets:
            asset_positions = [
                p
                for p in positions
                if str(p.get("asset_type", "")).upper() == asset
            ]
            longs = [
                p
                for p in asset_positions
                if str(p.get("position_type", "")).upper() == "LONG"
            ]
            shorts = [
                p
                for p in asset_positions
                if str(p.get("position_type", "")).upper() == "SHORT"
            ]
            data = {}
            if longs:
                data["long"] = build(longs, asset)
            if shorts:
                data["short"] = build(shorts, asset)
            if data:
                heat_data[asset] = data

        longs_all = [p for p in positions if str(p.get("position_type", "")).upper() == "LONG"]
        shorts_all = [p for p in positions if str(p.get("position_type", "")).upper() == "SHORT"]
        totals = {}
        if shorts_all:
            totals["short"] = build(shorts_all, "Short")
        if longs_all:
            totals["long"] = build(longs_all, "Long")
        heat_data["totals"] = totals

        return render_template("hedge_report.html", heat_data=heat_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@system_bp.route("/xcom_config", methods=["GET"])
def xcom_config_page():
    dl = current_app.data_locker
    profile = dl.system.get_active_theme_profile() or {}
    providers = profile.get("communication", {}).get("providers")
    if not providers:
        providers = dl.system.get_var("xcom_providers") or {}
    return render_template("system/xcom_config.html", xcom_config=providers)


@system_bp.route("/xcom_config/save", methods=["POST"])
def save_xcom_config():
    try:
        dl = current_app.data_locker
        form = request.form
        core = get_core()

        # 🧠 Extract form values
        def extract(field):
            return form.get(field, "").strip()

        new_config = {
            "communication": {
                "providers": {
                    "api": {
                        "account_sid": extract("api[account_sid]"),
                        "auth_token": extract("api[auth_token]"),
                        "flow_sid": extract("api[flow_sid]"),
                        "default_to_phone": extract("api[default_to_phone]"),
                        "default_from_phone": extract("api[default_from_phone]"),
                    },
                    "email": {
                        "enabled": True,
                        "smtp": {
                            "server": extract("email[smtp][server]"),
                            "port": int(extract("email[smtp][port]") or 0),
                            "username": extract("email[smtp][username]"),
                            "password": extract("email[smtp][password]"),
                            "default_recipient": extract(
                                "email[smtp][default_recipient]"
                            ),
                        },
                    },
                    "sms": {
                        "enabled": True,
                        "carrier_gateway": extract("sms[carrier_gateway]"),
                        "default_recipient": extract("sms[default_recipient]"),
                    },
                }
            }
        }

        # Store providers globally for use outside of theme profiles
        dl.system.set_var(
            "xcom_providers", new_config["communication"]["providers"]
        )

        # ✅ Get active profile name safely
        profile_name = core.get_active_profile_name()
        if not profile_name:
            flash("❌ No active profile set — cannot save XCom config.", "danger")
            return redirect(url_for("system.xcom_config_page"))

        # 💾 Save using SystemCore → ThemeService
        core.save_profile(profile_name, new_config)
        flash(f"✅ XCom config saved to profile '{profile_name}'.", "success")

    except Exception as e:
        flash(f"❌ Failed to save XCom config: {e}", "danger")

    return redirect(url_for("system.xcom_config_page"))


@system_bp.route("/alert_thresholds", methods=["GET"])
def list_alert_thresholds():
    db = current_app.data_locker.db
    thresholds = DLThresholdManager(db).get_all()

    grouped = {}

    for t in thresholds:
        for level in ["low", "medium", "high"]:
            # ✅ Notify list for checkbox rendering
            notify_field = f"{level}_notify"
            raw = getattr(t, notify_field, "") or ""
            notify_list = [v.strip() for v in raw.split(",") if v.strip()]
            setattr(t, f"{notify_field}_list", notify_list)

            # ✅ Value field (e.g. t.low_val, t.medium_val)
            value_field = getattr(t, level, None)
            setattr(t, f"{level}_val", value_field)

        grouped.setdefault(t.alert_class, []).append(t)

    return render_template("system/alert_thresholds.html", grouped_thresholds=grouped)


# === POST: Update a threshold (AJAX) ===
@system_bp.route("/alert_thresholds/update/<id>", methods=["POST"])
def update_alert_threshold(id):
    try:
        data = request.json
        fields = {
            "low": float(data["low"]),
            "medium": float(data["medium"]),
            "high": float(data["high"]),
            "enabled": bool(data["enabled"]),
            "low_notify": ",".join(data.get("low_notify", [])),
            "medium_notify": ",".join(data.get("medium_notify", [])),
            "high_notify": ",".join(data.get("high_notify", [])),
        }
        db = current_app.data_locker.db
        DLThresholdManager(db).update(id, fields)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# === POST: Update all thresholds ===
@system_bp.route("/alert_thresholds/update_all", methods=["POST"])
def update_all_alert_thresholds():
    try:
        payload = request.get_json(force=True)
        if not isinstance(payload, list):
            return (
                jsonify({"success": False, "error": "Expected a list of thresholds"}),
                400,
            )

        db = current_app.data_locker.db
        dl_mgr = DLThresholdManager(db)
        updated = 0
        for item in payload:
            tid = item.get("id")
            if not tid:
                continue
            dl_mgr.update(tid, item)
            updated += 1
        return jsonify({"success": True, "updated": updated})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@system_bp.route("/alert_thresholds/export", methods=["GET"])
def export_alert_thresholds():
    try:
        db = current_app.data_locker.db
        mgr = DLThresholdManager(db)
        mgr.export_to_json()
        thresholds = mgr.get_all()
        data = [t.to_dict() for t in thresholds]
        return jsonify(data)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@system_bp.route("/alert_thresholds/import", methods=["POST"])
def import_alert_thresholds():
    try:
        payload = request.get_json(silent=True)
        db = current_app.data_locker.db
        mgr = DLThresholdManager(db)

        updated = 0
        if isinstance(payload, list):
            for item in payload:
                tid = item.get("id")
                if not tid:
                    continue
                if mgr.get_by_id(tid):
                    mgr.update(tid, item)
                else:
                    mgr.insert(AlertThreshold(**item))
                updated += 1
        else:
            updated = mgr.import_from_json()

        return jsonify({"success": True, "updated": updated})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@system_bp.route("/xcom_config/export", methods=["GET"])
def export_xcom_config():
    try:
        config = current_app.data_locker.system.get_var("xcom_providers") or {}
        return jsonify(config)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@system_bp.route("/xcom_config/import", methods=["POST"])
def import_xcom_config():
    try:
        payload = request.get_json()
        if not isinstance(payload, dict):
            return jsonify({"success": False, "error": "Expected JSON object"}), 400

        current_app.data_locker.system.set_var("xcom_providers", payload)
        return jsonify({"success": True, "message": "XCom config imported."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@system_bp.route("/xcom_config/validate_api", methods=["POST"])
def validate_api():
    try:
        from flask import current_app
        import requests

        dl = current_app.data_locker
        api_cfg = dl.system.get_var("xcom_providers").get("api", {})

        sid = api_cfg.get("account_sid")
        token = api_cfg.get("auth_token")

        if not sid or not token:
            return jsonify({"status": "fail", "reason": "Missing SID or token"}), 400

        url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}.json"
        response = requests.get(url, auth=(sid, token))

        if response.status_code == 200:
            return jsonify(
                {"status": "ok", "message": "✅ API credentials are valid."}
            )
        elif response.status_code == 401:
            return (
                jsonify(
                    {
                        "status": "fail",
                        "message": "❌ Invalid Account SID or Auth Token.",
                        "details": response.json(),
                    }
                ),
                401,
            )
        else:
            return (
                jsonify(
                    {
                        "status": "fail",
                        "message": f"❌ Unexpected response from Twilio: {response.status_code}",
                        "details": response.text,
                    }
                ),
                response.status_code,
            )

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@system_bp.route("/api/check/<string:api_name>", methods=["GET"])
def api_check(api_name: str):
    """Return health check status for a specific API."""
    core = get_core()
    result = core.check_api(api_name)
    return jsonify(result)


@system_bp.route("/xcom_api_status", methods=["GET"])
def xcom_api_status():
    """Return connectivity status for key XCom APIs."""
    core = get_core()

    checks = {
        "twilio": core.check_twilio_api(),
        "chatgpt": core.check_chatgpt(),
        "jupiter": core.check_jupiter(),
        "github": core.check_github(),
    }

    def _format(res):
        if isinstance(res, dict):
            return "ok" if res.get("success") else f"error: {res.get('error')}"
        return "ok" if str(res).lower() == "ok" else f"error: {res}"

    status = {name: _format(res) for name, res in checks.items()}

    return jsonify(status)


@classmethod
def death(cls, message: str, source: str = None, payload: dict = None):
    cls._print("death", message, source, payload)


@system_bp.route("/test_death", methods=["GET"])
def test_death_nail():
    try:
        system_core = current_app.system_core

        system_core.death(
            {
                "message": "💀 Manual death spiral test triggered via /test_death",
                "payload": {
                    "status": 401,
                    "source": "manual_test",
                    "user": "tester",
                    "reason": "Triggered by /test_death",
                },
                "level": "HIGH",
            }
        )

        return "<h2 style='color:red'>💀 DEATH NAIL TRIGGERED</h2><p>Sound, log, and escalation executed.</p>"

    except Exception as e:
        return f"<h2>❌ Death Nail Failed</h2><pre>{str(e)}</pre>", 500
