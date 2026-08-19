from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.brsr_organization_profile import BrsrOrganizationProfile
from app.repositories.brsr_organization_profile_repository import (
    BrsrOrganizationProfileRepository,
)
from app.schemas.brsr_organization_profile import BrsrOrganizationProfileUpdate


# ---------------------------------------------------------------------------
# Question map for BRSR Section A - General Disclosures.
#
# Keyed by the SEBI question number so that completeness reporting matches
# what the filer sees in the actual BRSR form, not our column layout.
# One question may span several columns (e.g. Q12 BRSR contact person).
#
# Q24 (overview of the entity's material responsible business conduct issues)
# is NOT tracked here: it is narrative and belongs with Section B/C work.
# ---------------------------------------------------------------------------
SECTION_A_QUESTIONS: List[Dict[str, Any]] = [
    {"q": "Q1", "label": "Corporate Identity Number (CIN)", "fields": ["cin"]},
    {"q": "Q3", "label": "Year of incorporation", "fields": ["year_of_incorporation"]},
    {"q": "Q4", "label": "Registered office address", "fields": ["registered_office_address"]},
    {"q": "Q5", "label": "Corporate address", "fields": ["corporate_address"]},
    {"q": "Q6", "label": "E-mail", "fields": ["contact_email"]},
    {"q": "Q7", "label": "Telephone", "fields": ["contact_telephone"]},
    {"q": "Q8", "label": "Website", "fields": ["website"]},
    {"q": "Q9", "label": "Financial year reported", "fields": ["financial_year_reported"]},
    {"q": "Q10", "label": "Stock exchanges where listed", "fields": ["stock_exchanges_listed"]},
    {"q": "Q11", "label": "Paid-up capital", "fields": ["paid_up_capital_inr"]},
    {"q": "Q12", "label": "BRSR contact person",
     "fields": ["brsr_contact_name", "brsr_contact_phone", "brsr_contact_email"]},
    {"q": "Q13", "label": "Reporting boundary", "fields": ["reporting_boundary"]},
    {"q": "Q14", "label": "Business activities accounting for 90% of turnover",
     "fields": ["business_activities"]},
    {"q": "Q15", "label": "Products/services sold (90% of turnover)", "fields": ["products_sold"]},
    {"q": "Q16", "label": "Number of plants and offices", "fields": ["location_counts"]},
    {"q": "Q17", "label": "Markets served", "fields": ["markets_served"]},
    {"q": "Q18", "label": "Employees and workers (including differently abled)",
     "fields": ["employee_worker_counts", "differently_abled_counts"]},
    {"q": "Q19", "label": "Participation of women", "fields": ["women_participation"]},
    {"q": "Q20", "label": "Turnover rate for employees and workers", "fields": ["turnover_rates"]},
    {"q": "Q21", "label": "Holding, subsidiary and associate companies",
     "fields": ["group_companies"]},
    {"q": "Q22", "label": "CSR details",
     "fields": ["csr_applicable", "csr_turnover_inr", "csr_net_worth_inr"]},
    {"q": "Q23", "label": "Transparency and disclosures - grievance redressal",
     "fields": ["grievance_redressal"]},
    {"q": "Q25", "label": "Assurance provider", "fields": ["assurance_provider_name"]},
    {"q": "Q26", "label": "Type of assurance obtained", "fields": ["assurance_type"]},
]


def _is_filled(value: Any) -> bool:
    """
    A field counts as answered only if it carries real content.

    Empty string / empty list / empty dict are treated as NOT answered,
    because frontend forms routinely submit "" for untouched inputs and
    counting those as answered would make completeness lie.

    Zero and False ARE treated as answered: "differently abled workers: 0"
    is a deliberate disclosure, not a blank.
    """
    if value is None:
        return False
    if isinstance(value, str) and value.strip() == "":
        return False
    if isinstance(value, (list, dict)) and len(value) == 0:
        return False
    return True


class BrsrProfileService:
    """Business logic for BRSR Section A - General Disclosures."""

    def __init__(self, db: Session, organization_id: int):
        self.db = db
        self.organization_id = organization_id
        self.repo = BrsrOrganizationProfileRepository(db, organization_id)

    def get_profile(self) -> Optional[BrsrOrganizationProfile]:
        return self.repo.get()

    def save_profile(
        self, data: BrsrOrganizationProfileUpdate
    ) -> BrsrOrganizationProfile:
        """Upsert: Section A is filled progressively across many sessions."""
        return self.repo.upsert(data)

    def delete_profile(self) -> bool:
        """Returns False if there was no profile to delete."""
        existing = self.repo.get()
        if existing is None:
            return False
        self.repo.delete(existing)
        return True

    def get_completeness(self) -> Dict[str, Any]:
        """
        Report how much of Section A is answered, question by question.

        total_questions reflects only what this platform actually tracks
        (see SECTION_A_QUESTIONS) - it is not hardcoded to the full SEBI
        question count, so the platform never reports a misleading 100%.
        """
        profile = self.repo.get()

        questions: List[Dict[str, Any]] = []
        answered_count = 0

        for entry in SECTION_A_QUESTIONS:
            if profile is None:
                answered = False
            else:
                # A question counts as answered if ANY of its fields is filled,
                # mirroring the SEBI form where one question is one row.
                answered = any(
                    _is_filled(getattr(profile, field, None))
                    for field in entry["fields"]
                )
            if answered:
                answered_count += 1
            questions.append(
                {
                    "question": entry["q"],
                    "label": entry["label"],
                    "answered": answered,
                }
            )

        total = len(SECTION_A_QUESTIONS)
        percent = round((answered_count / total) * 100, 1) if total else 0.0

        return {
            "organization_id": self.organization_id,
            "profile_exists": profile is not None,
            "tracked_questions": total,
            "answered_questions": answered_count,
            "completeness_percent": percent,
            "questions": questions,
        }
