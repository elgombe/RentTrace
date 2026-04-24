import os
from datetime import date, datetime
from flask import current_app
from app.models.reconcile_model import Reconciliation
from app.controllers.reconcile_controller import get_summary


def generate_pdf_report(period: str = None) -> dict:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        )
    except ImportError:
        return {"success": False, "error": "reportlab is required for PDF export. Run: pip install reportlab"}

    try:
        if not period:
            today  = date.today()
            period = f"{today.year}-{today.month:02d}"

        summary = get_summary()
        rows    = Reconciliation.query.filter_by(period=period).order_by(
            Reconciliation.status
        ).all()

        # ── Output path ──
        filename = f"RentTrace_Report_{period}.pdf"
        out_dir  = os.path.join(current_app.config.get("UPLOAD_FOLDER", "data/uploads"))
        out_path = os.path.join(out_dir, filename)

        doc    = SimpleDocTemplate(out_path, pagesize=A4,
                                   leftMargin=2*cm, rightMargin=2*cm,
                                   topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        story  = []

        # ── Header ──
        title_style = ParagraphStyle("Title", parent=styles["Heading1"],
                                     fontSize=18, textColor=colors.HexColor("#111827"),
                                     spaceAfter=4)
        sub_style   = ParagraphStyle("Sub", parent=styles["Normal"],
                                     fontSize=10, textColor=colors.HexColor("#6b7280"),
                                     spaceAfter=16)
        story.append(Paragraph("RentTrace — Audit Report", title_style))
        story.append(Paragraph(f"Period: {period} &nbsp;|&nbsp; Generated: {datetime.now().strftime('%d %b %Y %H:%M')}", sub_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e5e7eb"), spaceAfter=16))

        # ── Summary table ──
        summary_data = [
            ["Metric", "Value"],
            ["Expected income",   f"${summary['expected']:.2f}"],
            ["Collected income",  f"${summary['collected']:.2f}"],
            ["Income leakage",    f"${summary['leakage']:.2f}"],
            ["Matched",           str(summary["matched"])],
            ["Missing deposits",  str(summary["missing"])],
            ["Unverified income", str(summary["unverified"])],
            ["Arrears",           str(summary["arrears"])],
        ]

        summary_table = Table(summary_data, colWidths=[9*cm, 6*cm])
        summary_table.setStyle(TableStyle([
            ("BACKGROUND",   (0, 0), (-1, 0),  colors.HexColor("#141414")),
            ("TEXTCOLOR",    (0, 0), (-1, 0),  colors.white),
            ("FONTNAME",     (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTSIZE",     (0, 0), (-1, 0),  10),
            ("FONTSIZE",     (0, 1), (-1, -1), 9),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),   [colors.HexColor("#f9fafb"), colors.white]),
            ("GRID",         (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
            ("LEFTPADDING",  (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING",   (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
            # Highlight leakage in red
            ("TEXTCOLOR",    (1, 3), (1, 3),   colors.HexColor("#b91c1c")),
            ("FONTNAME",     (1, 3), (1, 3),   "Helvetica-Bold"),
        ]))

        story.append(Paragraph("Summary", styles["Heading2"]))
        story.append(Spacer(1, 0.3*cm))
        story.append(summary_table)
        story.append(Spacer(1, 0.8*cm))

        # ── Detailed results table ──
        story.append(Paragraph("Transaction Details", styles["Heading2"]))
        story.append(Spacer(1, 0.3*cm))

        detail_data = [["Tenant", "Expected", "Status", "Flag reason"]]
        status_colors = {
            "matched":         colors.HexColor("#15803d"),
            "missing_deposit": colors.HexColor("#b91c1c"),
            "unverified":      colors.HexColor("#92400e"),
            "arrears":         colors.HexColor("#1d4ed8"),
        }

        for r in rows:
            tenant_name = r.tenant.name if r.tenant else "Unknown"
            expected    = f"${r.expected_amount:.2f}" if r.expected_amount else "—"
            status      = r.status.replace("_", " ").title()
            flag        = r.flag_reason or "—"
            detail_data.append([tenant_name, expected, status, flag])

        detail_table = Table(detail_data, colWidths=[4.5*cm, 3*cm, 3.5*cm, 6*cm])
        detail_table.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0),  colors.HexColor("#141414")),
            ("TEXTCOLOR",     (0, 0), (-1, 0),  colors.white),
            ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, -1), 8),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.HexColor("#f9fafb"), colors.white]),
            ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
            ("LEFTPADDING",   (0, 0), (-1, -1), 6),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("WORDWRAP",      (3, 1), (3, -1),  True),
        ]))

        # Colour status column per row
        for i, r in enumerate(rows, start=1):
            col = status_colors.get(r.status, colors.black)
            detail_table.setStyle(TableStyle([
                ("TEXTCOLOR", (2, i), (2, i), col),
                ("FONTNAME",  (2, i), (2, i), "Helvetica-Bold"),
            ]))

        story.append(detail_table)
        story.append(Spacer(1, 0.8*cm))

        # ── Footer ──
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e5e7eb"), spaceAfter=8))
        story.append(Paragraph(
            "This report was generated by RentTrace. It is intended for audit and forensic review purposes only.",
            ParagraphStyle("Footer", parent=styles["Normal"], fontSize=8, textColor=colors.HexColor("#9ca3af"))
        ))

        doc.build(story)

        return {"success": True, "path": out_path, "filename": filename}

    except Exception as e:
        return {"success": False, "error": str(e)}
