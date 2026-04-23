from flask import Blueprint, request, jsonify, session

receipts_bp = Blueprint("receipts", __name__, url_prefix="/api/receipts")

@receipts_bp.route("/", methods=["GET"])
def get_receipts():
    return jsonify({"message": "Get receipts endpoint - not implemented yet"}), 501