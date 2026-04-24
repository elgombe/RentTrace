from flask import Blueprint, request, jsonify, send_file
from app.middleware.auth_guard import login_required
from app.controllers.report_controller import generate_pdf_report

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/export", methods=["GET"])
@login_required
def export():
    from_period = request.args.get("from_period")
    to_period   = request.args.get("to_period")
    result      = generate_pdf_report(from_period, to_period)

    if not result["success"]:
        return jsonify(result), 400

    return send_file(
        result["path"],
        as_attachment=True,
        download_name=result["filename"],
        mimetype="application/pdf",
    )