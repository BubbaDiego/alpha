
"""
🌐 Module: wallet_controller.py
📌 Purpose: Flask routes for managing wallets (UI + image upload).
"""

import os
from flask import Blueprint, request, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename

from wallets.wallet_service import WalletService
from wallets.wallet_core import WalletCore
from wallets.wallet_schema import WalletIn
from core.core_imports import retry_on_locked

wallet_bp = Blueprint("wallets", __name__, url_prefix="/wallets")
service = WalletService()
core = WalletCore()

# 📁 Where uploaded wallet images go
UPLOAD_FOLDER = os.path.join("static", "uploads", "wallets")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 🔍 Show wallet manager
@wallet_bp.route("/", methods=["GET"])
@retry_on_locked()
def list_wallets():
    try:
        wallets = core.load_wallets()
        return render_template("wallets/wallet_manager.html", wallets=wallets)
    except Exception as e:
        import traceback
        return f"<pre>{traceback.format_exc()}</pre>", 500

# ➕ Add a wallet (form submit w/ optional avatar upload)
@wallet_bp.route("/add", methods=["POST"])
def add_wallet():
    try:
        form = request.form
        file = request.files.get("image_file")
        filename = None

        # 💾 Save uploaded image
        if file and file.filename:
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

        # 🧠 Determine final image_path
        image_path = f"/static/uploads/wallets/{filename}" if filename else form.get("image_path")

        # 🧱 Construct wallet data
        data = WalletIn(
            name=form.get("name"),
            public_address=form.get("public_address"),
            private_address=form.get("private_address"),
            image_path=image_path,
            balance=float(form.get("balance", 0.0)),
            tags=[t.strip() for t in form.get("tags", "").split(",") if t.strip()],
            is_active=form.get("is_active", "off") == "on",
            type=form.get("type", "personal"),
            chrome_profile=form.get("chrome_profile", "Default")
        )

        service.create_wallet(data)
        flash("✅ Wallet added!", "success")
    except Exception as e:
        import traceback
        flash(f"❌ Failed to add wallet: {e}", "danger")
        return f"<pre>{traceback.format_exc()}</pre>", 500

    return redirect(url_for("wallets.list_wallets"))

# 🗑️ Delete a wallet
@wallet_bp.route("/delete/<name>", methods=["POST"])
def delete_wallet(name):
    try:
        service.delete_wallet(name)
        flash("🗑️ Wallet deleted.", "info")
    except Exception as e:
        flash(f"❌ Delete failed: {e}", "danger")
    return redirect(url_for("wallets.list_wallets"))

# 💾 Export wallets to JSON
@wallet_bp.route("/export", methods=["POST"])
def export_wallets():
    try:
        service.export_wallets_to_json()
        flash("💾 Exported to wallets.json", "success")
    except Exception as e:
        flash(f"❌ Export failed: {e}", "danger")
    return redirect(url_for("wallets.list_wallets"))

# ♻️ Import wallets from JSON
@wallet_bp.route("/import", methods=["POST"])
def import_wallets():
    try:
        count = service.import_wallets_from_json()
        flash(f"♻️ Imported {count} wallets from backup.", "success")
    except Exception as e:
        flash(f"❌ Import failed: {e}", "danger")
    return redirect(url_for("wallets.list_wallets"))
