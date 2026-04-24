from flask import Blueprint, request, jsonify, render_template
from app.middleware.auth_guard import login_required
from app.controllers.reconcile_controller import (
    run_reconciliation,
    get_results,
    get_recent_exceptions,
    get_summary,
    get_monthly_chart_data,
)

reconcile_bp = Blueprint("reconcile", __name__)


@reconcile_bp.route("/run", methods=["POST"])
@login_required
def run():
    data   = request.get_json() or {}
    period = data.get("period")
    result = run_reconciliation(period)
    return jsonify(result), 200 if result["success"] else 400


@reconcile_bp.route("/results", methods=["GET"])
@login_required
def results():
    period = request.args.get("period")
    status = request.args.get("status")
    rows   = get_results(period=period, status=status)
    return render_template("partials/reconcile_table.html", results=rows)


@reconcile_bp.route("/recent", methods=["GET"])
@login_required
def recent():
    rows = get_recent_exceptions()
    return render_template("partials/exceptions_table.html", results=rows)


@reconcile_bp.route("/summary", methods=["GET"])
@login_required
def summary():
    data = get_summary()
    return jsonify(data)


@reconcile_bp.route("/monthly", methods=["GET"])
@login_required
def monthly():
    data = get_monthly_chart_data()
    return jsonify(data)
