"""
Ethics Record endpoints (BRSR Section C, Principle 1).
Prefix /ethics-records. organization_id always from JWT.
"""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.api.deps import get_current_user
from app.services.ethics_record_service import EthicsRecordService
from app.schemas.ethics_record import (
    EthicsRecordCreate,
    EthicsRecordUpdate,
    EthicsRecordResponse,
)

router = APIRouter(prefix="/ethics-records", tags=["ethics-records"])


def get_service(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> EthicsRecordService:
    return EthicsRecordService(db, current_user.organization_id)


@router.post("/", response_model=EthicsRecordResponse, status_code=201)
def create_record(payload: EthicsRecordCreate, service: EthicsRecordService = Depends(get_service)):
    return service.create_record(payload.model_dump())


@router.get("/", response_model=list[EthicsRecordResponse])
def list_records(service: EthicsRecordService = Depends(get_service)):
    return service.list_records()


@router.get("/{record_id}", response_model=EthicsRecordResponse)
def get_record(record_id: int, service: EthicsRecordService = Depends(get_service)):
    result = service.get_record(record_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Ethics record not found")
    return result


@router.put("/{record_id}", response_model=EthicsRecordResponse)
def update_record(
    record_id: int,
    payload: EthicsRecordUpdate,
    service: EthicsRecordService = Depends(get_service),
):
    result = service.update_record(record_id, payload.model_dump(exclude_unset=True))
    if result is None:
        raise HTTPException(status_code=404, detail="Ethics record not found")
    return result


@router.delete("/{record_id}", status_code=204)
def delete_record(record_id: int, service: EthicsRecordService = Depends(get_service)):
    if not service.delete_record(record_id):
        raise HTTPException(status_code=404, detail="Ethics record not found")
