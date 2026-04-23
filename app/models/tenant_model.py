from datetime import datetime
from app.models.database import db


class Tenant(db.Model):
    __tablename__ = "tenants"

    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(255), nullable=False)
    unit_number  = db.Column(db.String(50), nullable=False)
    monthly_rent = db.Column(db.Float, nullable=False)
    lease_start  = db.Column(db.Date, nullable=True)
    lease_end    = db.Column(db.Date, nullable=True)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    receipts        = db.relationship("Receipt", backref="tenant", lazy=True)
    reconciliations = db.relationship("Reconciliation", backref="tenant", lazy=True)

    def to_dict(self):
        return {
            "id":           self.id,
            "name":         self.name,
            "unit_number":  self.unit_number,
            "monthly_rent": self.monthly_rent,
            "lease_start":  self.lease_start.isoformat() if self.lease_start else None,
            "lease_end":    self.lease_end.isoformat() if self.lease_end else None,
            "created_at":   self.created_at.isoformat(),
        }
