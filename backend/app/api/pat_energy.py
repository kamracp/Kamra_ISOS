"""
PAT Cycle Target + Energy/Production Record endpoints (Manufacturing /
Energy module). Prefix /pat-energy. organization_id always from JWT.
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
from app.schemas.energy_production_record import (
    EnergyProductionRecordCreate,
    EnergyProductionRecordUpdate,
    EnergyProductionRecordResponse,
)

router = APIRouter(prefix="/pat-energy", tags=["pat-energy"])


def get_service(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> PatSecService:
    return PatSecService(db, current_user.organization_id)


# ---- PAT Cycle Targets ----

@router.post("/targets/{manufacturing_unit_id}", response_model=PatCycleTargetResponse, status_code=201)
def create_target(
    manufacturing_unit_id: int,
    payload: PatCycleTargetCreate,
    service: PatSecService = Depends(get_service),
):
    data = payload.model_dump(exclude={"manufacturing_unit_id"})
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


# ---- Energy/Production Records ----

@router.post("/records/{manufacturing_unit_id}", response_model=EnergyProductionRecordResponse, status_code=201)
def create_record(
    manufacturing_unit_id: int,
    payload: EnergyProductionRecordCreate,
    service: PatSecService = Depends(get_service),
):
    data = payload.model_dump(exclude={"manufacturing_unit_id"})
    return service.create_record(manufacturing_unit_id, data)


@router.get("/records/{manufacturing_unit_id}", response_model=list[EnergyProductionRecordResponse])
def list_records(
    manufacturing_unit_id: int,
    year: int | None = None,
    service: PatSecService = Depends(get_service),
):
    return service.list_records(manufacturing_unit_id, year)


@router.put("/records/{record_id}", response_model=EnergyProductionRecordResponse)
def update_record(
    record_id: int,
    payload: EnergyProductionRecordUpdate,
    service: PatSecService = Depends(get_service),
):
    data = payload.model_dump(exclude_unset=True)
    result = service.update_record(record_id, data)
    if result is None:
        raise HTTPException(status_code=404, detail="Energy/production record not found")
    return result


@router.delete("/records/{record_id}", status_code=204)
def delete_record(record_id: int, service: PatSecService = Depends(get_service)):
    if not service.delete_record(record_id):
        raise HTTPException(status_code=404, detail="Energy/production record not found")


# ---- Summary ----

@router.get("/summary/{manufacturing_unit_id}")
def get_sec_summary(
    manufacturing_unit_id: int,
    year: int,
    service: PatSecService = Depends(get_service),
):
    return service.get_sec_summary(manufacturing_unit_id, year)
