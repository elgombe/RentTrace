from flask import Blueprint, request, jsonify, session

reports_bp = Blueprint("reports", __name__, url_prefix="/api/reports")

@reports_bp.route("/rent-roll", methods=["GET"])
def rent_roll():
    return jsonify({"message": "Rent roll report endpoint - not implemented yet"}), 501