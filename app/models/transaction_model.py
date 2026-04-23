from datetime import datetime
from app.models.database import db


class BankTransaction(db.Model):
    __tablename__ = "bank_transactions"

    id          = db.Column(db.Integer, primary_key=True)
    date        = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(500), nullable=True)
    amount      = db.Column(db.Float, nullable=False)
    reference   = db.Column(db.String(255), nullable=True)
    source_file = db.Column(db.String(255), nullable=True)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    reconciliations = db.relationship("Reconciliation", backref="transaction", lazy=True)

    def to_dict(self):
        return {
            "id":          self.id,
            "date":        self.date.isoformat(),
            "description": self.description,
            "amount":      self.amount,
            "reference":   self.reference,
            "source_file": self.source_file,
            "created_at":  self.created_at.isoformat(),
        }
