"""
PAT Cycle Target endpoints (Manufacturing / Energy module). Prefix
/pat-energy. Actual energy/production data lives in the existing
/production-records + utility-bills stack; this module only manages
BEE-notified targets and the PAT-aware summary on top of them.
organization_id always from JWT.
"""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.api.deps import get_current_user
from app.services.pat_sec_service import PatSecService
from app.schemas.pat_cycle_target import (
    PatCycleTargetCreate,
    PatCycleTargetUpdate,
    PatCycleTargetResponse,
)

router = APIRouter(prefix="/pat-energy", tags=["pat-energy"])


def get_service(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> PatSecService:
    return PatSecService(db, current_user.organization_id)


@router.post("/targets/{manufacturing_unit_id}", response_model=PatCycleTargetResponse, status_code=201)
def create_target(
    manufacturing_unit_id: int,
    payload: PatCycleTargetCreate,
    service: PatSecService = Depends(get_service),
):
    data = payload.model_dump()
    return service.create_target(manufacturing_unit_id, data)


@router.get("/targets/{manufacturing_unit_id}", response_model=list[PatCycleTargetResponse])
def list_targets(manufacturing_unit_id: int, service: PatSecService = Depends(get_service)):
    return service.list_targets(manufacturing_unit_id)


@router.put("/targets/{target_id}", response_model=PatCycleTargetResponse)
def update_target(
    target_id: int,
    payload: PatCycleTargetUpdate,
    service: PatSecService = Depends(get_service),
):
    data = payload.model_dump(exclude_unset=True)
    result = service.update_target(target_id, data)
    if result is None:
        raise HTTPException(status_code=404, detail="PAT cycle target not found")
    return result


@router.delete("/targets/{target_id}", status_code=204)
def delete_target(target_id: int, service: PatSecService = Depends(get_service)):
    if not service.delete_target(target_id):
        raise HTTPException(status_code=404, detail="PAT cycle target not found")


@router.get("/pat-summary/{manufacturing_unit_id}")
def get_pat_summary(
    manufacturing_unit_id: int,
    year: int,
    service: PatSecService = Depends(get_service),
):
    return service.get_pat_summary(manufacturing_unit_id, year)
