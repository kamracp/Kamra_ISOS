"""
Manufacturing Fuel Record endpoints (fuel combustion for ManufactureOS).
Prefix /manufacturing-fuel-records. organization_id always from JWT.
"""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.api.deps import get_current_user
from app.services.manufacturing_fuel_service import ManufacturingFuelService
from app.repositories.manufacturing_fuel_record_repository import ManufacturingFuelRecordRepository
from app.schemas.manufacturing_fuel_record import (
    ManufacturingFuelRecordCreate, ManufacturingFuelRecordUpdate, ManufacturingFuelRecordResponse,
)

router = APIRouter(prefix="/manufacturing-fuel-records", tags=["manufacturing-fuel-records"])
NOT_FOUND = "Fuel record not found"


def get_service(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> ManufacturingFuelService:
    return ManufacturingFuelService(ManufacturingFuelRecordRepository(db, organization_id=current_user.organization_id))


@router.get("/library")
def fuel_library(service: ManufacturingFuelService = Depends(get_service)):
    """The 54 IPCC fuels with LHV and emission factors -- for the entry form dropdown."""
    return service.library()


@router.post("/", response_model=ManufacturingFuelRecordResponse, status_code=201)
def create_record(payload: ManufacturingFuelRecordCreate, service: ManufacturingFuelService = Depends(get_service)):
    return service.create_record(payload)


@router.get("/", response_model=list[ManufacturingFuelRecordResponse])
def list_records(year: int | None = None, service: ManufacturingFuelService = Depends(get_service)):
    return service.list_records(year=year)


@router.get("/by-unit/{manufacturing_unit_id}", response_model=list[ManufacturingFuelRecordResponse])
def list_by_unit(manufacturing_unit_id: int, year: int | None = None, service: ManufacturingFuelService = Depends(get_service)):
    return service.list_by_unit(manufacturing_unit_id, year=year)


@router.get("/{record_id}", response_model=ManufacturingFuelRecordResponse)
def get_record(record_id: int, service: ManufacturingFuelService = Depends(get_service)):
    result = service.get_record(record_id)
    if result is None:
        raise HTTPException(status_code=404, detail=NOT_FOUND)
    return result


@router.put("/{record_id}", response_model=ManufacturingFuelRecordResponse)
def update_record(record_id: int, payload: ManufacturingFuelRecordUpdate, service: ManufacturingFuelService = Depends(get_service)):
    result = service.update_record(record_id, payload)
    if result is None:
        raise HTTPException(status_code=404, detail=NOT_FOUND)
    return result


@router.delete("/{record_id}", status_code=204)
def delete_record(record_id: int, service: ManufacturingFuelService = Depends(get_service)):
    if not service.delete_record(record_id):
        raise HTTPException(status_code=404, detail=NOT_FOUND)
