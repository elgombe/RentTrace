import os
import pandas as pd
from datetime import datetime
from flask import current_app
from werkzeug.utils import secure_filename
from app.models.transaction_model import BankTransaction
from app.models.receipt_model import Receipt
from app.models.database import db

ALLOWED_BANK    = {"csv", "xlsx", "xls"}
ALLOWED_RECEIPT = {"csv", "xlsx", "xls", "pdf", "png", "jpg", "jpeg"}


def allowed_file(filename: str, allowed: set) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed


def save_upload(file) -> str:
    filename = secure_filename(file.filename)
    path     = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    file.save(path)
    return path


def process_bank_upload(file) -> dict:
    if not file or not file.filename:
        return {"success": False, "error": "No file provided"}

    if not allowed_file(file.filename, ALLOWED_BANK):
        return {"success": False, "error": "File must be CSV or Excel (.csv, .xlsx, .xls)"}

    try:
        path = save_upload(file)
        ext  = file.filename.rsplit(".", 1)[1].lower()

        if ext == "csv":
            df = pd.read_csv(path)
        else:
            df = pd.read_excel(path)

        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

        # ── Flexible column mapping ──
        date_col   = next((c for c in df.columns if "date" in c), None)
        amount_col = next((c for c in df.columns if "amount" in c or "credit" in c or "debit" in c), None)
        desc_col   = next((c for c in df.columns if "desc" in c or "narr" in c or "detail" in c or "ref" in c), None)
        ref_col    = next((c for c in df.columns if "ref" in c and c != desc_col), None)

        if not date_col or not amount_col:
            return {"success": False, "error": "Could not find date or amount columns in the file"}

        inserted = 0
        for _, row in df.iterrows():
            try:
                raw_date = row[date_col]
                if pd.isna(raw_date):
                    continue

                txn_date = pd.to_datetime(raw_date).date()
                amount   = float(row[amount_col])
                desc     = str(row[desc_col]) if desc_col and not pd.isna(row.get(desc_col)) else None
                ref      = str(row[ref_col])  if ref_col  and not pd.isna(row.get(ref_col))  else None

                txn = BankTransaction(
                    date=txn_date,
                    description=desc,
                    amount=amount,
                    reference=ref,
                    source_file=secure_filename(file.filename),
                )
                db.session.add(txn)
                inserted += 1
            except Exception:
                continue

        db.session.commit()
        return {"success": True, "message": f"{inserted} transactions imported", "count": inserted}

    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": f"Failed to process file: {str(e)}"}


def process_receipt_upload(file) -> dict:
    if not file or not file.filename:
        return {"success": False, "error": "No file provided"}

    if not allowed_file(file.filename, ALLOWED_RECEIPT):
        return {"success": False, "error": "Unsupported file type"}

    try:
        path = save_upload(file)
        ext  = file.filename.rsplit(".", 1)[1].lower()

        # ── Structured file (CSV / Excel) ──
        if ext in {"csv", "xlsx", "xls"}:
            df = pd.read_csv(path) if ext == "csv" else pd.read_excel(path)
            df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

            date_col   = next((c for c in df.columns if "date" in c), None)
            amount_col = next((c for c in df.columns if "amount" in c), None)
            tenant_col = next((c for c in df.columns if "tenant" in c or "name" in c), None)
            ref_col    = next((c for c in df.columns if "receipt" in c or "ref" in c or "no" in c), None)

            if not date_col or not amount_col:
                return {"success": False, "error": "Could not find date or amount columns"}

            inserted = 0
            for _, row in df.iterrows():
                try:
                    raw_date = row[date_col]
                    if pd.isna(raw_date):
                        continue

                    rec_date = pd.to_datetime(raw_date).date()
                    amount   = float(row[amount_col])
                    ref      = str(row[ref_col]) if ref_col and not pd.isna(row.get(ref_col)) else None

                    # Try to match tenant by name
                    tenant_id = None
                    if tenant_col and not pd.isna(row.get(tenant_col)):
                        from app.models.tenant_model import Tenant
                        tenant_name = str(row[tenant_col]).strip()
                        tenant = Tenant.query.filter(
                            Tenant.name.ilike(f"%{tenant_name}%")
                        ).first()
                        if tenant:
                            tenant_id = tenant.id

                    receipt = Receipt(
                        receipt_number=ref,
                        tenant_id=tenant_id,
                        amount=amount,
                        date=rec_date,
                        file_path=path,
                    )
                    db.session.add(receipt)
                    inserted += 1
                except Exception:
                    continue

            db.session.commit()
            return {"success": True, "message": f"{inserted} receipts imported", "count": inserted}

        # ── Image / PDF — store as file reference ──
        else:
            receipt = Receipt(
                receipt_number=None,
                tenant_id=None,
                amount=0.0,
                date=datetime.utcnow().date(),
                file_path=path,
            )
            db.session.add(receipt)
            db.session.commit()
            return {"success": True, "message": "Receipt file stored. Please review and assign manually."}

    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": f"Failed to process file: {str(e)}"}
