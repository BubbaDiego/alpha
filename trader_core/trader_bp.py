import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Blueprint, current_app, jsonify, render_template, redirect
from utils.console_logger import ConsoleLogger as log

from flask import Blueprint, render_template

trader_bp = Blueprint("trader_bp", __name__, url_prefix="/trader")

@trader_bp.route("/shop", endpoint="trader_shop")  # <== THIS LINE MUST EXIST
def trader_shop():
    return render_template("trader_shop.html")
