"""
Report Studio PDF - renders the tree returned by
report_studio_service.generate_complete_report() into one complete
sustainability report. Pure renderer: no DB access, no calculation.
Indicator-table helpers are imported from esg_report_pdf so numbers are
formatted exactly as in the single-principle PDFs.
"""
import io
from datetime import datetime
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate,
    Spacer, Table, TableStyle,
)

from app.services.esg_report_pdf import _indicator_rows

DEFAULT_THEME = "#1A7F37"
PAGE_W, PAGE_H = A4
MARGIN = 18 * mm
CONTENT_W = PAGE_W - 2 * MARGIN

PRINCIPLE_TITLES = {
    1: "Ethics, Transparency and Accountability",
    2: "Sustainable and Safe Goods and Services",
    3: "Employee Well-being",
    4: "Stakeholder Responsiveness",
    5: "Human Rights",
    6: "Environment",
    7: "Public and Regulatory Policy Advocacy",
    8: "Inclusive Growth and Equitable Development",
    9: "Responsible Engagement with Consumers",
}


# ---------- small helpers ----------

def _txt(v) -> str:
    """Escape for reportlab's Paragraph mini-XML; None -> em dash."""
    if v is None or v == "":
        return "\u2014"
    return escape(str(v)).replace("\n", "<br/>")


def _num(v, unit: str = "", digits: int = 2) -> str:
    if v is None:
        return "\u2014"
    try:
        s = f"{float(v):,.{digits}f}"
    except (TypeError, ValueError):
        s = str(v)
    return f"{s} {unit}".strip()


def _styles(theme: str) -> dict:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("rs_title", parent=base["Title"], fontSize=28,
                                leading=34, textColor=colors.HexColor(theme),
                                alignment=0, spaceAfter=6),
        "subtitle": ParagraphStyle("rs_sub", parent=base["Normal"], fontSize=14,
                                   leading=18, textColor=colors.HexColor("#444444")),
        "h1": ParagraphStyle("rs_h1", parent=base["Heading1"], fontSize=18,
                             leading=22, textColor=colors.HexColor(theme),
                             spaceBefore=4, spaceAfter=8),
        "h2": ParagraphStyle("rs_h2", parent=base["Heading2"], fontSize=12.5,
                             leading=16, textColor=colors.HexColor("#222222"),
                             spaceBefore=10, spaceAfter=4),
        "body": ParagraphStyle("rs_body", parent=base["Normal"], fontSize=9.5,
                               leading=13.5, spaceAfter=6),
        "small": ParagraphStyle("rs_small", parent=base["Normal"], fontSize=8,
                                leading=10.5, textColor=colors.HexColor("#666666")),
        "cell": ParagraphStyle("rs_cell", parent=base["Normal"], fontSize=8,
                               leading=10.5),
        "highlight": ParagraphStyle("rs_hl", parent=base["Normal"], fontSize=12,
                                    leading=16, textColor=colors.HexColor(theme),
                                    fontName="Helvetica-Bold", spaceAfter=6),
    }


def _table(header: list[str], rows: list[list], st: dict, widths: list,
           theme: str) -> Table:
    data = [[Paragraph(f"<b>{_txt(h)}</b>", st["cell"]) for h in header]]
    for row in rows:
        data.append([c if isinstance(c, Paragraph) else Paragraph(_txt(c), st["cell"])
                     for c in row])
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(theme)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#BBBBBB")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F4F6F4")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    # Header row text must be white: override the Paragraph colour via markup.
    for i, h in enumerate(header):
        data[0][i] = Paragraph(f"<font color='white'><b>{_txt(h)}</b></font>", st["cell"])
    return t


def _kv(rows: list[tuple], st: dict, theme: str) -> Table:
    return _table(["Item", "Value"], [[k, v] for k, v in rows], st,
                  [70 * mm, CONTENT_W - 70 * mm], theme)


def _status_note(block: dict, st: dict) -> list:
    """Flowables for a section that is not 'ok' (error / not_tracked / not_written)."""
    status = block.get("status")
    if status == "ok":
        return []
    msg = {
        "not_tracked": "Not yet tracked in Kamra BENAS for this reporting year.",
        "not_written": "Narrative not yet written in Report Studio.",
        "error": "This section could not be generated: " + str(block.get("detail", "")),
    }.get(status, str(block.get("detail", status)))
    return [Paragraph(f"<i>{_txt(msg)}</i>", st["small"]), Spacer(1, 4)]


# ---------- page builders ----------

def _cover(r: dict, st: dict, theme: str) -> list:
    meta, nar = r["meta"], (r["narratives"].get("data") or {})
    org = meta.get("organization_name") or "Organization"
    title = nar.get("cover_title") or f"Sustainability Report {meta['reporting_year']}"
    out = [Spacer(1, 60 * mm),
           HRFlowable(width="100%", thickness=4, color=colors.HexColor(theme)),
           Spacer(1, 8 * mm),
           Paragraph(_txt(title), st["title"])]
    if nar.get("cover_subtitle"):
        out.append(Paragraph(_txt(nar["cover_subtitle"]), st["subtitle"]))
    out += [Spacer(1, 12 * mm),
            Paragraph(f"<b>{_txt(org)}</b>", st["subtitle"]),
            Paragraph(f"Reporting year {meta['reporting_year']}", st["subtitle"]),
            Spacer(1, 40 * mm),
            Paragraph("Prepared with Kamra BENAS \u2014 Net Zero and ESG Intelligence "
                      "Platform. BRSR (SEBI) structure; GHG Protocol Scope 1 and 2.",
                      st["small"]),
            PageBreak()]
    return out


def _leadership(r: dict, st: dict, theme: str) -> list:
    nar = r["narratives"].get("data") or {}
    out = [Paragraph("Message from Leadership", st["h1"])]
    if nar.get("leadership_message"):
        out.append(Paragraph(_txt(nar["leadership_message"]), st["body"]))
        signer = " ".join(x for x in [nar.get("leadership_name"),
                                      f"({nar['leadership_designation']})"
                                      if nar.get("leadership_designation") else None] if x)
        if signer:
            out.append(Paragraph(f"<b>{_txt(signer)}</b>", st["body"]))
    else:
        out += _status_note({"status": "not_written"}, st)
    out.append(PageBreak())
    return out


def _about(r: dict, st: dict, theme: str) -> list:
    nar = r["narratives"].get("data") or {}
    out = [Paragraph("About the Company", st["h1"])]
    out.append(Paragraph(_txt(nar["about_company"]), st["body"]) if nar.get("about_company")
               else Paragraph("<i>Not yet written in Report Studio.</i>", st["small"]))
    milestones = nar.get("milestones") or []
    if milestones:
        out.append(Paragraph("Milestones", st["h2"]))
        rows = [[m.get("year"), m.get("title"), m.get("description")]
                for m in sorted(milestones, key=lambda m: m.get("year", 0))]
        out.append(_table(["Year", "Milestone", "Detail"], rows, st,
                          [18 * mm, 55 * mm, CONTENT_W - 73 * mm], theme))
    out.append(PageBreak())
    return out


def _section_ab(r: dict, st: dict, theme: str) -> list:
    out = [Paragraph("BRSR Section A \u2014 General Disclosures", st["h1"])]
    out += _status_note(r["section_a"], st)
    a = r["section_a"].get("data") or {}
    if a:
        rows = [("CIN", a.get("cin")), ("Year of incorporation", a.get("year_of_incorporation")),
                ("Registered office", a.get("registered_office_address")),
                ("Corporate address", a.get("corporate_address")),
                ("Website", a.get("website")), ("Financial year reported", a.get("financial_year_reported")),
                ("Paid-up capital (INR)", _num(a.get("paid_up_capital_inr"), digits=0)),
                ("Reporting boundary", a.get("reporting_boundary")),
                ("BRSR contact", a.get("brsr_contact_name"))]
        out.append(_kv(rows, st, theme))
    comp = (r["section_a"].get("completeness") or {}).get("data") or {}
    if comp:
        out.append(Paragraph(
            f"Section A completeness: {comp.get('answered_questions')} / "
            f"{comp.get('tracked_questions')} tracked questions "
            f"({comp.get('completeness_percent')}%).", st["small"]))
    out.append(Paragraph("BRSR Section B \u2014 Management and Process Disclosures", st["h1"]))
    out += _status_note(r["section_b"], st)
    b_rows = []
    for p in sorted(r["section_b"].get("data") or [], key=lambda x: x.get("principle", 0)):
        yn = lambda v: "Yes" if v else ("No" if v is False else "\u2014")
        b_rows.append([f"P{p.get('principle')}", yn(p.get("has_policy")),
                       yn(p.get("policy_board_approved")), yn(p.get("extends_to_value_chain")),
                       p.get("commitments_and_targets")])
    if b_rows:
        out.append(_table(["Principle", "Policy", "Board approved", "Value chain", "Commitments / targets"],
                          b_rows, st, [18 * mm, 16 * mm, 24 * mm, 22 * mm, CONTENT_W - 80 * mm], theme))
    out.append(PageBreak())
    return out


def _principles(r: dict, st: dict, theme: str) -> list:
    out = []
    ind_widths = [CONTENT_W * 0.42, CONTENT_W * 0.20, CONTENT_W * 0.38]
    for n in range(1, 10):
        block = r["principles"].get(str(n)) or r["principles"].get(n) or {}
        nar = block.get("narrative") or {}
        head = [Paragraph(f"Principle {n} \u2014 {PRINCIPLE_TITLES[n]}", st["h1"])]
        if nar.get("highlight"):
            head.append(Paragraph(_txt(nar["highlight"]), st["highlight"]))
        if nar.get("sdgs"):
            chips = " &nbsp;|&nbsp; ".join(
                f"SDG {s['number']}: {_txt(s.get('label'))}" for s in nar["sdgs"])
            head.append(Paragraph(f"<font color='{theme}'>{chips}</font>", st["small"]))
        if nar.get("intro"):
            head.append(Paragraph(_txt(nar["intro"]), st["body"]))
        out.append(KeepTogether(head))
        out += _status_note(block, st)
        data = block.get("data") or {}
        for key, label in (("essential_indicators", "Essential indicators"),
                           ("leadership_indicators", "Leadership indicators")):
            ind = data.get(key) or {}
            if not ind:
                continue
            rows = _indicator_rows(ind, st["cell"])
            if rows:
                out.append(Paragraph(label, st["h2"]))
                out.append(_table(["Indicator", "Value", "Source / note"], rows, st,
                                  ind_widths, theme))
        if data.get("data_basis"):
            out.append(Paragraph(f"Data basis: {_txt(data['data_basis'])}", st["small"]))
        out.append(PageBreak())
    return out


def _energy(r: dict, st: dict, theme: str) -> list:
    out = [Paragraph("Energy Balance", st["h1"])] + _status_note(r["energy_balance"], st)
    e = r["energy_balance"].get("data") or {}
    if e:
        out.append(_kv([
            ("Total energy", _num(e.get("total_gj"), "GJ")),
            ("Total energy (toe)", _num(e.get("total_toe"), "toe")),
            ("Electricity", f"{_num(e.get('electricity_kwh'), 'kWh', 0)}  ({_num(e.get('electrical_gj'), 'GJ')})"),
            ("Renewable electricity", _num(e.get("renewable_kwh"), "kWh", 0)),
            ("Thermal (fuels)", _num(e.get("thermal_gj"), "GJ")),
            ("Biomass", _num(e.get("biomass_gj"), "GJ")),
            ("Renewable / non-renewable", f"{_num(e.get('renewable_gj'), 'GJ')} / {_num(e.get('non_renewable_gj'), 'GJ')}"),
            ("Manufacturing units with data", e.get("units_with_data")),
        ], st, theme))
        by_fuel = e.get("by_fuel_gj") or {}
        if by_fuel:
            out.append(Paragraph("Energy by fuel", st["h2"]))
            out.append(_table(["Fuel", "GJ"], [[k, _num(v)] for k, v in by_fuel.items()],
                              st, [90 * mm, CONTENT_W - 90 * mm], theme))
    out.append(PageBreak())
    return out


def _ghg(r: dict, st: dict, theme: str) -> list:
    out = [Paragraph("GHG Emissions \u2014 Scope 1 and 2", st["h1"])] + _status_note(r["ghg"], st)
    g = r["ghg"].get("data") or {}
    if g:
        out.append(_kv([
            ("Scope 1 (direct)", _num(g.get("scope1_tco2e"), "tCO2e")),
            ("Scope 2 (purchased electricity)", _num(g.get("scope2_tco2e"), "tCO2e")),
            ("Total Scope 1 + 2", _num(g.get("total_tco2e"), "tCO2e")),
            ("Scope 3", "Not tracked"),
            ("Source", g.get("source")),
        ], st, theme))
        out.append(Paragraph("Emission factors: DEFRA / India CEA grid factor / IPCC 2006 "
                             "as recorded per source in Kamra BENAS.", st["small"]))
    out.append(PageBreak())
    return out


def _water_waste(r: dict, st: dict, theme: str) -> list:
    out = [Paragraph("Water and Waste", st["h1"])] + _status_note(r["water_waste"], st)
    d = r["water_waste"].get("data") or {}
    w, ws = d.get("water") or {}, d.get("waste") or {}
    if w:
        out.append(Paragraph("Water (kilolitres)", st["h2"]))
        out.append(_kv([("Withdrawal", _num(w.get("total_withdrawal_kl"), "KL")),
                        ("Discharge", _num(w.get("total_discharge_kl"), "KL")),
                        ("Consumption (withdrawal \u2212 discharge)", _num(w.get("total_consumption_kl"), "KL")),
                        ("Records in water-stressed areas", w.get("water_stressed_records")),
                        ("Records", w.get("record_count"))], st, theme))
    if ws:
        out.append(Paragraph("Waste (metric tonnes)", st["h2"]))
        out.append(_kv([("Generated", _num(ws.get("total_generated_mt"), "MT")),
                        ("of which hazardous", _num(ws.get("hazardous_generated_mt"), "MT")),
                        ("Recovered (recycled / reused / other)", _num(ws.get("total_recovered_mt"), "MT")),
                        ("Disposed", _num(ws.get("total_disposed_mt"), "MT")),
                        ("Records", ws.get("record_count"))], st, theme))
    out.append(PageBreak())
    return out


def _net_zero(r: dict, st: dict, theme: str) -> list:
    out = [Paragraph("Net Zero Pathway", st["h1"])] + _status_note(r["net_zero"], st)
    targets = r["net_zero"].get("data") or []
    if not targets and r["net_zero"].get("status") == "ok":
        out.append(Paragraph("<i>No net-zero targets defined.</i>", st["small"]))
    for t in targets:
        out.append(Paragraph(_txt(t.get("target_name")), st["h2"]))
        out.append(_kv([
            ("Baseline", f"{t.get('baseline_year')}: {_num(t.get('baseline_co2e_tonnes'), 'tCO2e')}"),
            ("Target", f"{t.get('target_year')}: {_num(t.get('target_co2e_tonnes'), 'tCO2e')} "
                       f"({_num(t.get('reduction_percentage'), '%', 1)} reduction)"),
            ("Current year actual", f"{t.get('current_year')}: {_num(t.get('current_actual_co2e_tonnes'), 'tCO2e')}"),
            ("Expected on trajectory", _num(t.get("expected_co2e_tonnes_on_trajectory"), "tCO2e")),
            ("Status", t.get("status")),
        ], st, theme))
    out.append(PageBreak())
    return out


def _climate_risk(r: dict, st: dict, theme: str) -> list:
    out = [Paragraph("Climate Risk", st["h1"])] + _status_note(r["climate_risk"], st)
    c = r["climate_risk"].get("data") or {}
    if c:
        out.append(_kv([
            ("Risks registered", c.get("total_risks")),
            ("Estimated financial impact", _num(c.get("total_estimated_financial_impact_inr"), "INR", 0)),
            ("Mitigation cost", _num(c.get("total_mitigation_cost_inr"), "INR", 0)),
            ("Mitigation benefit", _num(c.get("total_mitigation_benefit_inr"), "INR", 0)),
            ("Net risk exposure", _num(c.get("total_net_risk_exposure_inr"), "INR", 0)),
        ], st, theme))
        cat = c.get("net_risk_exposure_by_category_inr") or {}
        if cat:
            out.append(Paragraph("Net exposure by category", st["h2"]))
            out.append(_table(["Category", "INR"], [[k, _num(v, "", 0)] for k, v in cat.items()],
                              st, [90 * mm, CONTENT_W - 90 * mm], theme))
    out.append(Paragraph("Materiality Assessment", st["h1"]))
    out += _status_note(r["materiality"], st)
    out.append(PageBreak())
    return out


def _method(r: dict, st: dict, theme: str) -> list:
    meta = r["meta"]
    return [Paragraph("About this Report", st["h1"]),
            Paragraph("Structure follows SEBI BRSR (Sections A, B and C, Principles 1\u20139). "
                      "GHG accounting follows the GHG Protocol; Scope 1 covers on-site fuel "
                      "combustion and process emissions, Scope 2 covers purchased electricity "
                      "using the applicable grid factor. Energy is reported in GJ and toe "
                      "(BEE PAT convention). Every figure is generated from records in Kamra "
                      "BENAS; items marked 'To be collected' have no record for the year.",
                      st["body"]),
            Paragraph(f"Generated {_txt(meta.get('generated_at'))} for organization "
                      f"{_txt(meta.get('organization_name'))}, reporting year "
                      f"{meta.get('reporting_year')}.", st["small"])]


# ---------- entry point ----------

def generate_complete_report_pdf(report: dict) -> bytes:
    theme = (report.get("meta") or {}).get("theme_colour") or DEFAULT_THEME
    st = _styles(theme)
    org = (report.get("meta") or {}).get("organization_name") or ""
    year = (report.get("meta") or {}).get("reporting_year")

    def _footer(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor(theme))
        canvas.setLineWidth(1.2)
        canvas.line(MARGIN, PAGE_H - MARGIN + 6, PAGE_W - MARGIN, PAGE_H - MARGIN + 6)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#666666"))
        canvas.drawString(MARGIN, 10 * mm, f"{org}  |  Sustainability Report {year}")
        canvas.drawRightString(PAGE_W - MARGIN, 10 * mm, f"Page {doc.page}")
        canvas.restoreState()

    story = []
    for build in (_cover, _leadership, _about, _section_ab, _principles, _energy,
                  _ghg, _water_waste, _net_zero, _climate_risk, _method):
        story += build(report, st, theme)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN,
                            topMargin=MARGIN, bottomMargin=MARGIN,
                            title=f"Sustainability Report {year}", author=org)
    doc.build(story, onFirstPage=lambda c, d: None, onLaterPages=_footer)
    return buf.getvalue()
