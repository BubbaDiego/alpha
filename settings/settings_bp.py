# settings/settings_bp.py

import os
import json
from flask import Blueprint, render_template, jsonify, request, current_app
from core.constants import THEME_CONFIG_PATH
from core.logging import log
from utils.route_decorators import route_log_alert
from utils.template_filters import short_datetime

settings_bp = Blueprint(
    'settings_bp',
    __name__,
    url_prefix='/settings',
    template_folder='../templates/settings'  # ✅ Corrected
)

# Register template filters for standalone test apps.
settings_bp.add_app_template_filter(short_datetime, 'short_datetime')

@settings_bp.route("/theme")
@route_log_alert
def theme_setup():
    theme_data = {
        "background": "#f5f5f5",
        "text": "#000",
        "card": "#ffffff",
        "navbar": "#eeeeee"
    }
    return render_template("theme_builder.html", theme=theme_data)

@settings_bp.route("/save_theme_mode", methods=["POST"])
@route_log_alert
def save_theme_mode():
    theme_mode = request.json.get("theme_mode")
    dl = current_app.data_locker
    dl.set_theme_mode(theme_mode)
    return jsonify({"success": True})

@settings_bp.route("/save_theme", methods=["POST"])
@route_log_alert
def save_theme():
    theme_data = request.json
    with open(THEME_CONFIG_PATH, "w") as f:
        json.dump(theme_data, f, indent=2)
    return jsonify({"success": True})

@settings_bp.route("/database")
@route_log_alert
def database_viewer():
    try:
        dl = current_app.data_locker
        datasets = dl.get_all_tables_as_dict()
        return render_template("db_viewer.html", datasets=datasets)
    except Exception as e:
        log.error(f"❌ Error loading tables: {e}", source="DatabaseViewer")
        return render_template("db_viewer.html", datasets={})
