"""Product LCA (PLCA) report PDF for one LCA product -- pure function, no DB access.

Structure follows ISO 14044:2006 clause 5 (third-party report) as laid out in EN 15804 background
reports: 1 Introduction, 2 Goal and scope, 3 Life cycle inventory, 4 Data quality (incl. mass balance),
5 Results, 6 Interpretation, 7 References. Renders exactly what GET /lca-products/{id} returns;
unresolved items are shown as such (never hidden, never zero). References come from
app/services/lca_references.py so nothing is cited that is not registered. reportlab platypus, A4.
"""
from __future__ import annotations

import io
from datetime import datetime, timezone
from xml.sax.saxutils import escape as _e

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.services.lca_references import REFERENCES

STAGE_LABELS = {"raw_materials": "Raw materials (A1)", "inbound_transport": "Inbound transport (A2)",
                "manufacturing": "Manufacturing (A3)", "packaging": "Packaging", "outbound_transport": "Outbound transport (A4)"}
BUCKET_LABELS = {None: "", "direct": "CBAM direct", "indirect": "CBAM indirect", "precursor": "CBAM precursor", "excluded": "CBAM excluded"}
_MASS_TO_KG = {"kg": 1.0, "kgs": 1.0, "tonne": 1000.0, "tonnes": 1000.0, "t": 1000.0, "mt": 1000.0, "g": 0.001}
# Methodology references cited in every report; factor-database refs are added from the factors actually used.
_METHOD_REFS = ["iso_14040_2006", "iso_14044_2006", "iso_14067_2018", "en_15804_a2_2019", "ghgp_product_2011",
                "ipcc_ar5_gwp100", "kes_conv_factor_resolution"]
_FACTOR_REF_BY_KEYWORD = [("DEFRA", "defra_2026_flat_v1_2"), ("DESNZ", "defra_2026_flat_v1_2"), ("IPCC 2006 Vol.3", "ipcc_2006_vol3_ch2_ch4"),
                          ("IPCC 2006", "ipcc_2006_vol2_ch2"), ("Version 21", "cea_co2_baseline_v21_2025"), ("V21", "cea_co2_baseline_v21_2025"),
                          ("Version 20", "cea_co2_baseline_v20_2024"), ("V20", "cea_co2_baseline_v20_2024")]


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


def _refs_used(p: dict) -> list[str]:
    ids = list(_METHOD_REFS)
    for src in p.get("factor_sources", []) or []:
        for kw, rid in _FACTOR_REF_BY_KEYWORD:
            if kw in src and rid not in ids:
                ids.append(rid); break
    b = p.get("benchmark")
    if b and b.get("ref") and b["ref"] not in ids:
        ids += [b["ref"], "iso_14025_2006", "kes_conv_plausibility_band"]
    if (p.get("mci") or {}).get("status") == "calculated":
        ids += ["emf_mci_v1_1_2019", "kes_conv_mci_inputs"]
    return [i for i in ids if i in REFERENCES]


def generate_plca_pdf(p: dict, org_name: str | None = None) -> bytes:
    ss = getSampleStyleSheet()
    h1, h2, body = ss["Title"], ss["Heading2"], ss["BodyText"]
    small = ParagraphStyle("small", parent=body, fontSize=8, leading=10)
    cell = ParagraphStyle("cell", parent=body, fontSize=8, leading=10)
    fu = f"{p['functional_unit_qty']:g} {p['functional_unit']}"
    boundary = (p.get("system_boundary") or "").replace("_", " ")
    items = p.get("items", [])
    calc = [i for i in items if i.get("status") == "calculated"]
    unresolved = [i for i in items if i.get("status") != "calculated"]
    P = lambda t, s=body: Paragraph(t, s)   # noqa: E731

    story = [P("Product Life Cycle Assessment (PLCA) Report", h1),
             P(f"<b>{_e(p['name'])}</b>{(' · ' + _e(p['product_code'])) if p.get('product_code') else ''} · functional unit {fu} · {boundary}"),
             Spacer(1, 4 * mm)]

    # 1 Introduction --------------------------------------------------------------------------
    story += [P("1. Introduction", h2),
              P(f"<b>Commissioner:</b> {_e(org_name or '-')} · <b>Practitioner / tool:</b> Kamra ClimateOS LCA/PCF Studio (Kamra Engineering Solutions) · "
                f"<b>Report date:</b> {datetime.now(timezone.utc):%Y-%m-%d} UTC · <b>Reference year of data:</b> {p.get('reference_year') or '-'}", small),
              P("<b>Standards applied:</b> ISO 14040:2006 and ISO 14044:2006 (LCA framework and requirements), ISO 14067:2018 (product carbon footprint), "
                "EN 15804+A2 module definitions (A1-A3 = cradle-to-gate), GHG Protocol Product Standard. Impact category reported: climate change (GWP-100, IPCC AR5) only.", small),
              P("<b>Purpose and audience:</b> internal product carbon footprint for management, customer and EPD-preparation use. This report is NOT a comparative "
                "assertion for public disclosure and has NOT been critically reviewed by a third party (ISO 14044 clause 6); a verification statement space is provided below.", small),
              P("<b>Verification:</b> ____________________________ (reviewer, organisation, date)", small), Spacer(1, 3 * mm)]

    # 2 Goal and scope ------------------------------------------------------------------------
    story += [P("2. Goal and scope", h2),
              P(f"<b>Functional / declared unit:</b> {fu}" + (f" (declared mass {p['fu_mass_kg']:g} kg)" if p.get("fu_mass_kg") else " (declared mass per unit: not stated)"), small),
              P(f"<b>Product:</b> {_e(p.get('description') or '-')} · production country {p.get('production_country_code', '-')} (grid factor country).", small),
              P(f"<b>System boundary:</b> {boundary}. Stages modelled: " + ", ".join(STAGE_LABELS[s['stage']] for s in p.get('by_stage', []) if s.get('item_count'))
                + ". Not modelled: installation, use, end of life (outside cradle-to-gate) and capital goods.", small),
              P("<b>Allocation:</b> items entered as annual totals are allocated to the functional unit by dividing by annual output "
                f"({_n(p.get('annual_output_qty'), 0)} {p['functional_unit']}/year); no economic allocation. "
                "<b>Cut-off:</b> no mass cut-off is applied; an item whose unit does not match its factor's unit, or whose factor is missing, is reported as "
                "unresolved and EXCLUDED from the total (listed in section 4.2), never approximated.", small), Spacer(1, 3 * mm)]

    # 3 Life cycle inventory ------------------------------------------------------------------
    story += [P("3. Life cycle inventory", h2),
              P("Activity data per functional unit and the emission factor resolved for each line. Source column = where the activity figure came from (invoice, weighbridge, ERP).", small)]
    rows = [["Item", "Stage", "Qty / FU", "Basis", "Activity data source", "Factor (kgCO2e/unit) and citation", "kgCO2e/FU", "Status"]]
    for i in items:
        bucket = BUCKET_LABELS.get(i.get("cbam_bucket"), "")
        factor = f"{_n(i.get('factor_value'), 5)} / {i.get('factor_unit') or '-'}<br/><font size=6>{_e(i.get('factor_citation') or '-')}</font>"
        rows.append([P(f"{_e(i['name'])}{('<br/><font size=6>' + bucket + '</font>') if bucket else ''}", cell), P(STAGE_LABELS.get(i["stage"], i["stage"]), cell),
                     P(f"{_n(i.get('quantity_per_fu'), 6)} {i.get('unit')}", cell), P((i.get("basis") or "").replace("_", " "), cell),
                     P(_e(i.get("data_source") or "not stated"), cell), P(factor, cell), _n(i.get("co2e_kg_per_fu")), i.get("status", "")])
    story += [_table(rows, [30 * mm, 22 * mm, 20 * mm, 16 * mm, 22 * mm, 42 * mm, 16 * mm, 14 * mm]), Spacer(1, 3 * mm)]

    # 4 Data quality --------------------------------------------------------------------------
    story += [P("4. Data quality", h2),
              P("<b>4.1 Representativeness.</b> Activity data are primary, plant-specific figures entered by the commissioner for the reference year. "
                "Emission factors are secondary, from the published databases listed in section 7 (temporal and geographical coverage as stated there; "
                "DEFRA material factors are UK-basis proxies where no India-specific factor exists).", small),
              P(f"<b>4.2 Completeness.</b> {len(items)} inventory lines, {len(calc)} calculated, {len(unresolved)} unresolved" +
                (": " + "; ".join(f"{_e(i['name'])} ({i.get('status')})" for i in unresolved) if unresolved else "") + ".", small)]
    mass_in = sum((i.get("quantity_per_fu") or 0) * _MASS_TO_KG.get((i.get("unit") or "").lower(), 0)
                  for i in calc if i.get("stage") == "raw_materials" and i.get("factor_source") != "fuel")
    declared = p.get("fu_mass_kg")
    if declared:
        ratio = mass_in / declared if declared else None
        mb = f"raw-material mass entered {mass_in:,.3f} kg/FU vs declared product mass {declared:g} kg/FU = {ratio:.2f}. " + \
             ("Within 0.9-1.3 (process losses expected)." if ratio and 0.9 <= ratio <= 1.3 else "OUTSIDE 0.9-1.3 - check missing raw materials or unit errors.")
    else:
        mb = f"raw-material mass entered {mass_in:,.3f} kg/FU; declared product mass not stated, so the balance cannot be closed."
    story += [P(f"<b>4.3 Mass balance.</b> {mb}", small),
              P("<b>4.4 Datasets.</b> " + " | ".join(_e(s) for s in (p.get("factor_sources") or ["-"])), small), Spacer(1, 3 * mm)]

    # 5 Results -------------------------------------------------------------------------------
    story += [P("5. Results", h2),
              _table([["Indicator", "Value", "Unit"],
                      ["Global warming potential, fossil (GWP-100, IPCC AR5)", _n(p.get("gwp_kgco2e_per_fu")), f"kgCO2e per {fu}"],
                      ["Biogenic CO2 (reported separately, not in GWP fossil)", _n(p.get("biogenic_co2_kg_per_fu")), f"kg per {fu}"]],
                     [90 * mm, 30 * mm, 60 * mm])]
    if unresolved:
        story.append(P(f"<b>Note:</b> {len(unresolved)} item(s) could not be computed; the GWP above excludes them and is therefore incomplete.", small))
    st = [["Life-cycle stage", "Items", "kgCO2e / FU", "Share"]]
    for s in p.get("by_stage", []):
        if s.get("item_count"):
            st.append([STAGE_LABELS.get(s["stage"], s["stage"]), s["item_count"], _n(s.get("co2e_kg_per_fu")), f"{_n(s.get('share_percent'), 1)} %"])
    story += [Spacer(1, 2 * mm), _table(st, [70 * mm, 20 * mm, 40 * mm, 30 * mm]), Spacer(1, 3 * mm)]

    # 6 Interpretation ------------------------------------------------------------------------
    story += [P("6. Interpretation", h2)]
    if calc:
        top = max(calc, key=lambda i: i.get("co2e_kg_per_fu") or 0)
        gwp = p.get("gwp_kgco2e_per_fu") or 0
        story.append(P(f"<b>6.1 Hotspot.</b> Largest single contributor: {_e(top['name'])} ({STAGE_LABELS.get(top['stage'], top['stage'])}), "
                       f"{_n(top.get('co2e_kg_per_fu'))} kgCO2e/FU" + (f" = {100 * (top.get('co2e_kg_per_fu') or 0) / gwp:.1f}% of GWP." if gwp else "."), small))
    b = p.get("benchmark")
    if b:
        if b.get("status") == "calculated":
            story.append(P(f"<b>6.2 Plausibility check against published benchmark.</b> {_e(b.get('label', ''))}: {b.get('value_kgco2e_per_fu')} kgCO2e/{b.get('functional_unit')} "
                           f"({_e(b.get('boundary', ''))}). This product = {b.get('ratio')}x the benchmark. {_e(b.get('warning') or 'Within the 0.5x-2x plausibility band.')} "
                           "The benchmark is a warning device only and does not alter the result.", small))
        else:
            story.append(P(f"<b>6.2 Plausibility check.</b> Benchmark selected but not compared: {_e(b.get('reason', ''))}.", small))
    m = p.get("mci") or {}
    if m.get("status") == "calculated":
        story.append(P(f"<b>6.3 Material Circularity Indicator (EMF v1.1).</b> MCI = {m.get('mci')} (LFI {m.get('lfi')}, {_e(m.get('utility_note', ''))}); "
                       f"product mass {_n(m.get('mass_kg_per_fu'))} kg/FU; Fr {m.get('fr')}, Fu {m.get('fu')}, Cr {m.get('cr')}, Cu {m.get('cu')}.", small))
    elif m:
        story.append(P(f"<b>6.3 Material Circularity Indicator.</b> Not computed: {_e(m.get('reason') or '')}.", small))
    story += [P("<b>6.4 Limitations.</b> Single impact category (climate change); no critical review; secondary factors are database averages, not supplier-specific; "
                "results are not comparable with other studies unless functional unit, boundary and data quality match (ISO 14044 clause 4.2.3.7).", small), Spacer(1, 3 * mm)]

    # 7 References ----------------------------------------------------------------------------
    story += [P("7. References", h2)]
    for n, rid in enumerate(_refs_used(p), 1):
        r = REFERENCES[rid]
        story.append(P(f"[{n}] {_e(r['citation'])}" + (f" {_e(r['url'])}" if r.get("url") else "") + f" <font size=6>({r['type']}, id {rid})</font>", small))
    story.append(P("Model exportable to openLCA (JSON-LD) for independent reproduction.", small))

    buf = io.BytesIO()
    SimpleDocTemplate(buf, pagesize=A4, leftMargin=15 * mm, rightMargin=15 * mm, topMargin=15 * mm, bottomMargin=15 * mm,
                      title=f"PLCA - {p['name']}").build(story)
    return buf.getvalue()
