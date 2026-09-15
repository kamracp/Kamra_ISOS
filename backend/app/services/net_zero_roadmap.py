"""Net Zero Roadmap — one organization, all its net-zero targets.

Per target: base-year inventory cross-check (from the shared ESG aggregator),
linear trajectory baseline -> target year with the current-year actual,
project pipeline in MACC order, and the gap between the reduction the
target requires and the abatement the pipeline commits to. Residual
emissions and neutralisation (removals) are not modelled on the platform
and are stated as such. Climate-risk (TCFD) exposure is appended when
risks exist. Numbers come from net_zero_service / climate_risk_service,
never recomputed here.
"""

import io
from datetime import datetime, timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer
from sqlalchemy.orm import Session

from app.models.net_zero_target import NetZeroTarget
from app.repositories.climate_risk_repository import ClimateRiskRepository
from app.services.climate_risk_service import ClimateRiskService
from app.services.lca_product_pdf import _n, _table
from app.services.net_zero_service import get_net_zero_summary


def _enum(v):
    return getattr(v, "value", v)


# Project statuses that do not contribute committed abatement.
_INACTIVE = ("cancel", "reject", "shelv", "abandon")


def _trajectory(s: dict) -> list[dict]:
    """Year-by-year linear path from baseline to target; actual only in current year."""
    b, t = s["baseline_year"], s["target_year"]
    b_t, t_t = s["baseline_co2e_tonnes"], s["target_co2e_tonnes"]
    n = max(t - b, 1)
    rows = []
    for y in range(b, t + 1):
        expected = round(b_t - (b_t - t_t) * (y - b) / n, 3)
        rows.append({
            "year": y,
            "expected_co2e_tonnes": expected,
            "actual_co2e_tonnes": s["current_actual_co2e_tonnes"] if y == s["current_year"] else None,
        })
    return rows


def build_net_zero_roadmap(db: Session, organization_id: int) -> dict:
    from app.services.esg_report_service import _get_scope_summary

    targets = (db.query(NetZeroTarget).filter(NetZeroTarget.organization_id == organization_id)
               .order_by(NetZeroTarget.target_year, NetZeroTarget.id).all())
    out = []
    for tgt in targets:
        s = get_net_zero_summary(db, organization_id, tgt.id)
        if s.get("status") != "ok":
            continue
        # Independent cross-check of the entered baseline against the inventory engine.
        # Cross-check only makes sense for an organization-wide target; a
        # unit-level baseline is not comparable with the org inventory.
        if s["manufacturing_unit_id"] is None:
            inv_s1, inv_s2, _src, _a, _b = _get_scope_summary(db, organization_id, s["baseline_year"])
            inventory_baseline = round(inv_s1 + inv_s2, 3)
        else:
            inventory_baseline = None
        macc = s["macc"]
        active = [p for p in macc if not any(k in str(_enum(p["status"])).lower() for k in _INACTIVE)]
        committed = round(sum(p["annual_co2e_abated_tonnes"] for p in active), 3)
        required = round(s["baseline_co2e_tonnes"] - s["target_co2e_tonnes"], 3)
        coverage_pct = round(committed / required * 100, 1) if required > 0 else None
        out.append({
            **{k: v for k, v in s.items() if k != "macc"},
            "inventory_baseline_scope1_2_tonnes": inventory_baseline,
            "baseline_matches_inventory": (abs(inventory_baseline - s["baseline_co2e_tonnes"]) < 0.5)
            if inventory_baseline is not None else None,
            "required_reduction_tonnes": required,
            "committed_abatement_tonnes": committed,
            "abatement_coverage_percent": coverage_pct,
            "uncovered_tonnes": round(max(required - committed, 0.0), 3),
            "trajectory": _trajectory(s),
            "projects": [{**p, "category": _enum(p["category"]), "status": _enum(p["status"])} for p in macc],
        })

    risk = ClimateRiskService(ClimateRiskRepository(db, organization_id=organization_id)).get_summary()

    return {
        "framework": "Net Zero Roadmap",
        "section": "Targets, trajectory, abatement pipeline and gap",
        "organization_id": organization_id,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "targets": out,
        "climate_risk": risk,
        "methodology": [
            "Trajectory is linear from the baseline-year emissions to the target-year emissions "
            "(baseline x (1 - reduction %)). For an organization-wide target the current-year actual is Scope 1+2 "
            "from the shared platform inventory (utility bills + manufacturing records, current calendar year); "
            "for a unit-level target it is limited to utility bills of the unit's linked building.",
            "Marginal abatement cost (MAC) = (capex / lifespan + annual opex delta) / annual tCO2e abated; "
            "projects are ordered cheapest first. Projects whose MAC cannot be computed are listed last, not dropped.",
            "Committed abatement sums annual abatement of all non-cancelled projects; coverage = committed / required reduction. "
            "Overlaps between projects are not netted.",
            "Residual emissions at the target year and their neutralisation through removals are not modelled on the platform; "
            "a net-zero claim per ISO 14068-1 / SBTi Net-Zero Standard requires them to be addressed separately.",
        ],
    }


# ----------------------------------------------------------------------- PDF

def _p(text, style):
    return Paragraph("" if text is None else str(text), style)


def generate_net_zero_roadmap_pdf(report: dict, org_name: str | None = None) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=15 * mm, rightMargin=15 * mm, topMargin=15 * mm, bottomMargin=15 * mm)
    ss = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=ss["Title"], fontSize=16, spaceAfter=2)
    h2 = ParagraphStyle("h2", parent=ss["Heading2"], fontSize=12, spaceBefore=10, spaceAfter=4)
    h3 = ParagraphStyle("h3", parent=ss["Heading3"], fontSize=10, spaceBefore=6, spaceAfter=3)
    meta = ParagraphStyle("meta", parent=ss["Normal"], fontSize=8, textColor=colors.grey)
    body = ParagraphStyle("body", parent=ss["Normal"], fontSize=8.5)
    cell = ParagraphStyle("cell", parent=ss["Normal"], fontSize=7.5, leading=9)
    W = doc.width

    story = [
        _p(org_name or "Kamra ClimateOS", h1),
        _p(f"{report['framework']} — {report['section']}", body),
        _p(f"Organization ID: {report['organization_id']} | Generated: {report['generated_at']}", meta),
        Spacer(1, 4 * mm),
    ]

    if not report["targets"]:
        story.append(_p("No net-zero target has been set for this organization. Add one under Net Zero → Targets & Projects.", body))

    for i, t in enumerate(report["targets"], 1):
        story.append(_p(f"{i}. Target: {t['target_name']}", h2))
        scope = "organization-wide" if t["manufacturing_unit_id"] is None else f"manufacturing unit {t['manufacturing_unit_id']}"
        match = t["baseline_matches_inventory"]
        match_txt = ("unit-level target, org inventory not comparable" if t["manufacturing_unit_id"] is not None
                     else "-" if match is None else ("matches inventory" if match else "differs from inventory"))
        rows = [[_p(k, cell), _p(v, cell)] for k, v in (
            ("Coverage", scope),
            ("Baseline year / emissions", f"{t['baseline_year']}: {_n(t['baseline_co2e_tonnes'], 2)} tCO2e "
             f"(inventory Scope 1+2 that year: {_n(t['inventory_baseline_scope1_2_tonnes'], 2)} tCO2e — {match_txt})"),
            ("Target year / emissions", f"{t['target_year']}: {_n(t['target_co2e_tonnes'], 2)} tCO2e ({_n(t['reduction_percentage'], 1)} % reduction)"),
            ("Current year actual", f"{t['current_year']}: {_n(t['current_actual_co2e_tonnes'], 2)} tCO2e "
             f"(trajectory expects {_n(t['expected_co2e_tonnes_on_trajectory'], 2)}; gap {_n(t['gap_tonnes'], 2)} — "
             f"{'on track' if t['on_track'] else 'behind trajectory'})"),
            ("Required reduction", f"{_n(t['required_reduction_tonnes'], 2)} tCO2e/yr by {t['target_year']}"),
            ("Committed abatement", f"{_n(t['committed_abatement_tonnes'], 2)} tCO2e/yr from non-cancelled projects "
             f"= {_n(t['abatement_coverage_percent'], 1)} % of required; uncovered {_n(t['uncovered_tonnes'], 2)} tCO2e/yr"),
        )]
        story.append(_table(rows, [W * 0.28, W * 0.72], header=False))

        story.append(_p("Trajectory (linear path)", h3))
        rows = [[_p("Year", cell), _p("Expected tCO2e", cell), _p("Actual tCO2e", cell)]]
        for r in t["trajectory"]:
            rows.append([_p(r["year"], cell), _p(_n(r["expected_co2e_tonnes"], 2), cell), _p(_n(r["actual_co2e_tonnes"], 2), cell)])
        story.append(_table(rows, [W * 0.2, W * 0.3, W * 0.3]))

        story.append(_p("Abatement pipeline (MACC order, cheapest first)", h3))
        if t["projects"]:
            rows = [[_p(h, cell) for h in ("Project", "Category", "Status", "tCO2e/yr", "Capex", "Opex Δ/yr", "Life (yr)", "MAC (cost/tCO2e)")]]
            for p in t["projects"]:
                rows.append([_p(p["project_name"], cell), _p(p["category"], cell), _p(p["status"], cell),
                             _p(_n(p["annual_co2e_abated_tonnes"], 2), cell), _p(_n(p["capex"], 0), cell),
                             _p(_n(p["annual_opex_delta"], 0), cell), _p(p["lifespan_years"], cell),
                             _p(_n(p["marginal_abatement_cost"], 2), cell)])
            story.append(_table(rows, [W * f for f in (0.24, 0.12, 0.11, 0.10, 0.12, 0.11, 0.08, 0.12)]))
        else:
            story.append(_p("No decarbonization projects recorded for this target's coverage.", body))
        if i < len(report["targets"]):
            story.append(PageBreak())

    cr = report["climate_risk"]
    if cr.get("total_risks"):
        story.append(_p("Climate risk exposure (TCFD)", h2))
        rows = [[_p(k, cell), _p(v, cell)] for k, v in (
            ("Risks recorded", cr["total_risks"]),
            ("Estimated financial impact", f"INR {_n(cr['total_estimated_financial_impact_inr'], 0)}"),
            ("Mitigation cost / benefit", f"INR {_n(cr['total_mitigation_cost_inr'], 0)} / INR {_n(cr['total_mitigation_benefit_inr'], 0)}"),
            ("Net exposure", f"INR {_n(cr['total_net_risk_exposure_inr'], 0)}"),
        )]
        for k, v in (cr.get("net_risk_exposure_by_category_inr") or {}).items():
            rows.append([_p(f"Net exposure — {k}", cell), _p(f"INR {_n(v, 0)}", cell)])
        story.append(_table(rows, [W * 0.35, W * 0.65], header=False))

    story.append(_p("Methodology and limitations", h2))
    for line in report["methodology"]:
        story.append(_p("• " + line, body))

    doc.build(story)
    return buf.getvalue()
