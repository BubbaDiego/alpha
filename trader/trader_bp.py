"""Flask blueprint for Trader dashboards."""

from flask import Blueprint, current_app, jsonify, render_template

from .trader_loader import TraderLoader

trader_bp = Blueprint(
    "trader_bp",
    __name__,
    url_prefix="/trader",
    template_folder="../templates",
)


def _loader():
    app = current_app._get_current_object() if current_app else None
    dl = getattr(app, "data_locker", None)
    return TraderLoader(data_locker=dl)


@trader_bp.route("/<name>")
def trader_page(name: str):
    loader = _loader()
    trader = loader.load_trader(name)
    return render_template("trader_dashboard.html", trader=trader)


@trader_bp.route("/factory/<name>")
def trader_factory(name: str):
    """Render the trader factory page with loaded trader data."""
    loader = _loader()
    trader = loader.load_trader(name)
    return render_template("trader_factory.html", trader=trader)


@trader_bp.route("/api/<name>")
def trader_api(name: str):
    loader = _loader()
    trader = loader.load_trader(name)
    return jsonify(trader.__dict__)


@trader_bp.route("/cards")
def trader_cards():
    """Display cards for all traders."""
    loader = _loader()
    traders = loader.load_all_traders()
    return render_template("trader_cards.html", traders=traders)
