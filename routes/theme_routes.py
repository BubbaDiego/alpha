
# /routes/theme_routes.py

from flask import Blueprint, request, jsonify
import os
import json
from core.core_imports import retry_on_locked

# Define Blueprint
theme_bp = Blueprint('theme', __name__, url_prefix='/theme')

# Theme config file path
THEME_CONFIG_PATH = os.path.join('config', 'theme_config.json')

# Default fallback if config doesn't exist
DEFAULT_THEME = {
    "selected_profile": "Default",
    "profiles": {
        "Default": {
            "background": "#ffffff",
            "text": "#000000",
            "card_background": "#f8f9fa",
            "navbar_background": "#007bff"
        }
    }
}

# Helper to load theme config
@retry_on_locked()
def load_theme_config():
    if not os.path.exists(THEME_CONFIG_PATH):
        save_theme_config(DEFAULT_THEME)
    with open(THEME_CONFIG_PATH, 'r') as f:
        return json.load(f)

# Helper to save theme config
def save_theme_config(data):
    with open(THEME_CONFIG_PATH, 'w') as f:
        json.dump(data, f, indent=2)


# === ROUTES ===

@theme_bp.route('/get', methods=['GET'])
def get_theme():
    config = load_theme_config()
    return jsonify(config)


@theme_bp.route('/save', methods=['POST'])
def save_theme():
    data = request.json
    name = data.get('name')
    colors = data.get('colors')
    
    if not name or not colors:
        return jsonify({"error": "Missing name or colors"}), 400

    config = load_theme_config()
    config['profiles'][name] = colors
    save_theme_config(config)
    return jsonify({"message": f"Theme '{name}' saved."})


@theme_bp.route('/set_active', methods=['POST'])
def set_active_theme():
    data = request.json
    name = data.get('name')
    
    if not name:
        return jsonify({"error": "Missing name"}), 400

    config = load_theme_config()
    if name not in config['profiles']:
        return jsonify({"error": "Theme not found"}), 404

    config['selected_profile'] = name
    save_theme_config(config)
    return jsonify({"message": f"Active theme set to '{name}'."})


@theme_bp.route('/delete', methods=['POST'])
def delete_theme():
    data = request.json
    name = data.get('name')
    
    if not name:
        return jsonify({"error": "Missing name"}), 400

    config = load_theme_config()
    if name not in config['profiles']:
        return jsonify({"error": "Theme not found"}), 404

    if name == config.get('selected_profile'):
        return jsonify({"error": "Cannot delete active theme"}), 400

    del config['profiles'][name]
    save_theme_config(config)
    return jsonify({"message": f"Theme '{name}' deleted."})
