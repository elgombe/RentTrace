from flask import Blueprint, request, jsonify, render_template
from app.middleware.auth_guard import login_required
from app.controllers.upload_controller import process_receipt_upload
from app.models.receipt_model import Receipt

receipts_bp = Blueprint("receipts", __name__)


@receipts_bp.route("/upload", methods=["POST"])
@login_required
def upload_receipt():
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file provided"}), 400

    file   = request.files["file"]
    result = process_receipt_upload(file)
    return jsonify(result), 201 if result["success"] else 400


@receipts_bp.route("", methods=["GET"])
@login_required
def list_receipts():
    receipts = Receipt.query.order_by(Receipt.date.desc()).all()
    return render_template("partials/receipts_table.html", receipts=receipts)


@receipts_bp.route("/<int:receipt_id>", methods=["DELETE"])
@login_required
def delete_receipt(receipt_id):
    receipt = Receipt.query.get(receipt_id)
    if not receipt:
        return jsonify({"success": False, "error": "Receipt not found"}), 404

    from app.models.database import db
    db.session.delete(receipt)
    db.session.commit()
    return jsonify({"success": True})
