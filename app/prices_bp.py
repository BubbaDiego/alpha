
#!/usr/bin/env python
"""
Module: prices_bp.py
Description:
    A production‑ready Flask blueprint for all price‑related endpoints.
    This module handles:
      - Rendering price charts for assets (BTC, ETH, SOL, SP500) over a specified timeframe.
      - Displaying a price list and manual price updates.
      - Triggering asynchronous price updates via PriceMonitor.

    It is structured similarly to our positions and alerts blueprints for consistent
    separation of concerns.
"""

import logging
import sqlite3
import asyncio
from datetime import datetime, timedelta

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, current_app

# Import configuration constants and modules
from data.data_locker import DataLocker
from monitor.price_monitor import PriceMonitor
from core.core_imports import CONFIG_PATH, DB_PATH, retry_on_locked


# ---------------------------------------------------------------------------
# Helper Functions (Replace with your actual implementations if available)
# ---------------------------------------------------------------------------
@retry_on_locked()
def _get_top_prices_for_assets(db_path, assets):
    """
    Retrieve the latest price for each asset.
    """
    dl = current_app.data_locker
    top_prices = []
    for asset in assets:
        row = dl.prices.get_latest_price(asset)
        if row:
            top_prices.append(row)
    return top_prices


def _get_recent_prices(db_path, limit=15):
    """
    Retrieve the most recent price entries.
    """
    dl = get_locker()
    prices = dl.get_prices()
    return prices[:limit]


# ---------------------------------------------------------------------------
# Logger Setup
# ---------------------------------------------------------------------------
logger = logging.getLogger("PricesBlueprint")
logger.setLevel(logging.DEBUG)

# ---------------------------------------------------------------------------
# Blueprint Definition
# ---------------------------------------------------------------------------
prices_bp = Blueprint("prices", __name__, template_folder="templates")

# Define the asset list to include S&P500 as well as crypto assets.
ASSETS_LIST = ["BTC", "ETH", "SOL", "SP500"]


# ---------------------------------------------------------------------------
# Price Charts Endpoint
# ---------------------------------------------------------------------------
@prices_bp.route("/charts", methods=["GET"])
def price_charts():
    """
    Render price charts for BTC, ETH, SOL, and SP500 over a specified timeframe.
    URL Params:
      - hours: (optional, default=6) Number of hours to look back.
    """
    try:
        hours = request.args.get("hours", default=6, type=int)
        cutoff_time = datetime.now() - timedelta(hours=hours)
        cutoff_iso = cutoff_time.isoformat()
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        chart_data = {asset: [] for asset in ASSETS_LIST}
        for asset in ASSETS_LIST:
            cur.execute(
                """
                SELECT current_price, last_update_time
                FROM prices
                WHERE asset_type = ? AND last_update_time >= ?
                ORDER BY last_update_time ASC
                """,
                (asset, cutoff_iso)
            )
            rows = cur.fetchall()
            for row in rows:
                iso_str = row["last_update_time"]
                price = float(row["current_price"])
                dt_obj = datetime.fromisoformat(iso_str)
                epoch_ms = int(dt_obj.timestamp() * 1000)
                chart_data[asset].append([epoch_ms, price])
        conn.close()
        return render_template("price_charts.html", chart_data=chart_data, timeframe=hours)
    except Exception as e:
        logger.error("Error in price_charts: %s", e, exc_info=True)
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------------------------------
# Price List and Manual Update Endpoint
# ---------------------------------------------------------------------------
@prices_bp.route("/", methods=["GET", "POST"])
def price_list():
    """
    Handles both GET and POST requests for price data.

    GET:
      - Renders a page with:
          - Top prices (latest per asset)
          - Recent price entries
          - API counters (if any)

    POST:
      - Accepts a manual price update.
      - Expects form fields:
            asset: asset type (e.g., "BTC", "SP500")
            price: the new price value
    """
    dl = get_locker()
    if request.method == "POST":
        try:
            asset = request.form.get("asset", "BTC")
            raw_price = request.form.get("price", "0.0")
            price_val = float(raw_price)
            dl.insert_or_update_price(
                asset_type=asset,
                current_price=price_val,
                source="Manual",
                timestamp=datetime.now()
            )
            flash(f"Price for {asset} updated successfully!", "success")
            return redirect(url_for("prices.price_list"))
        except Exception as e:
            logger.error("Error updating price manually: %s", e, exc_info=True)
            flash(f"Error updating price: {e}", "danger")
            return redirect(url_for("prices.price_list"))
    else:
        try:
            top_prices = _get_top_prices_for_assets(DB_PATH, ASSETS_LIST)
            recent_prices = _get_recent_prices(DB_PATH, limit=15)
            api_counters = dl.read_api_counters()
            return render_template("prices.html", prices=top_prices, recent_prices=recent_prices,
                                   api_counters=api_counters)
        except Exception as e:
            logger.error("Error in rendering price list: %s", e, exc_info=True)
            return jsonify({"error": str(e)}), 500


# ---------------------------------------------------------------------------
# Asynchronous Price Update Endpoint
# ---------------------------------------------------------------------------
@prices_bp.route("/update", methods=["POST"])
def update_prices_route():
    """
    Triggers an asynchronous update of price data using PriceMonitor.
    Expects an optional query/form parameter 'source' to indicate the origin.
    """
    try:
        source = request.args.get("source") or request.form.get("source") or "API"
        pm = PriceMonitor(db_path=DB_PATH, config_path=CONFIG_PATH)
        asyncio.run(pm.update_prices())
        dl = get_locker()
        now = datetime.now()
        dl.set_last_update_times({
            "last_update_time_prices": now.isoformat(),
            "last_update_prices_source": source
        })
        return jsonify({
            "status": "ok",
            "message": "Prices updated successfully",
            "last_update": now.isoformat()
        })
    except Exception as e:
        logger.exception("Error updating prices: %s", e)
        return jsonify({"status": "error", "message": str(e)}), 500


# ---------------------------------------------------------------------------
# (Optional) API Endpoint for Price Data
# ---------------------------------------------------------------------------
@prices_bp.route("/api/data", methods=["GET"])
@prices_bp.route("/api/data", methods=["GET"])
def prices_data_api():
    """
    Provides an API endpoint that returns:
      - Mini price data for each asset (BTC, ETH, SOL, SP500)
      - Full price list (top prices)
    """
    try:
        dl = current_app.data_locker
        mini_prices = []
        for asset in ASSETS_LIST:
            row = dl.prices.get_latest_price(asset)
            if row:
                mini_prices.append({
                    "asset_type": row["asset_type"],
                    "current_price": float(row["current_price"])
                })
        prices_list = _get_top_prices_for_assets(DB_PATH, ASSETS_LIST)
        return jsonify({
            "mini_prices": mini_prices,
            "prices": prices_list
            # Removed "totals" since not needed
        })
    except Exception as e:
        logger.error("Error in prices_data_api: %s", e, exc_info=True)
        return jsonify({"error": str(e)}), 500
