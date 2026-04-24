from datetime import date
from app.models.database import db
from app.models.tenant_model import Tenant
from app.models.transaction_model import BankTransaction
from app.models.receipt_model import Receipt
from app.models.reconcile_model import Reconciliation


# ── Tolerance for amount matching (e.g. rounding differences) ──
MATCH_TOLERANCE = 1.00


def run_reconciliation(from_period: str = None, to_period: str = None) -> dict:
    try:
        today = date.today()

        if not from_period:
            from_period = f"{today.year}-{today.month:02d}"
        if not to_period:
            to_period = from_period

        # Build list of YYYY-MM periods in range
        def period_months(fp, tp):
            fy, fm = map(int, fp.split("-"))
            ty, tm = map(int, tp.split("-"))
            periods = []
            y, m = fy, fm
            while (y, m) <= (ty, tm):
                periods.append(f"{y}-{m:02d}")
                m += 1
                if m > 12:
                    m = 1
                    y += 1
            return periods

        periods = period_months(from_period, to_period)
        total   = 0

        for period_str in periods:
            year, month = map(int, period_str.split("-"))
            month_start = date(year, month, 1)
            month_end   = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)

            Reconciliation.query.filter_by(period=period_str).delete()
            db.session.flush()

            tenants   = Tenant.query.all()
            bank_txns = BankTransaction.query.filter(
                BankTransaction.date >= month_start,
                BankTransaction.date <  month_end,
                BankTransaction.amount > 0,
            ).all()
            receipts  = Receipt.query.filter(
                Receipt.date >= month_start,
                Receipt.date <  month_end,
            ).all()

            used_txn_ids     = set()
            used_receipt_ids = set()
            results          = []

            for tenant in tenants:
                tenant_receipts = [r for r in receipts if r.tenant_id == tenant.id]

                if not tenant_receipts:
                    results.append(Reconciliation(
                        tenant_id=tenant.id, receipt_id=None, transaction_id=None,
                        expected_amount=tenant.monthly_rent, status="arrears",
                        flag_reason="No receipt found for this period", period=period_str,
                    ))
                    continue

                for receipt in tenant_receipts:
                    used_receipt_ids.add(receipt.id)
                    matched_txn = next((
                        t for t in bank_txns
                        if t.id not in used_txn_ids
                        and abs(t.amount - receipt.amount) <= MATCH_TOLERANCE
                    ), None)

                    if matched_txn:
                        used_txn_ids.add(matched_txn.id)
                        results.append(Reconciliation(
                            tenant_id=tenant.id, receipt_id=receipt.id,
                            transaction_id=matched_txn.id,
                            expected_amount=tenant.monthly_rent, status="matched",
                            flag_reason=None, period=period_str,
                        ))
                    else:
                        results.append(Reconciliation(
                            tenant_id=tenant.id, receipt_id=receipt.id,
                            transaction_id=None, expected_amount=tenant.monthly_rent,
                            status="missing_deposit",
                            flag_reason=f"Receipt #{receipt.receipt_number or receipt.id} has no matching bank deposit",
                            period=period_str,
                        ))

            for txn in bank_txns:
                if txn.id not in used_txn_ids:
                    results.append(Reconciliation(
                        tenant_id=None, receipt_id=None, transaction_id=txn.id,
                        expected_amount=None, status="unverified",
                        flag_reason=f"Bank deposit of ${txn.amount:.2f} on {txn.date} has no matching receipt",
                        period=period_str,
                    ))

            for r in results:
                db.session.add(r)

            total += len(results)

        db.session.commit()
        return {"success": True, "total": total, "from_period": from_period, "to_period": to_period}

    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e)}

def get_results(from_period: str = None, to_period: str = None, status: str = None):
    query = Reconciliation.query

    if from_period:
        query = query.filter(Reconciliation.period >= from_period)
    if to_period:
        query = query.filter(Reconciliation.period <= to_period)
    if status:
        query = query.filter_by(status=status)

    return query.order_by(Reconciliation.period, Reconciliation.created_at).all()

def get_recent_exceptions(limit: int = 10):
    return Reconciliation.query.filter(
        Reconciliation.status != "matched"
    ).order_by(
        Reconciliation.created_at.desc()
    ).limit(limit).all()


def get_summary() -> dict:
    rows = Reconciliation.query.all()

    matched    = sum(1 for r in rows if r.status == "matched")
    missing    = sum(1 for r in rows if r.status == "missing_deposit")
    unverified = sum(1 for r in rows if r.status == "unverified")
    arrears    = sum(1 for r in rows if r.status == "arrears")

    expected  = sum(r.expected_amount or 0 for r in rows if r.status == "matched")
    collected = sum(
        r.transaction.amount for r in rows
        if r.status == "matched" and r.transaction
    )
    leakage   = max(0.0, expected - collected)

    return {
        "matched":    matched,
        "missing":    missing,
        "unverified": unverified,
        "arrears":    arrears,
        "expected":   round(expected, 2),
        "collected":  round(collected, 2),
        "leakage":    round(leakage, 2),
    }


def get_monthly_chart_data() -> dict:
    from sqlalchemy import func

    rows = db.session.query(
        Reconciliation.period,
        func.sum(Reconciliation.expected_amount).label("expected"),
    ).group_by(Reconciliation.period).order_by(Reconciliation.period).all()

    labels    = [r.period for r in rows]
    expected  = [round(r.expected or 0, 2) for r in rows]

    # Collected = sum of matched transaction amounts per period
    collected = []
    for r in rows:
        matched = Reconciliation.query.filter_by(
            period=r.period, status="matched"
        ).all()
        total = sum(
            m.transaction.amount for m in matched if m.transaction
        )
        collected.append(round(total, 2))

    return {
        "labels":    labels,
        "expected":  expected,
        "collected": collected,
    }
