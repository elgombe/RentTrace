from app.models.tenant_model import Tenant
from app.models.database import db


def get_all_tenants():
    return Tenant.query.order_by(Tenant.name).all()


def get_tenant_by_id(tenant_id: int):
    return Tenant.query.get(tenant_id)


def create_tenant(data: dict) -> dict:
    name         = (data.get("name") or "").strip()
    unit_number  = (data.get("unit_number") or "").strip()
    monthly_rent = data.get("monthly_rent")
    lease_start  = data.get("lease_start") or None
    lease_end    = data.get("lease_end") or None

    if not name:
        return {"success": False, "error": "Tenant name is required"}
    if not unit_number:
        return {"success": False, "error": "Unit number is required"}
    if monthly_rent is None or float(monthly_rent) <= 0:
        return {"success": False, "error": "Monthly rent must be greater than zero"}

    existing = Tenant.query.filter_by(unit_number=unit_number).first()
    if existing:
        return {"success": False, "error": f"Unit {unit_number} is already assigned to another tenant"}

    tenant = Tenant(
        name=name,
        unit_number=unit_number,
        monthly_rent=float(monthly_rent),
        lease_start=lease_start,
        lease_end=lease_end,
    )
    db.session.add(tenant)
    db.session.commit()

    return {"success": True, "tenant": tenant.to_dict()}


def update_tenant(tenant_id: int, data: dict) -> dict:
    tenant = Tenant.query.get(tenant_id)
    if not tenant:
        return {"success": False, "error": "Tenant not found"}

    name         = (data.get("name") or "").strip()
    unit_number  = (data.get("unit_number") or "").strip()
    monthly_rent = data.get("monthly_rent")
    lease_start  = data.get("lease_start") or None
    lease_end    = data.get("lease_end") or None

    if not name:
        return {"success": False, "error": "Tenant name is required"}
    if not unit_number:
        return {"success": False, "error": "Unit number is required"}
    if monthly_rent is None or float(monthly_rent) <= 0:
        return {"success": False, "error": "Monthly rent must be greater than zero"}

    # Check unit conflict — exclude current tenant
    conflict = Tenant.query.filter(
        Tenant.unit_number == unit_number,
        Tenant.id != tenant_id
    ).first()
    if conflict:
        return {"success": False, "error": f"Unit {unit_number} is already assigned to another tenant"}

    tenant.name         = name
    tenant.unit_number  = unit_number
    tenant.monthly_rent = float(monthly_rent)
    tenant.lease_start  = lease_start
    tenant.lease_end    = lease_end
    db.session.commit()

    return {"success": True, "tenant": tenant.to_dict()}


def delete_tenant(tenant_id: int) -> dict:
    tenant = Tenant.query.get(tenant_id)
    if not tenant:
        return {"success": False, "error": "Tenant not found"}

    db.session.delete(tenant)
    db.session.commit()

    return {"success": True}
