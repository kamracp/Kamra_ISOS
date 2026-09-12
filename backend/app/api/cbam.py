"""
CBAM API (definitive period, 2026+).

  GET    /cbam/goods/            list goods with computed SEE (optional ?year=)
  POST   /cbam/goods/            create
  GET    /cbam/goods/{id}        one good with SEE, excluded items, factor sources
  PUT    /cbam/goods/{id}        update (recomputed SEE returned)
  DELETE /cbam/goods/{id}

Operator template export (Commission XLSX) comes in session 2.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.cbam_good import CbamGoodCreate, CbamGoodUpdate, CbamGoodResponse
from app.services.cbam_service import CbamService

router = APIRouter(prefix="/cbam", tags=["CBAM"])


def get_service(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> CbamService:
    return CbamService(db, organization_id=current_user.organization_id)


def _404(good_id: int):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"CBAM good {good_id} not found")


@router.get("/goods/", response_model=list[CbamGoodResponse])
def list_goods(year: int | None = Query(default=None), svc: CbamService = Depends(get_service)):
    return svc.list_goods(year)


@router.post("/goods/", response_model=CbamGoodResponse, status_code=status.HTTP_201_CREATED)
def create_good(data: CbamGoodCreate, svc: CbamService = Depends(get_service)):
    return svc.create_good(data)


@router.get("/goods/{good_id}", response_model=CbamGoodResponse)
def get_good(good_id: int, svc: CbamService = Depends(get_service)):
    good = svc.get_good(good_id)
    if good is None:
        _404(good_id)
    return good


@router.put("/goods/{good_id}", response_model=CbamGoodResponse)
def update_good(good_id: int, data: CbamGoodUpdate, svc: CbamService = Depends(get_service)):
    good = svc.update_good(good_id, data)
    if good is None:
        _404(good_id)
    return good


@router.delete("/goods/{good_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_good(good_id: int, svc: CbamService = Depends(get_service)):
    if not svc.delete_good(good_id):
        _404(good_id)
