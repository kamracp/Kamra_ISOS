from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.services.brsr_filing_validator import BrsrFilingValidator

router = APIRouter(
    prefix="/brsr-filing",
    tags=["BRSR Filing Readiness"],
)


def get_validator(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BrsrFilingValidator:
    # Tenant-scoped: organization_id always from the JWT.
    return BrsrFilingValidator(db, organization_id=current_user.organization_id)


@router.get("/validate")
def validate_filing(
    year: int = 2025,
    validator: BrsrFilingValidator = Depends(get_validator),
):
    """
    Pre-filing check across Sections A, B and C.

    `ready_to_file` is true only when there are no blocking errors. Warnings
    can be a deliberate disclosure choice; errors are things the exchange
    will reject or an assurance provider will challenge.

    Query param is `year`, matching the ESG report endpoints.
    """
    return validator.validate(year)
