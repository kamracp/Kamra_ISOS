"""PAT SEC Report — BEE Perform-Achieve-Trade compliance view for one
organization and year.

Builder returns a plain dict (served as JSON); the PDF renders that dict.
Every number comes from the same engines the UI uses (PatSecService,
energy_service.unit_year_balance, org_year_energy) so report == screen.
Null stays null: a unit without a target or without production data is
listed with '-' and an explicit status, never a silent zero.
"""

import io
from datetime import datetime, timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from sqlalchemy.orm import Session

from app.repositories.manufacturing_unit_repository import ManufacturingUnitRepository
from app.services.energy_service import GJ_PER_TOE, org_year_energy, unit_year_balance
from app.services.lca_product_pdf import _n, _table
from app.services.pat_sec_service import PatSecService


def _enum(v):
    return getattr(v, "value", v)


def _status(summary: dict) -> str:
    if summary.get("actual_sec_gj_per_unit") is None:
        return "no_data"
    if summary.get("target") is None:
        return "no_target"
    return "on_track" if summary.get("on_track") else "gap"


STATUS_LABEL = {
    "on_track": "Target met",
    "gap": "Gap to target",
    "no_target": "No PAT target set",
    "no_data": "No production/energy data",
}


def build_pat_sec_report(db: Session, organization_id: int, year: int) -> dict:
    units = [u for u in ManufacturingUnitRepository(db, organization_id=organization_id).get_all() if u.is_active]
    pat = PatSecService(db, organization_id)
    rows = []
    for u in units:
        s = pat.get_pat_summary(u.id, year)
        b = unit_year_balance(db, organization_id, u.id, year)
        t = b.get("year_totals") or {}
        # No production periods this year -> totals are unknown, not zero.
        if not b.get("periods"):
            t = {k: (None if k in ("total_energy_toe", "total_energy_gj", "electricity_kwh", "thermal_gj") else v)
                 for k, v in t.items()}
        target = s.get("target")
        actual = s.get("actual_sec_gj_per_unit")
        target_sec = target["target_sec_gj_per_unit"] if target else None
        delta_pct = round((actual - target_sec) / target_sec * 100, 2) if (actual is not None and target_sec) else None
        rows.append({
            "manufacturing_unit_id": u.id,
            "unit_code": u.unit_code,
            "unit_name": u.unit_name,
            "sector": _enum(u.sector),
            "country_code": u.country_code,
            "baseline_year": u.baseline_year,
            "cycle": f"PAT-{target['cycle_number']} ({target['cycle_start_year']}-{target['cycle_end_year']})" if target else None,
            "baseline_sec_gj_per_unit": target["baseline_sec_gj_per_unit"] if target else None,
            "mandated_reduction_percent": target["mandated_reduction_percent"] if target else None,
            "target_sec_gj_per_unit": target_sec,
            "actual_sec_gj_per_unit": actual,
            "delta_vs_target_percent": delta_pct,
            "status": _status(s),
            "production_quantity": s.get("actual_production_qty"),
            "production_unit": target["production_unit"] if target else None,
            "thermal_sec_gcal_per_unit": t.get("thermal_sec_gcal_per_unit"),
            "electrical_sec_kwh_per_unit": t.get("electrical_sec_kwh_per_unit"),
            "sec_toe_per_unit": t.get("sec_toe_per_unit"),
            "total_energy_toe": t.get("total_energy_toe"),
            "electricity_kwh": t.get("electricity_kwh"),
            "pat_dc_threshold_toe": t.get("pat_dc_threshold_toe"),
            "is_designated_consumer_scale": t.get("is_designated_consumer_scale"),
            "periods_without_energy_data": b.get("periods_without_energy_data") or [],
        })
    org = org_year_energy(db, organization_id, year)
    return {
        "framework": "BEE PAT",
        "section": "Specific Energy Consumption (SEC) Report",
        "reporting_year": year,
        "organization_id": organization_id,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "units": rows,
        "org_energy": org,
        "counts": {
            "units": len(rows),
            "target_met": sum(1 for r in rows if r["status"] == "on_track"),
            "gap": sum(1 for r in rows if r["status"] == "gap"),
            "no_target": sum(1 for r in rows if r["status"] == "no_target"),
            "no_data": sum(1 for r in rows if r["status"] == "no_data"),
        },
        "methodology": [
            "SEC (GJ per production unit) = total site energy / production quantity for the reporting year; "
            "gate-to-gate, consistent with BEE PAT Form-1 / ISO 50001 energy review.",
            "Electricity converted at 0.0036 GJ/kWh; fuels at IPCC 2006 lower heating values from the platform fuel library; "
            f"1 toe = {GJ_PER_TOE} GJ.",
            "Target SEC = baseline SEC x (1 - mandated reduction %), from the PAT cycle target entered for the unit. "
            "Units without a target or without production/energy data are reported as such, never estimated.",
            "Designated-Consumer scale is checked against the sector threshold (toe/year) notified under the Energy Conservation Act.",
        ],
    }


# ----------------------------------------------------------------------- PDF

def _p(text, style):
    return Paragraph("" if text is None else str(text), style)


def generate_pat_sec_pdf(report: dict, org_name: str | None = None) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4), leftMargin=12 * mm, rightMargin=12 * mm,
                            topMargin=12 * mm, bottomMargin=12 * mm)
    ss = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=ss["Title"], fontSize=16, spaceAfter=2)
    h2 = ParagraphStyle("h2", parent=ss["Heading2"], fontSize=11, spaceBefore=8, spaceAfter=4)
    meta = ParagraphStyle("meta", parent=ss["Normal"], fontSize=8, textColor=colors.grey)
    body = ParagraphStyle("body", parent=ss["Normal"], fontSize=8)
    cell = ParagraphStyle("cell", parent=ss["Normal"], fontSize=7.5, leading=9)
    W = doc.width

    story = [
        _p(org_name or "Kamra ClimateOS", h1),
        _p(f"{report['framework']} — {report['section']}", body),
        _p(f"Reporting Year: {report['reporting_year']} | Organization ID: {report['organization_id']} | "
           f"Generated: {report['generated_at']}", meta),
        Spacer(1, 4 * mm),
    ]

    c = report["counts"]
    story.append(_p(f"Units: {c['units']} &nbsp;|&nbsp; Target met: {c['target_met']} &nbsp;|&nbsp; Gap to target: {c['gap']} "
                    f"&nbsp;|&nbsp; No target: {c['no_target']} &nbsp;|&nbsp; No data: {c['no_data']}", body))

    story.append(_p("1. PAT compliance by unit", h2))
    hdr = ["Unit", "Sector", "Cycle", "Baseline SEC (GJ/u)", "Mandated %", "Target SEC (GJ/u)",
           "Actual SEC (GJ/u)", "Δ vs target %", "Production", "Status"]
    rows = [[_p(h, cell) for h in hdr]]
    for r in report["units"]:
        prod = f"{_n(r['production_quantity'], 2)} {r['production_unit'] or ''}".strip() if r["production_quantity"] is not None else "-"
        rows.append([_p(f"{r['unit_code']} {r['unit_name']}", cell), _p(r["sector"], cell), _p(r["cycle"] or "-", cell),
                     _p(_n(r["baseline_sec_gj_per_unit"], 4), cell), _p(_n(r["mandated_reduction_percent"], 2), cell),
                     _p(_n(r["target_sec_gj_per_unit"], 4), cell), _p(_n(r["actual_sec_gj_per_unit"], 4), cell),
                     _p(_n(r["delta_vs_target_percent"], 2), cell), _p(prod, cell), _p(STATUS_LABEL[r["status"]], cell)])
    story.append(_table(rows, [W * f for f in (0.16, 0.09, 0.11, 0.09, 0.07, 0.09, 0.09, 0.08, 0.10, 0.12)]))

    story.append(_p("2. Energy balance by unit (gate-to-gate)", h2))
    hdr = ["Unit", "Thermal SEC (Gcal/u)", "Electrical SEC (kWh/u)", "SEC (toe/u)", "Total energy (toe)",
           "Electricity (kWh)", "DC threshold (toe)", "DC scale", "Periods w/o energy data"]
    rows = [[_p(h, cell) for h in hdr]]
    for r in report["units"]:
        dc = "-" if r["is_designated_consumer_scale"] is None else ("Yes" if r["is_designated_consumer_scale"] else "No")
        rows.append([_p(f"{r['unit_code']} {r['unit_name']}", cell), _p(_n(r["thermal_sec_gcal_per_unit"], 4), cell),
                     _p(_n(r["electrical_sec_kwh_per_unit"], 2), cell), _p(_n(r["sec_toe_per_unit"], 5), cell),
                     _p(_n(r["total_energy_toe"], 2), cell), _p(_n(r["electricity_kwh"], 0), cell),
                     _p(_n(r["pat_dc_threshold_toe"], 0), cell), _p(dc, cell),
                     _p(str(len(r["periods_without_energy_data"])), cell)])
    story.append(_table(rows, [W * f for f in (0.18, 0.11, 0.11, 0.09, 0.11, 0.11, 0.10, 0.07, 0.12)]))

    o = report["org_energy"]
    story.append(_p("3. Organization energy balance", h2))
    rows = [[_p(k, cell), _p(v, cell)] for k, v in (
        ("Total energy", f"{_n(o.get('total_gj'), 2)} GJ = {_n(o.get('total_toe'), 2)} toe"),
        ("Electrical", f"{_n(o.get('electrical_gj'), 2)} GJ ({_n(o.get('electricity_kwh'), 0)} kWh)"),
        ("Thermal", f"{_n(o.get('thermal_gj'), 2)} GJ"),
        ("Renewable", f"{_n(o.get('renewable_gj'), 2)} GJ ({_n(o.get('renewable_kwh'), 0)} kWh renewable electricity; biomass {_n(o.get('biomass_gj'), 2)} GJ)"),
        ("Units with data / records", f"{o.get('units_with_data', '-')} / {o.get('record_count', '-')}"),
        ("Source", o.get("source", "-")),
    )]
    story.append(_table(rows, [W * 0.25, W * 0.75], header=False))
    if o.get("by_fuel_gj"):
        story.append(Spacer(1, 3 * mm))
        rows = [[_p("Fuel", cell), _p("GJ", cell), _p("toe", cell)]]
        for k, v in sorted(o["by_fuel_gj"].items(), key=lambda kv: -kv[1]):
            rows.append([_p(k, cell), _p(_n(v, 2), cell), _p(_n(v / GJ_PER_TOE, 2), cell)])
        story.append(_table(rows, [W * 0.4, W * 0.2, W * 0.2]))

    story.append(_p("4. Methodology and data basis", h2))
    for line in report["methodology"]:
        story.append(_p("• " + line, body))

    doc.build(story)
    return buf.getvalue()
