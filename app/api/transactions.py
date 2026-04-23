from flask import Blueprint, request, jsonify, session

transactions_bp = Blueprint("transactions", __name__, url_prefix="/api/transactions")

@transactions_bp.route("/", methods=["GET"])
def get_transactions():
    return jsonify({"message": "Get transactions endpoint - not implemented yet"}), 501