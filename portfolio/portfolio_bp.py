
#!/usr/bin/env python
"""
Module: portfolio_bp.py
Description:
    A production-ready Flask blueprint for all portfolio-related endpoints.
    This module handles portfolio tracking, performance over time, and CRUD operations
    for portfolio entries. All routes are defined inline.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
import uuid
from data.data_locker import DataLocker
from core.core_imports import retry_on_locked

portfolio_bp = Blueprint("portfolio", __name__, url_prefix="/portfolio", template_folder="templates")

@portfolio_bp.route("/", methods=["GET"])
@retry_on_locked()
def index():
    dl = get_locker()
    portfolio_history = dl.get_portfolio_history()  # Returns a list of portfolio snapshot dictionaries
    percent_change = None
    if portfolio_history and len(portfolio_history) >= 2:
        first_value = portfolio_history[0].get("total_value", 0)
        last_value = portfolio_history[-1].get("total_value", 0)
        if first_value != 0:
            percent_change = ((last_value - first_value) / first_value) * 100
    # Render the portfolio history page using the global templates directory
    return render_template(
        "positions/portfolio.html",
        portfolio_data=portfolio_history,
        percent_change=percent_change,
    )

@portfolio_bp.route("/add", methods=["GET", "POST"])
def add_entry():
    dl = get_locker()
    if request.method == "POST":
        total_value_str = request.form.get("total_value", "")
        try:
            total_value = float(total_value_str)
        except ValueError:
            flash("Invalid total value. Please enter a valid number.", "danger")
            return redirect(url_for("portfolio.add_entry"))
        snapshot = {
            "id": str(uuid.uuid4()),
            "snapshot_time": datetime.now().isoformat(),
            "total_value": total_value
        }
        try:
            dl.add_portfolio_entry(snapshot)
            flash("Portfolio entry added successfully!", "success")
        except Exception as e:
            flash(f"Error adding portfolio entry: {e}", "danger")
        return redirect(url_for("portfolio.index"))
    return render_template("add_entry.html")

@portfolio_bp.route("/edit/<entry_id>", methods=["GET", "POST"])
def edit_entry(entry_id):
    dl = get_locker()
    if request.method == "POST":
        total_value_str = request.form.get("total_value", "")
        try:
            total_value = float(total_value_str)
        except ValueError:
            flash("Invalid total value. Please enter a valid number.", "danger")
            return redirect(url_for("portfolio.edit_entry", entry_id=entry_id))
        updated_fields = {"total_value": total_value, "snapshot_time": datetime.now().isoformat()}
        try:
            dl.update_portfolio_entry(entry_id, updated_fields)
            flash("Portfolio entry updated successfully!", "success")
        except Exception as e:
            flash(f"Error updating portfolio entry: {e}", "danger")
        return redirect(url_for("portfolio.index"))
    else:
        entry = dl.get_portfolio_entry_by_id(entry_id)
        if not entry:
            flash("Portfolio entry not found", "danger")
            return redirect(url_for("portfolio.index"))
        return render_template("edit_entry.html", entry=entry)

@portfolio_bp.route("/delete/<entry_id>", methods=["POST"])
def delete_entry(entry_id):
    dl = get_locker()
    try:
        dl.delete_portfolio_entry(entry_id)
        flash("Portfolio entry deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting portfolio entry: {e}", "danger")
    return redirect(url_for("portfolio.index"))
