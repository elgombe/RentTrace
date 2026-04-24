from flask import Blueprint, request, jsonify, render_template
from app.middleware.auth_guard import login_required
from app.controllers.upload_controller import process_bank_upload

transactions_bp = Blueprint("transactions", __name__)


@transactions_bp.route("/upload", methods=["POST"])
@login_required
def upload_bank():
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file provided"}), 400

    file   = request.files["file"]
    result = process_bank_upload(file)
    return jsonify(result), 201 if result["success"] else 400


@transactions_bp.route("/recent", methods=["GET"])
@login_required
def recent_transactions():
    from app.models.transaction_model import BankTransaction
    transactions = BankTransaction.query.order_by(
        BankTransaction.date.desc()
    ).limit(20).all()
    return render_template("partials/transactions_table.html", transactions=transactions)


@transactions_bp.route("", methods=["GET"])
@login_required
def list_transactions():
    from app.models.transaction_model import BankTransaction
    transactions = BankTransaction.query.order_by(
        BankTransaction.date.desc()
    ).all()
    return jsonify([t.to_dict() for t in transactions])
