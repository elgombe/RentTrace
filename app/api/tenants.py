from flask import Blueprint, request, jsonify, render_template
from app.middleware.auth_guard import login_required
from app.controllers.tenant_controller import (
    get_all_tenants,
    create_tenant,
    update_tenant,
    delete_tenant,
)

tenants_bp = Blueprint("tenants", __name__)


@tenants_bp.route("", methods=["GET"])
@login_required
def list_tenants():
    tenants = get_all_tenants()
    return render_template("partials/tenants_table.html", tenants=tenants)


@tenants_bp.route("", methods=["POST"])
@login_required
def add_tenant():
    data   = request.get_json()
    result = create_tenant(data)
    return jsonify(result), 201 if result["success"] else 400


@tenants_bp.route("/<int:tenant_id>", methods=["PUT"])
@login_required
def edit_tenant(tenant_id):
    data   = request.get_json()
    result = update_tenant(tenant_id, data)
    return jsonify(result), 200 if result["success"] else 400


@tenants_bp.route("/<int:tenant_id>", methods=["DELETE"])
@login_required
def remove_tenant(tenant_id):
    result = delete_tenant(tenant_id)
    return jsonify(result), 200 if result["success"] else 400
