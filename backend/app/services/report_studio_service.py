"""
Report Studio - assembles ONE complete report tree for an organization and
reporting year by composing the existing services. No calculation happens
here: every number comes from the service that owns it, so the report can
never disagree with the pages it summarises (one truth).

Each section is wrapped so that one failing module degrades to
{"status": "error"} instead of taking the whole report down.
"""
from datetime import datetime, timezone
from typing import Any, Callable, Dict

from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.repositories.climate_risk_repository import ClimateRiskRepository
from app.repositories.net_zero_target_repository import NetZeroTargetRepository
from app.schemas.report_narrative import SDG_LABELS
from app.services import esg_report_service as esg
from app.services.brsr_policy_service import BrsrPolicyService
from app.services.brsr_profile_service import BrsrProfileService
from app.services.climate_risk_service import ClimateRiskService
from app.services.energy_service import org_year_energy
from app.services.net_zero_service import get_net_zero_summary
from app.services.report_narrative_service import ReportNarrativeService
from app.services.water_waste_service import WaterWasteService

PRINCIPLE_GENERATORS = {
    1: esg.generate_brsr_principle1, 2: esg.generate_brsr_principle2,
    3: esg.generate_brsr_principle3, 4: esg.generate_brsr_principle4,
    5: esg.generate_brsr_principle5, 6: esg.generate_brsr_principle6,
    7: esg.generate_brsr_principle7, 8: esg.generate_brsr_principle8,
    9: esg.generate_brsr_principle9,
}


def _row_to_dict(row) -> Dict[str, Any] | None:
    if row is None:
        return None
    return {c.name: getattr(row, c.name) for c in row.__table__.columns}


def _section(fn: Callable[[], Any]) -> Dict[str, Any]:
    try:
        return {"status": "ok", "data": fn()}
    except Exception as exc:  # one broken module must not kill the report
        return {"status": "error", "detail": f"{type(exc).__name__}: {exc}"}


def generate_complete_report(db: Session, organization_id: int, year: int) -> dict:
    org = db.query(Organization).filter(Organization.id == organization_id).first()
    narrative_row = ReportNarrativeService(db, organization_id).get(year)
    narrative = _row_to_dict(narrative_row) or {}
    by_principle = {
        p["principle"]: p for p in (narrative.get("principle_narratives") or [])
    }

    profile_svc = BrsrProfileService(db, organization_id)
    policy_svc = BrsrPolicyService(db, organization_id)

    def _ghg():
        scope1_t, scope2_t, src, s1_std, s2_std = esg._get_scope_summary(
            db, organization_id, year
        )
        return {
            "scope1_tco2e": scope1_t, "scope2_tco2e": scope2_t,
            "total_tco2e": round((scope1_t or 0) + (scope2_t or 0), 3),
            "source": src, "scope1_standards": s1_std, "scope2_standards": s2_std,
        }

    def _net_zero():
        targets = NetZeroTargetRepository(db, organization_id).get_all()
        return [get_net_zero_summary(db, organization_id, t.id) for t in targets]

    def _principles():
        out = {}
        for n, gen in PRINCIPLE_GENERATORS.items():
            nar = by_principle.get(n, {})
            out[n] = {
                **_section(lambda: gen(db, organization_id, year)),
                "narrative": {
                    "highlight": nar.get("highlight"),
                    "intro": nar.get("intro"),
                    "sdgs": [{"number": s, "label": SDG_LABELS.get(s)}
                             for s in nar.get("sdgs", [])],
                },
            }
        return out

    return {
        "meta": {
            "reporting_year": year,
            "organization_id": organization_id,
            "organization_name": getattr(org, "organization_name", None),
            "legal_name": getattr(org, "legal_name", None),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "theme_colour": narrative.get("theme_colour"),
        },
        "narratives": {
            "status": "ok" if narrative_row else "not_written",
            "data": narrative,
            "completeness": ReportNarrativeService(db, organization_id).get_completeness(year),
        },
        "section_a": {
            **_section(lambda: _row_to_dict(profile_svc.get_profile())),
            "completeness": _section(profile_svc.get_completeness),
        },
        "section_b": {
            **_section(lambda: [_row_to_dict(r) for r in policy_svc.get_all()]),
            "completeness": _section(policy_svc.get_completeness),
        },
        "principles": _principles(),
        "energy_balance": _section(lambda: org_year_energy(db, organization_id, year)),
        "ghg": _section(_ghg),
        "water_waste": _section(lambda: WaterWasteService(db, organization_id).get_summary(year)),
        "net_zero": _section(_net_zero),
        "climate_risk": _section(
            lambda: ClimateRiskService(ClimateRiskRepository(db, organization_id)).get_summary()
        ),
        # No materiality module exists yet; say so rather than fabricate.
        "materiality": {"status": "not_tracked",
                        "detail": "Double-materiality assessment not yet implemented"},
    }
