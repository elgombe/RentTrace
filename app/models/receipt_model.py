from datetime import datetime
from app.models.database import db



class Receipt(db.Model):
    __tablename__ = "receipts"

    id             = db.Column(db.Integer, primary_key=True)
    receipt_number = db.Column(db.String(100), nullable=True)
    tenant_id      = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=True)
    amount         = db.Column(db.Float, nullable=False)
    date           = db.Column(db.Date, nullable=False)
    file_path      = db.Column(db.String(500), nullable=True)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    reconciliations = db.relationship("Reconciliation", backref="receipt", lazy=True)

    def to_dict(self):
        return {
            "id":             self.id,
            "receipt_number": self.receipt_number,
            "tenant_id":      self.tenant_id,
            "amount":         self.amount,
            "date":           self.date.isoformat(),
            "file_path":      self.file_path,
            "created_at":     self.created_at.isoformat(),
        }
