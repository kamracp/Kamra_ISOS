from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.brsr_organization_profile import (
    BrsrOrganizationProfileRead,
    BrsrOrganizationProfileUpdate,
)
from app.services.brsr_profile_service import BrsrProfileService

router = APIRouter(
    prefix="/brsr-profile",
    tags=["BRSR Section A - General Disclosures"],
)


def get_service(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BrsrProfileService:
    # Tenant-scoped: organization_id always comes from the JWT, never from
    # the client, so one org can never read or write another org's profile.
    return BrsrProfileService(db, organization_id=current_user.organization_id)


@router.get("/", response_model=BrsrOrganizationProfileRead | None)
def get_brsr_profile(service: BrsrProfileService = Depends(get_service)):
    """BRSR Section A profile for the current organization.

    Returns null rather than 404 when no profile exists yet: an unfilled
    Section A is the normal starting state, not an error.
    """
    return service.get_profile()


@router.put("/", response_model=BrsrOrganizationProfileRead)
def save_brsr_profile(
    data: BrsrOrganizationProfileUpdate,
    service: BrsrProfileService = Depends(get_service),
):
    """Create or update the profile. Only fields present in the body are applied."""
    return service.save_profile(data)


@router.get("/completeness")
def get_brsr_profile_completeness(
    service: BrsrProfileService = Depends(get_service),
):
    """Question-by-question completion status for Section A.

    tracked_questions reflects only what this platform actually stores,
    so the response never implies a misleading full-form 100%.
    """
    return service.get_completeness()


@router.delete("/", status_code=204)
def delete_brsr_profile(service: BrsrProfileService = Depends(get_service)):
    if not service.delete_profile():
        raise HTTPException(status_code=404, detail="BRSR profile not found")
