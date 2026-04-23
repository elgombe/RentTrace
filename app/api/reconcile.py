from flask import Blueprint, request, jsonify, session

reconcile_bp = Blueprint("reconcile", __name__, url_prefix="/api/reconcile")

@reconcile_bp.route("/", methods=["POST"])
def reconcile():
    return jsonify({"message": "Reconcile endpoint - not implemented yet"}), 501