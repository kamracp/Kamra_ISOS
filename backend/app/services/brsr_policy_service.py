from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.models.brsr_policy_disclosure import BrsrPolicyDisclosure
from app.repositories.brsr_policy_disclosure_repository import (
    BrsrPolicyDisclosureRepository,
)
from app.repositories.brsr_organization_profile_repository import (
    BrsrOrganizationProfileRepository,
)
from app.schemas.brsr_policy_disclosure import (
    PRINCIPLE_LABELS,
    BrsrPolicyDisclosureUpdate,
)


def _has_text(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


class BrsrPolicyService:
    """Business logic for BRSR Section B - Management and Process Disclosures."""

    def __init__(self, db: Session, organization_id: int):
        self.db = db
        self.organization_id = organization_id
        self.repo = BrsrPolicyDisclosureRepository(db, organization_id)
        # Section B's three entity-level questions live on the profile row,
        # since they are asked once for the whole entity, not per principle.
        self.profile_repo = BrsrOrganizationProfileRepository(db, organization_id)

    def get_all(self) -> List[BrsrPolicyDisclosure]:
        return self.repo.get_all()

    def save(
        self, disclosures: List[BrsrPolicyDisclosureUpdate]
    ) -> List[BrsrPolicyDisclosure]:
        return self.repo.bulk_upsert(disclosures)

    def get_completeness(self) -> Dict[str, Any]:
        """
        Completion status across the nine NGRBC principles.

        Two different counts, deliberately:

        - answered: the core question (is there a policy?) has an explicit
          yes or no. This is what the progress bar shows.
        - complete: the follow-ups implied by that answer are filled too -
          board approval and a web link when there IS a policy, a stated
          reason when there is not.

        Counting only `answered` would let nine "no" answers reach 100%
        with nothing actually disclosed; counting only `complete` would
        make the bar sit at zero through most of a real filling session.
        Reporting both keeps the figure honest without being discouraging.
        """
        rows = {row.principle: row for row in self.repo.get_all()}

        principles: List[Dict[str, Any]] = []
        answered_count = 0
        complete_count = 0

        for number in range(1, 10):
            row = rows.get(number)
            answered = row is not None and row.has_policy is not None

            if not answered:
                complete = False
                missing = "Policy status not stated"
            elif row.has_policy:
                complete = (
                    row.policy_board_approved is not None
                    and _has_text(row.policy_web_link)
                )
                missing = (
                    "" if complete else "Board approval and policy web link needed"
                )
            else:
                complete = _has_text(row.reason_no_policy)
                missing = "" if complete else "Reason for not having a policy needed"

            if answered:
                answered_count += 1
            if complete:
                complete_count += 1

            principles.append(
                {
                    "principle": number,
                    "label": PRINCIPLE_LABELS[number],
                    "answered": answered,
                    "complete": complete,
                    "missing": missing,
                }
            )

        profile = self.profile_repo.get()
        entity_level = [
            {
                "key": "has_sustainability_committee",
                "label": "Board committee overseeing sustainability",
                "answered": profile is not None
                and profile.has_sustainability_committee is not None,
            },
            {
                "key": "policy_review_frequency",
                "label": "Frequency of policy review",
                "answered": profile is not None
                and _has_text(profile.policy_review_frequency),
            },
            {
                "key": "independent_assessment_agency",
                "label": "Independent assessment of policies",
                "answered": profile is not None
                and _has_text(profile.independent_assessment_agency),
            },
        ]

        total = 9
        return {
            "organization_id": self.organization_id,
            "entity_level": entity_level,
            "entity_level_answered": sum(1 for e in entity_level if e["answered"]),
            "total_principles": total,
            "answered_principles": answered_count,
            "complete_principles": complete_count,
            "completeness_percent": round((answered_count / total) * 100, 1),
            "principles": principles,
        }
