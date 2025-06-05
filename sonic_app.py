#!/usr/bin/env python
"""
sonic_app.py
Main Flask app for Sonic Dashboard.
"""

import os
import sys
try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover - optional dependency
    def load_dotenv(*_a, **_k):
        pass

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
load_dotenv()

try:
    from flask import Flask, redirect, url_for, current_app, jsonify
    from flask_socketio import SocketIO
except Exception:  # pragma: no cover - optional dependency
    class Flask:
        """Minimal stub used when Flask isn't installed."""

        def __init__(self, *a, **k):
            self.config = {}
            self.view_functions = {}

        def route(self, *args, **kwargs):
            def decorator(func):
                self.view_functions[func.__name__] = func
                return func

            return decorator

        def add_url_rule(self, rule, endpoint=None, view_func=None, **options):
            if view_func:
                self.view_functions[endpoint or view_func.__name__] = view_func

        def context_processor(self, func):
            return func

        def run(self, *a, **k):  # pragma: no cover - not executed in tests
            raise RuntimeError("Flask not installed")

    def redirect(location):
        return location

    def url_for(endpoint, **kwargs):
        return endpoint

    current_app = type("obj", (), {})()

    def jsonify(*_a, **_k):
        return {}

    class SocketIO:
        def __init__(self, *a, **k):
            pass

from core.core_imports import log, configure_console_log, DB_PATH, BASE_DIR, retry_on_locked
from datetime import datetime
from data.data_locker import DataLocker
from system.system_core import SystemCore
from dashboard.dashboard_service import get_profit_badge_value

# --- Monitor & Cyclone Core Integration ---
from monitor.monitor_core import MonitorCore
from cyclone.cyclone_engine import Cyclone

# --- Logging Setup ---
log.banner("SONIC DASHBOARD STARTUP")
log.enable_all()
configure_console_log(debug=True)

# --- Flask Setup ---
app = Flask(__name__)
app.debug = False
app.secret_key = "i-like-lamp"

# ✅ Safe to assign config values now
app.config["PHANTOM_PATH"] = os.getenv("PHANTOM_PATH", "C:/alpha/wallets/phantom_wallet")
app.config["SOLFLARE_PATH"] = os.getenv("SOLFLARE_PATH", "C:/alpha/wallets/solflare_wallet")
# Any other config values...

socketio = SocketIO(app)

# --- Template Filters ---
from utils.template_filters import short_datetime

# Register filters with the Flask app so they are available even when this file
# is imported in isolation (e.g. during tests).
app.add_template_filter(short_datetime, "short_datetime")

# --- SINGLETON BACKEND ---
app.data_locker = DataLocker(str(DB_PATH))
app.system_core = SystemCore(app.data_locker)
app.monitor_core = MonitorCore()
app.cyclone = Cyclone(monitor_core=app.monitor_core, debug=True)

# --- Blueprints ---
from app.positions_bp import positions_bp
from app.alerts_bp import alerts_bp
from app.prices_bp import prices_bp
from app.dashboard_bp import dashboard_bp
from portfolio.portfolio_bp import portfolio_bp
from sonic_labs.sonic_labs_bp import sonic_labs_bp
from cyclone.cyclone_bp import cyclone_bp
from routes.theme_routes import theme_bp
from app.system_bp import system_bp
from settings.settings_bp import settings_bp
from gpt.chat_gpt_bp import chat_gpt_bp
from gpt.gpt_bp import gpt_bp
from trader_core.trader_bp import trader_bp


log.info("Registering blueprints...", source="Startup")
app.register_blueprint(positions_bp, url_prefix="/positions")
app.register_blueprint(alerts_bp, url_prefix="/alerts")
app.register_blueprint(prices_bp, url_prefix="/prices")
app.register_blueprint(dashboard_bp)
app.register_blueprint(portfolio_bp, url_prefix="/portfolio")
app.register_blueprint(sonic_labs_bp, url_prefix="/sonic_labs")
app.register_blueprint(cyclone_bp)
app.register_blueprint(theme_bp)
app.register_blueprint(system_bp)
app.register_blueprint(settings_bp)
app.register_blueprint(chat_gpt_bp)
app.register_blueprint(gpt_bp)
app.register_blueprint(trader_bp)

# --- Set Default Email Provider for XCom ---
with app.app_context():
    providers = app.data_locker.system.get_var("xcom_providers") or {}
    providers["email"] = {
        "enabled": False,  # True,
        "smtp": {
            "server": os.getenv("SMTP_SERVER"),
            "port": int(os.getenv("SMTP_PORT", "0")) if os.getenv("SMTP_PORT") else None,
            "username": os.getenv("SMTP_USERNAME"),
            "password": os.getenv("SMTP_PASSWORD"),
            "default_recipient": os.getenv("SMTP_DEFAULT_RECIPIENT"),
        },
    }
    app.data_locker.system.set_var("xcom_providers", providers)
    print("✅ Default email provider set in xcom_providers")


@app.route("/traders", endpoint="trader_cards")
def show_trader_factory():
    return render_template("trader_factory.html")



# --- Heartbeat API Route for Countdown ---
@app.route("/api/heartbeat")
def api_heartbeat():
    dl = app.data_locker
    cursor = dl.db.get_cursor()
    if not cursor:
        log.error("No DB cursor available; cannot query heartbeat data.")
        return jsonify({"monitors": []})
    cursor.execute("SELECT monitor_name, last_run, interval_seconds FROM monitor_heartbeat")
    rows = cursor.fetchall()
    result = []
    for row in rows:
        result.append({
            "name": row["monitor_name"],
            "last_run": row["last_run"],
            "interval_seconds": row["interval_seconds"],
        })
    return jsonify({"monitors": result})

# --- Hedge Calculator Redirect ---
@app.route("/hedge_calculator")
def hedge_calculator_redirect():
    """Redirect to the Hedge Calculator page within the system blueprint."""
    return redirect(url_for("system.hedge_calculator_page"))

if "dashboard.index" in app.view_functions:
    app.add_url_rule("/dashboard", endpoint="dash", view_func=app.view_functions["dashboard.index"])

# --- Simple Root Redirect ---
@app.route("/")
@retry_on_locked()
def index():
    log.info(f"📂 DB path in use: {current_app.data_locker.db.db_path}", source="DBPath")
    return redirect(url_for('dashboard.dash_page'))

# --- Optional: System Config (if needed by admin panel) ---
# ... (Keep any routes you actually want for config/admin or special actions)


@app.route("/launch/<profile>/<asset>")
def launch_jupiter_position(profile, asset):
    import subprocess

    JUPITER_TOKEN_MAP = {
        "SOL": "So11111111111111111111111111111111111111112",
        "BTC": "9n4nbM75f5Ui33ZbPYXn59EwSgE8CGsHtAeTH5YFeJ9E",
        "ETH": "2jXy799YNy9Wi6kXZGk8Hg3H2wZbYGFh5xdtNBxgdCz6",
        # Extend this map as needed
    }

    token = JUPITER_TOKEN_MAP.get(asset.upper())
    if not token:
        return f"⚠️ Unknown asset: {asset}", 400

    url = f"https://jup.ag/perpetuals/{asset.upper()}"
    chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"
    profile_arg = f"--profile-directory={profile}"

    try:
        subprocess.Popen([chrome_path, profile_arg, url])
        return f"Launching {asset.upper()} in {profile}"
    except Exception as e:
        return f"Failed to launch browser: {str(e)}", 500


# --- Context: Theme Profile (optional, for templates) ---
@app.context_processor
def inject_theme_profile():
    try:
        core = SystemCore(current_app.data_locker)
        active_theme = core.get_active_profile()
        return {"active_theme_profile": active_theme or {}}
    except Exception:
        return {"active_theme_profile": {}}

# --- Context: Profit Badge ---
@app.context_processor
def inject_profit_badge():
    try:
        value = get_profit_badge_value(current_app.data_locker, current_app.system_core)
        return {"profit_badge_value": value}
    except Exception:
        return {"profit_badge_value": None}

# --- Server Entry Point ---
if __name__ == "__main__":
    monitor = "--monitor" in sys.argv
    if monitor:
        try:
            import subprocess
            CREATE_NEW_CONSOLE = 0x00000010
            monitor_script = os.path.join(BASE_DIR, "local_monitor.py")
            subprocess.Popen(["python", monitor_script], creationflags=CREATE_NEW_CONSOLE)
            log.info("Launched local monitor in new console window.", source="Startup")
        except Exception as e:
            log.error(f"Failed to launch local monitor: {e}", source="Startup")

    host = "0.0.0.0"
    port = 5000
    log.success(f"Starting Flask server at {host}:{port}", source="Startup")
    log.print_dashboard_link(host="127.0.0.1", port=port, route="/")
    app.run(debug=False, host=host, port=port)
