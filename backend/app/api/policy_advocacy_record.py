"""
Policy Advocacy Record + Trade Association endpoints (BRSR Section C, Principle 7).
Prefix /policy-advocacy-records. organization_id always from JWT.
"""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.api.deps import get_current_user
from app.services.policy_advocacy_record_service import PolicyAdvocacyRecordService
from app.schemas.policy_advocacy_record import (
    PolicyAdvocacyRecordCreate,
    PolicyAdvocacyRecordUpdate,
    PolicyAdvocacyRecordResponse,
    TradeAssociationCreate,
    TradeAssociationUpdate,
    TradeAssociationResponse,
)

router = APIRouter(prefix="/policy-advocacy-records", tags=["policy-advocacy-records"])


def get_service(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> PolicyAdvocacyRecordService:
    return PolicyAdvocacyRecordService(db, current_user.organization_id)


@router.post("/", response_model=PolicyAdvocacyRecordResponse, status_code=201)
def create_record(payload: PolicyAdvocacyRecordCreate, service: PolicyAdvocacyRecordService = Depends(get_service)):
    return service.create_record(payload.model_dump())


@router.get("/", response_model=list[PolicyAdvocacyRecordResponse])
def list_records(service: PolicyAdvocacyRecordService = Depends(get_service)):
    return service.list_records()


@router.get("/{record_id}", response_model=PolicyAdvocacyRecordResponse)
def get_record(record_id: int, service: PolicyAdvocacyRecordService = Depends(get_service)):
    result = service.get_record(record_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Policy advocacy record not found")
    return result


@router.put("/{record_id}", response_model=PolicyAdvocacyRecordResponse)
def update_record(
    record_id: int,
    payload: PolicyAdvocacyRecordUpdate,
    service: PolicyAdvocacyRecordService = Depends(get_service),
):
    result = service.update_record(record_id, payload.model_dump(exclude_unset=True))
    if result is None:
        raise HTTPException(status_code=404, detail="Policy advocacy record not found")
    return result


@router.delete("/{record_id}", status_code=204)
def delete_record(record_id: int, service: PolicyAdvocacyRecordService = Depends(get_service)):
    if not service.delete_record(record_id):
        raise HTTPException(status_code=404, detail="Policy advocacy record not found")


@router.post("/{record_id}/associations", response_model=TradeAssociationResponse, status_code=201)
def create_association(
    record_id: int,
    payload: TradeAssociationCreate,
    service: PolicyAdvocacyRecordService = Depends(get_service),
):
    result = service.create_association(record_id, payload.model_dump())
    if result is None:
        raise HTTPException(status_code=404, detail="Policy advocacy record not found")
    return result


@router.put("/associations/{association_id}", response_model=TradeAssociationResponse)
def update_association(
    association_id: int,
    payload: TradeAssociationUpdate,
    service: PolicyAdvocacyRecordService = Depends(get_service),
):
    result = service.update_association(association_id, payload.model_dump(exclude_unset=True))
    if result is None:
        raise HTTPException(status_code=404, detail="Trade association not found")
    return result


@router.delete("/associations/{association_id}", status_code=204)
def delete_association(association_id: int, service: PolicyAdvocacyRecordService = Depends(get_service)):
    if not service.delete_association(association_id):
        raise HTTPException(status_code=404, detail="Trade association not found")
