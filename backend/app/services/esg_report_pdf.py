"""
PDF export for ESG reports (Kamra ClimateOS).

Pure formatter: takes the same dict produced by
esg_report_service.generate_brsr_principle6() and renders it as a
PDF using reportlab. No new data, no new calculations.
"""

import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Table,
    TableStyle,
)

STATUS_COLORS = {
    "tracked": colors.HexColor("#1a7f37"),
    "not_tracked": colors.HexColor("#b08800"),
}


def _fmt_datapoint(dp: dict) -> tuple[str, str]:
    """Return (value_text, source_or_note_text) for one indicator datapoint."""
    if dp.get("status") == "tracked":
        value_text = f"{dp['value']} {dp.get('unit', '')}".strip()
        note_text = dp.get("source", "")
    else:
        value_text = "To be collected"
        note_text = dp.get("note", "")
    return value_text, note_text


def _indicator_rows(indicators: dict) -> list[list]:
    """Flatten the essential_indicators dict into table rows."""
    rows = [["Indicator", "Value", "Status / Source"]]

    for entry in indicators.values():
        label = entry.get("label", "")

        # Some indicators (EI_1) have multiple sub-datapoints instead
        # of a single "data" key -- handle both shapes.
        if "data" in entry:
            value_text, note_text = _fmt_datapoint(entry["data"])
            rows.append([label, value_text, note_text])
        else:
            for key, val in entry.items():
                if not isinstance(val, dict) or "status" not in val:
                    continue
                value_text, note_text = _fmt_datapoint(val)
                sub_label = f"{label} — {key.replace('_', ' ')}"
                rows.append([sub_label, value_text, note_text])

    return rows


def generate_brsr_principle6_pdf(report: dict) -> bytes:
    """Render a BRSR Principle 6 report dict as a PDF, return raw bytes."""

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle", parent=styles["Title"], fontSize=16, spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle", parent=styles["Normal"], fontSize=10,
        textColor=colors.HexColor("#555555"), spaceAfter=14,
    )
    section_style = ParagraphStyle(
        "SectionHeading", parent=styles["Heading2"], fontSize=12,
        spaceBefore=14, spaceAfter=6,
    )
    footnote_style = ParagraphStyle(
        "Footnote", parent=styles["Normal"], fontSize=8,
        textColor=colors.HexColor("#777777"), spaceBefore=16,
    )

    story = []

    story.append(Paragraph("Kamra ClimateOS", title_style))
    story.append(
        Paragraph(
            f"{report['framework']} \u2014 {report['section']}<br/>"
            f"Reporting Year: {report['reporting_year']} &nbsp;|&nbsp; "
            f"Organization ID: {report['organization_id']} &nbsp;|&nbsp; "
            f"Generated: {datetime.utcnow().strftime('%d %b %Y, %H:%M UTC')}",
            subtitle_style,
        )
    )

    story.append(Paragraph("Data Basis", section_style))
    story.append(Paragraph(report["data_basis"], styles["Normal"]))

    story.append(Paragraph("Essential Indicators", section_style))

    rows = _indicator_rows(report["essential_indicators"])
    table = Table(rows, colWidths=[70 * mm, 40 * mm, 65 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7f7f7")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(table)

    story.append(Paragraph("Totals", section_style))
    totals = report["totals"]
    totals_rows = [["Metric", "Value"]]
    totals_rows.append(
        ["Scope 1 + Scope 2 (tCO2e)", str(totals["scope1_plus_2_tCO2e"])]
    )
    total_dp = totals["total_all_scopes"]
    value_text, note_text = _fmt_datapoint(total_dp)
    totals_rows.append(["Total, all scopes (tCO2e)", f"{value_text}  ({note_text})"])

    totals_table = Table(totals_rows, colWidths=[80 * mm, 95 * mm])
    totals_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(totals_table)

    story.append(
        Paragraph(
            "Indicators marked \u201cTo be collected\u201d are not yet tracked on "
            "the Kamra ClimateOS platform and are reported honestly as such, "
            "rather than estimated. This report reflects data available as of "
            "the generation timestamp above and is not year-filtered.",
            footnote_style,
        )
    )

    doc.build(story)
    return buffer.getvalue()