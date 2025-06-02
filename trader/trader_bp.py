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



@trader_bp.route("/factory")
def trader_factory_all():
    """Show cards for all known traders."""
    loader = _loader()
    names = loader.persona_manager.list_personas()
    traders = [loader.load_trader(n) for n in names]
    return render_template("trader_factory.html", traders=traders)


@trader_bp.route("/factory/<name>")
def trader_factory_single(name: str):
    """Render the trader factory page with a single trader."""
    loader = _loader()
    trader = loader.load_trader(name)
    return render_template("trader_factory.html", traders=[trader])

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
