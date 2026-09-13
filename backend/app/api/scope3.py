"""
Scope 3 API (GHG Protocol categories 1-15).

  GET    /scope3/summary?year=            all 15 categories: derived (3, 5), entered (4), not_tracked
  GET    /scope3/records/?year=&category= entered activity records with computed tCO2e
  POST   /scope3/records/
  GET    /scope3/records/{id}
  PUT    /scope3/records/{id}
  DELETE /scope3/records/{id}
`year` is always explicit -- never defaulted (platform rule).
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.scope3 import Scope3RecordCreate, Scope3RecordResponse, Scope3RecordUpdate, Scope3SummaryOut
from app.services.scope3_service import Scope3Service

router = APIRouter(prefix="/scope3", tags=["Scope 3"])


def get_service(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Scope3Service:
    return Scope3Service(db, organization_id=current_user.organization_id)


def _404(rid: int):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Scope 3 record {rid} not found")


@router.get("/summary", response_model=Scope3SummaryOut)
def summary(year: int = Query(...), svc: Scope3Service = Depends(get_service)):
    return svc.summary(year)


@router.get("/records/", response_model=list[Scope3RecordResponse])
def list_records(year: int | None = Query(default=None), category: int | None = Query(default=None, ge=1, le=15),
                 svc: Scope3Service = Depends(get_service)):
    return svc.list_records(year, category)


@router.post("/records/", response_model=Scope3RecordResponse, status_code=status.HTTP_201_CREATED)
def create_record(data: Scope3RecordCreate, svc: Scope3Service = Depends(get_service)):
    return svc.create_record(data)


@router.get("/records/{rid}", response_model=Scope3RecordResponse)
def get_record(rid: int, svc: Scope3Service = Depends(get_service)):
    r = svc.get_record(rid)
    if r is None:
        _404(rid)
    return r


@router.put("/records/{rid}", response_model=Scope3RecordResponse)
def update_record(rid: int, data: Scope3RecordUpdate, svc: Scope3Service = Depends(get_service)):
    r = svc.update_record(rid, data)
    if r is None:
        _404(rid)
    return r


@router.delete("/records/{rid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_record(rid: int, svc: Scope3Service = Depends(get_service)):
    if not svc.delete_record(rid):
        _404(rid)
