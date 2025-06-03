from flask import Blueprint, current_app, jsonify, render_template, redirect
from trader.trader_core import TraderCore
from core.console_logger import ConsoleLogger as log
from flask import Blueprint, render_template

trader_bp = Blueprint("trader_bp", __name__, url_prefix="/trader")

@trader_bp.route("/shop", endpoint="trader_shop")
def trader_shop():
    return render_template("trader_shop.html")

