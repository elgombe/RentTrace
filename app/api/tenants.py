from flask import Blueprint, request, jsonify, session

tenants_bp = Blueprint("tenants", __name__, url_prefix="/api/tenants")

@tenants_bp.route("/", methods=["GET"])
def get_tenants():
    return jsonify({"message": "Get tenants endpoint - not implemented yet"}), 501