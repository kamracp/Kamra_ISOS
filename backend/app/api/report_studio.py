from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.services.report_studio_service import generate_complete_report

router = APIRouter(prefix="/report-studio", tags=["Report Studio"])


@router.get("/complete")
def complete_report(
    year: int = Query(..., ge=2000, le=2100, description="Reporting year"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """The full report tree for one year - Section A/B, nine principles,
    energy balance, GHG, water/waste, net zero, climate risk, narratives.
    This JSON is what the PDF renderer will consume."""
    return generate_complete_report(db, current_user.organization_id, year)
