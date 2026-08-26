"""
Manufacturing Electricity Record endpoints (Scope 2 purchased
electricity for ManufactureOS). Prefix /manufacturing-electricity-records.
organization_id always from JWT.
"""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.api.deps import get_current_user
from app.services.manufacturing_electricity_service import ManufacturingElectricityService
from app.repositories.manufacturing_electricity_record_repository import (
    ManufacturingElectricityRecordRepository,
)
from app.repositories.manufacturing_unit_repository import ManufacturingUnitRepository
from app.schemas.manufacturing_electricity_record import (
    ManufacturingElectricityRecordCreate,
    ManufacturingElectricityRecordUpdate,
    ManufacturingElectricityRecordResponse,
)

router = APIRouter(prefix="/manufacturing-electricity-records", tags=["manufacturing-electricity-records"])


def get_service(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> ManufacturingElectricityService:
    org_id = current_user.organization_id
    return ManufacturingElectricityService(
        electricity_repository=ManufacturingElectricityRecordRepository(db, organization_id=org_id),
        unit_repository=ManufacturingUnitRepository(db, organization_id=org_id),
    )


@router.post("/", response_model=ManufacturingElectricityRecordResponse, status_code=201)
def create_record(payload: ManufacturingElectricityRecordCreate, service: ManufacturingElectricityService = Depends(get_service)):
    return service.create_record(payload)


@router.get("/", response_model=list[ManufacturingElectricityRecordResponse])
def list_records(year: int | None = None, service: ManufacturingElectricityService = Depends(get_service)):
    return service.list_records(year=year)


@router.get("/by-unit/{manufacturing_unit_id}", response_model=list[ManufacturingElectricityRecordResponse])
def list_by_unit(manufacturing_unit_id: int, year: int | None = None, service: ManufacturingElectricityService = Depends(get_service)):
    return service.list_by_unit(manufacturing_unit_id, year=year)


@router.get("/{record_id}", response_model=ManufacturingElectricityRecordResponse)
def get_record(record_id: int, service: ManufacturingElectricityService = Depends(get_service)):
    result = service.get_record(record_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Manufacturing electricity record not found")
    return result


@router.put("/{record_id}", response_model=ManufacturingElectricityRecordResponse)
def update_record(
    record_id: int,
    payload: ManufacturingElectricityRecordUpdate,
    service: ManufacturingElectricityService = Depends(get_service),
):
    result = service.update_record(record_id, payload)
    if result is None:
        raise HTTPException(status_code=404, detail="Manufacturing electricity record not found")
    return result


@router.delete("/{record_id}", status_code=204)
def delete_record(record_id: int, service: ManufacturingElectricityService = Depends(get_service)):
    if not service.delete_record(record_id):
        raise HTTPException(status_code=404, detail="Manufacturing electricity record not found")
