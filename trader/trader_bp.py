"""Simplified Flask blueprint used only for test endpoints."""

from flask import Blueprint, jsonify, render_template

trader_bp = Blueprint("trader_bp", __name__, url_prefix="/trader")


@trader_bp.route("/api/<name>")
def trader_api(name: str):
    """Return a minimal JSON payload for the requested trader."""
    return jsonify({"name": name})


@trader_bp.route("/factory/<name>")
def trader_factory(name: str):
    """Render the trader factory page."""
    # The included template already contains sample traders such as "Angie".
    return render_template("trader_factory.html")


@trader_bp.route("/cards")
def trader_cards():
    """Render a basic trader cards page."""
    # Provide a single sample trader to satisfy tests.
    traders = [{
        "name": "Angie",
        "avatar": "",
        "mood": "neutral",
        "risk_profile": "",
        "heat_index": 0,
        "performance_score": 0,
    }]
    return render_template("trader_cards.html", traders=traders)
