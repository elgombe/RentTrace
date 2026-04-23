from datetime import datetime
from app.models.database import db


class Reconciliation(db.Model):
    __tablename__ = "reconciliation"

    id             = db.Column(db.Integer, primary_key=True)
    tenant_id      = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=True)
    receipt_id     = db.Column(db.Integer, db.ForeignKey("receipts.id"), nullable=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey("bank_transactions.id"), nullable=True)
    expected_amount = db.Column(db.Float, nullable=True)
    status         = db.Column(db.String(50), nullable=False)
    flag_reason    = db.Column(db.String(500), nullable=True)
    period         = db.Column(db.String(20), nullable=True)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id":              self.id,
            "tenant_id":       self.tenant_id,
            "receipt_id":      self.receipt_id,
            "transaction_id":  self.transaction_id,
            "expected_amount": self.expected_amount,
            "status":          self.status,
            "flag_reason":     self.flag_reason,
            "period":          self.period,
            "created_at":      self.created_at.isoformat(),
        }