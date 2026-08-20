from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.brsr_policy_disclosure import (
    PRINCIPLE_LABELS,
    BrsrPolicyBulkUpdate,
    BrsrPolicyDisclosureRead,
)
from app.services.brsr_policy_service import BrsrPolicyService

router = APIRouter(
    prefix="/brsr-policy",
    tags=["BRSR Section B - Management and Process Disclosures"],
)


def get_service(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BrsrPolicyService:
    # Tenant-scoped: organization_id always from the JWT, never the client.
    return BrsrPolicyService(db, organization_id=current_user.organization_id)


@router.get("/", response_model=list[BrsrPolicyDisclosureRead])
def get_policy_disclosures(service: BrsrPolicyService = Depends(get_service)):
    """All saved principle disclosures. Empty list when nothing is filled yet."""
    return service.get_all()


@router.put("/", response_model=list[BrsrPolicyDisclosureRead])
def save_policy_disclosures(
    data: BrsrPolicyBulkUpdate,
    service: BrsrPolicyService = Depends(get_service),
):
    """Upsert one or more principles in a single transaction."""
    return service.save(data.disclosures)


@router.get("/completeness")
def get_policy_completeness(service: BrsrPolicyService = Depends(get_service)):
    """Per-principle status, with what is still missing for each."""
    return service.get_completeness()


@router.get("/principles")
def list_principles():
    """
    The nine NGRBC principles with their SEBI wording.

    Kept behind the same router so the frontend reads the labels from one
    place instead of hard-coding a second copy.
    """
    return [
        {"principle": number, "label": label}
        for number, label in sorted(PRINCIPLE_LABELS.items())
    ]
