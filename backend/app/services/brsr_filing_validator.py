"""
Pre-filing validation for BRSR.

Checks the platform's own data against the mistakes the exchanges have
publicly said listed companies keep making in their BRSR submissions -
NIC turnover percentages that do not add up, energy reported in the wrong
unit, mandatory narratives left blank.

This is deliberately NOT an XBRL generator. The BRSR taxonomy is not in
BSE's public taxonomy release (that covers shareholding pattern, financial
results, corporate governance, voting results and share capital audit) -
only the Excel utility exists, behind a Listing Centre login. Generating
an instance document against a schema we cannot see would risk a rejected
filing on a hard deadline. Catching the errors before the filer opens the
utility is the part we can do correctly.
"""

from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.repositories.brsr_organization_profile_repository import (
    BrsrOrganizationProfileRepository,
)
from app.services.brsr_policy_service import BrsrPolicyService
from app.services.water_waste_service import WaterWasteService

SEVERITY_ERROR = "error"      # the exchange will reject this
SEVERITY_WARNING = "warning"  # accepted, but the disclosure is incomplete
SEVERITY_INFO = "info"        # worth a look, not blocking


def _finding(severity: str, where: str, message: str) -> Dict[str, str]:
    """`where` names the SEBI section and question, so the filer can go
    straight to it rather than hunting through the form."""
    return {"severity": severity, "where": where, "message": message}


def _pct_total(rows: Optional[List[Dict[str, Any]]], key: str) -> Optional[Decimal]:
    if not rows:
        return None
    values = [r.get(key) for r in rows if isinstance(r, dict)]
    present = [Decimal(str(v)) for v in values if v is not None]
    if not present:
        return None
    return sum(present, Decimal("0"))


class BrsrFilingValidator:
    """Runs every pre-filing check for one organization and reporting year."""

    def __init__(self, db: Session, organization_id: int):
        self.db = db
        self.organization_id = organization_id
        self.profile_repo = BrsrOrganizationProfileRepository(db, organization_id)
        self.policy_service = BrsrPolicyService(db, organization_id)

    def validate(self, year: int) -> Dict[str, Any]:
        findings: List[Dict[str, str]] = []
        profile = self.profile_repo.get()

        if profile is None:
            findings.append(
                _finding(
                    SEVERITY_ERROR,
                    "Section A",
                    "No Section A profile exists. General disclosures are "
                    "mandatory for every filer.",
                )
            )
        else:
            findings.extend(self._check_section_a(profile))

        findings.extend(self._check_section_b())
        findings.extend(self._check_p6(year))

        counts = {
            SEVERITY_ERROR: sum(1 for f in findings if f["severity"] == SEVERITY_ERROR),
            SEVERITY_WARNING: sum(1 for f in findings if f["severity"] == SEVERITY_WARNING),
            SEVERITY_INFO: sum(1 for f in findings if f["severity"] == SEVERITY_INFO),
        }

        return {
            "organization_id": self.organization_id,
            "reporting_year": year,
            # ready_to_file means no blocking errors - warnings can be a
            # deliberate choice, errors cannot.
            "ready_to_file": counts[SEVERITY_ERROR] == 0,
            "counts": counts,
            "findings": findings,
        }

    # --- Section A ---

    def _check_section_a(self, profile) -> List[Dict[str, str]]:
        findings: List[Dict[str, str]] = []

        if not profile.cin:
            findings.append(
                _finding(SEVERITY_ERROR, "Section A, Q1", "CIN is not filled.")
            )
        if not profile.financial_year_reported:
            findings.append(
                _finding(
                    SEVERITY_ERROR,
                    "Section A, Q9",
                    "Financial year reported is not filled.",
                )
            )
        if not profile.reporting_boundary:
            findings.append(
                _finding(
                    SEVERITY_ERROR,
                    "Section A, Q13",
                    "Reporting boundary (standalone or consolidated) is not stated.",
                )
            )

        # The exchanges specifically flag NIC turnover percentages that do
        # not add up. Over 100 is arithmetically impossible; under 90 fails
        # SEBI's own instruction that these cover 90% of turnover.
        for label, rows, key in (
            ("Section A, Q14", profile.business_activities, "turnover_percent"),
            ("Section A, Q15", profile.products_sold, "turnover_percent"),
        ):
            total = _pct_total(rows, key)
            if total is None:
                findings.append(
                    _finding(
                        SEVERITY_WARNING,
                        label,
                        "No turnover percentages entered; the exchange expects "
                        "activities covering 90% of turnover.",
                    )
                )
                continue
            if total > 100:
                findings.append(
                    _finding(
                        SEVERITY_ERROR,
                        label,
                        f"Turnover percentages total {total}%, which exceeds 100%.",
                    )
                )
            elif total < 90:
                findings.append(
                    _finding(
                        SEVERITY_WARNING,
                        label,
                        f"Turnover percentages total {total}%. SEBI asks for "
                        "activities covering at least 90% of turnover.",
                    )
                )

        if not profile.employee_worker_counts:
            findings.append(
                _finding(
                    SEVERITY_WARNING,
                    "Section A, Q18",
                    "Employee and worker counts are not filled.",
                )
            )

        return findings

    # --- Section B ---

    def _check_section_b(self) -> List[Dict[str, str]]:
        findings: List[Dict[str, str]] = []
        completeness = self.policy_service.get_completeness()

        for principle in completeness["principles"]:
            number = principle["principle"]
            if not principle["answered"]:
                findings.append(
                    _finding(
                        SEVERITY_ERROR,
                        f"Section B, Principle {number}",
                        "Policy status not stated. Every principle needs an "
                        "explicit yes or no.",
                    )
                )
            elif not principle["complete"]:
                findings.append(
                    _finding(
                        SEVERITY_WARNING,
                        f"Section B, Principle {number}",
                        principle["missing"],
                    )
                )

        for entry in completeness["entity_level"]:
            if not entry["answered"]:
                findings.append(
                    _finding(
                        SEVERITY_WARNING,
                        "Section B, entity-level",
                        f"{entry['label']} is not stated.",
                    )
                )

        return findings

    # --- Section C, Principle 6 ---

    def _check_p6(self, year: int) -> List[Dict[str, str]]:
        findings: List[Dict[str, str]] = []
        summary = WaterWasteService(self.db, self.organization_id).get_summary(year)
        water = summary["water"]
        waste = summary["waste"]

        if water["record_count"] == 0:
            findings.append(
                _finding(
                    SEVERITY_WARNING,
                    "Section C, P6 Q3",
                    f"No water records for {year}. Water withdrawal and "
                    "discharge are BRSR Core KPIs under assurance.",
                )
            )
        else:
            consumption = water["total_consumption_kl"]
            # Negative consumption means discharge exceeds withdrawal, which
            # is physically impossible - the figures disagree with each other
            # and an assurance provider will find it.
            if consumption is not None and consumption < 0:
                findings.append(
                    _finding(
                        SEVERITY_ERROR,
                        "Section C, P6 Q3",
                        f"Water consumption computes to {consumption} kL. "
                        "Discharge exceeds withdrawal, so the figures are "
                        "inconsistent.",
                    )
                )

        if waste["record_count"] == 0:
            findings.append(
                _finding(
                    SEVERITY_WARNING,
                    "Section C, P6 Q9",
                    f"No waste records for {year}. Waste generated and waste "
                    "diverted from disposal are BRSR Core KPIs under assurance.",
                )
            )
        else:
            generated = waste["total_generated_mt"]
            recovered = waste["total_recovered_mt"] or Decimal("0")
            disposed = waste["total_disposed_mt"] or Decimal("0")
            if generated is not None and (recovered + disposed) > generated:
                findings.append(
                    _finding(
                        SEVERITY_ERROR,
                        "Section C, P6 Q9",
                        f"Waste recovered plus disposed ({recovered + disposed} MT) "
                        f"exceeds waste generated ({generated} MT).",
                    )
                )

        return findings
