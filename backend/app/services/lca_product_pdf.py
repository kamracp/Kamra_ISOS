"""Product LCA (PLCA) report PDF for one LCA product -- pure function, no DB access.

Renders exactly what GET /lca-products/{id} returns: header, GWP per functional unit,
stage breakdown, inventory with resolved factors and citations, unresolved items shown
as such (never hidden, never zero), factor source list. reportlab platypus, A4.
"""
from __future__ import annotations

import io
from datetime import datetime, timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

STAGE_LABELS = {"raw_materials": "Raw materials (A1)", "inbound_transport": "Inbound transport (A2)",
                "manufacturing": "Manufacturing (A3)", "packaging": "Packaging", "outbound_transport": "Outbound transport (A4)"}
BUCKET_LABELS = {None: "", "direct": "CBAM direct", "indirect": "CBAM indirect", "precursor": "CBAM precursor", "excluded": "CBAM excluded"}


def _n(v, d: int = 3) -> str:
    """Null -> '-' so an unresolved value is visibly unresolved, never a silent 0."""
    return "-" if v is None else f"{v:,.{d}f}"


def _table(rows: list[list], widths: list[float], header: bool = True) -> Table:
    t = Table(rows, colWidths=widths, repeatRows=1 if header else 0)
    style = [("FONTSIZE", (0, 0), (-1, -1), 8), ("VALIGN", (0, 0), (-1, -1), "TOP"),
             ("GRID", (0, 0), (-1, -1), 0.3, colors.grey), ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3)]
    if header:
        style += [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E78")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                  ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold")]
    t.setStyle(TableStyle(style))
    return t


def generate_plca_pdf(p: dict, org_name: str | None = None) -> bytes:
    ss = getSampleStyleSheet()
    h1, h2, body = ss["Title"], ss["Heading2"], ss["BodyText"]
    small = ParagraphStyle("small", parent=body, fontSize=8, leading=10)
    cell = ParagraphStyle("cell", parent=body, fontSize=8, leading=10)
    fu = f"{p['functional_unit_qty']:g} {p['functional_unit']}"
    story = [Paragraph("Product Life Cycle Assessment (PLCA) Report", h1),
             Paragraph(f"<b>{p['name']}</b>{(' · ' + p['product_code']) if p.get('product_code') else ''}", body),
             Paragraph(f"Functional unit: {fu} · System boundary: {p.get('system_boundary', '').replace('_', ' ')} · "
                       f"Production country: {p.get('production_country_code')} · Reference year: {p.get('reference_year') or '-'}", body),
             Paragraph(f"Prepared by: {org_name or '-'} · Generated: {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC · Kamra ClimateOS", small),
             Spacer(1, 6 * mm), Paragraph("1. Result", h2)]
    story.append(_table([["Indicator", "Value", "Unit"],
                         ["GWP (fossil), cradle to gate", _n(p.get("gwp_kgco2e_per_fu")), f"kgCO2e per {fu}"],
                         ["Biogenic CO2 (reported separately)", _n(p.get("biogenic_co2_kg_per_fu")), f"kg CO2 per {fu}"],
                         ["Inventory items / unresolved", f"{p.get('item_count', 0)} / {p.get('unresolved_count', 0)}", ""]],
                        [80 * mm, 40 * mm, 50 * mm]))
    if p.get("unresolved_count"):
        story.append(Paragraph(f"<b>Note:</b> {p['unresolved_count']} item(s) could not be computed; GWP above excludes them and is therefore incomplete.", small))

    story += [Spacer(1, 5 * mm), Paragraph("2. Contribution by life-cycle stage", h2)]
    rows = [["Stage", "Items", f"kgCO2e / {fu}", "Share %"]]
    for s in p.get("by_stage", []):
        rows.append([STAGE_LABELS.get(s["stage"], s["stage"]), str(s.get("item_count", 0)), _n(s.get("co2e_kg_per_fu")), _n(s.get("share_percent"), 1)])
    story.append(_table(rows, [70 * mm, 25 * mm, 40 * mm, 35 * mm]))

    story += [Spacer(1, 5 * mm), Paragraph("3. Life-cycle inventory and resolved factors", h2)]
    rows = [["Item", "Stage", f"Qty / FU", "Factor (source)", f"kgCO2e / FU", "Status"]]
    for i in p.get("items", []):
        factor = f"{_n(i.get('factor_value'), 4)} kgCO2e/{i.get('factor_unit') or i.get('unit')}<br/><font size=6>{i.get('factor_citation') or ''}</font>"
        bucket = BUCKET_LABELS.get(i.get("cbam_bucket"), "")
        rows.append([Paragraph(f"{i['name']}{('<br/><font size=6>' + bucket + '</font>') if bucket else ''}", cell),
                     Paragraph(STAGE_LABELS.get(i["stage"], i["stage"]), cell),
                     Paragraph(f"{_n(i.get('quantity_per_fu'), 6)} {i.get('unit')}", cell),
                     Paragraph(factor, cell), _n(i.get("co2e_kg_per_fu")), i.get("status", "")])
    story.append(_table(rows, [38 * mm, 28 * mm, 26 * mm, 52 * mm, 22 * mm, 22 * mm]))

    story += [Spacer(1, 5 * mm), Paragraph("4. Factor sources", h2)]
    for src in p.get("factor_sources", []) or ["-"]:
        story.append(Paragraph(f"• {src}", small))
    story += [Spacer(1, 4 * mm),
              Paragraph("Method: activity data × emission factor per inventory line, allocated to the functional unit (annual totals ÷ annual output). "
                        "Factors are resolved at generation time from cited sources (IPCC 2006, CEA India grid, DEFRA); no estimated values. "
                        "Biogenic CO2 is reported separately and not included in fossil GWP. Model is exportable to openLCA (JSON-LD) for reproduction.", small)]

    buf = io.BytesIO()
    SimpleDocTemplate(buf, pagesize=A4, leftMargin=15 * mm, rightMargin=15 * mm, topMargin=15 * mm, bottomMargin=15 * mm,
                      title=f"PLCA - {p['name']}").build(story)
    return buf.getvalue()
