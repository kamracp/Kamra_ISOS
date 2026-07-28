"""
ESG Report API. GET /esg-reports/brsr-principle6?year=YYYY

Returns the BRSR Section C Principle 6 (Environment) structured report
for the current user's organization, built from existing platform data.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.services.esg_report_service import generate_brsr_principle6

router = APIRouter(prefix="/esg-reports", tags=["ESG Reports"])


@router.get("/brsr-principle6")
def brsr_principle6(
    year: int = 2024,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """BRSR Principle 6 (Environment) report for the caller's organization."""
    return generate_brsr_principle6(
        db=db,
        organization_id=current_user.organization_id,
        reporting_year=year,
    )
