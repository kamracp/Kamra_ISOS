from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.report_narrative import (
    SDG_LABELS,
    ReportNarrativeResponse,
    ReportNarrativeUpdate,
)
from app.services.report_narrative_service import ReportNarrativeService

router = APIRouter(
    prefix="/report-narratives",
    tags=["Report Studio - Narratives"],
)

# `year` is REQUIRED everywhere here. A defaulted year would silently
# return another year's (empty) narrative and look like a broken feature.
YearParam = Query(..., ge=2000, le=2100, description="Reporting year")


def get_service(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReportNarrativeService:
    # Tenant-scoped: organization_id always from the JWT.
    return ReportNarrativeService(db, organization_id=current_user.organization_id)


@router.get("/sdgs")
def list_sdgs(_: User = Depends(get_current_user)):
    return [{"number": n, "label": label} for n, label in SDG_LABELS.items()]


@router.get("/years", response_model=list[int])
def list_years(service: ReportNarrativeService = Depends(get_service)):
    return service.list_years()


@router.get("/completeness")
def get_completeness(
    year: int = YearParam,
    service: ReportNarrativeService = Depends(get_service),
):
    return service.get_completeness(year)


@router.get("/", response_model=Optional[ReportNarrativeResponse])
def get_narrative(
    year: int = YearParam,
    service: ReportNarrativeService = Depends(get_service),
):
    # null, not 404: an unwritten narrative is the normal starting state.
    return service.get(year)


@router.put("/", response_model=ReportNarrativeResponse)
def upsert_narrative(
    payload: ReportNarrativeUpdate,
    year: int = YearParam,
    service: ReportNarrativeService = Depends(get_service),
):
    return service.upsert(year, payload)


@router.delete("/", status_code=204)
def delete_narrative(
    year: int = YearParam,
    service: ReportNarrativeService = Depends(get_service),
):
    if not service.delete(year):
        raise HTTPException(status_code=404, detail="No narrative for that year")
    return Response(status_code=204)
