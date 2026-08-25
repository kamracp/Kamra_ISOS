"""
Stakeholder Engagement Record + Stakeholder Group endpoints (BRSR Section C, Principle 4).
Prefix /stakeholder-engagement-records. organization_id always from JWT.
"""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.api.deps import get_current_user
from app.services.stakeholder_engagement_record_service import StakeholderEngagementRecordService
from app.schemas.stakeholder_engagement_record import (
    StakeholderEngagementRecordCreate,
    StakeholderEngagementRecordUpdate,
    StakeholderEngagementRecordResponse,
    StakeholderGroupCreate,
    StakeholderGroupUpdate,
    StakeholderGroupResponse,
)

router = APIRouter(prefix="/stakeholder-engagement-records", tags=["stakeholder-engagement-records"])


def get_service(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> StakeholderEngagementRecordService:
    return StakeholderEngagementRecordService(db, current_user.organization_id)


@router.post("/", response_model=StakeholderEngagementRecordResponse, status_code=201)
def create_record(payload: StakeholderEngagementRecordCreate, service: StakeholderEngagementRecordService = Depends(get_service)):
    return service.create_record(payload.model_dump())


@router.get("/", response_model=list[StakeholderEngagementRecordResponse])
def list_records(service: StakeholderEngagementRecordService = Depends(get_service)):
    return service.list_records()


@router.get("/{record_id}", response_model=StakeholderEngagementRecordResponse)
def get_record(record_id: int, service: StakeholderEngagementRecordService = Depends(get_service)):
    result = service.get_record(record_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Stakeholder engagement record not found")
    return result


@router.put("/{record_id}", response_model=StakeholderEngagementRecordResponse)
def update_record(
    record_id: int,
    payload: StakeholderEngagementRecordUpdate,
    service: StakeholderEngagementRecordService = Depends(get_service),
):
    result = service.update_record(record_id, payload.model_dump(exclude_unset=True))
    if result is None:
        raise HTTPException(status_code=404, detail="Stakeholder engagement record not found")
    return result


@router.delete("/{record_id}", status_code=204)
def delete_record(record_id: int, service: StakeholderEngagementRecordService = Depends(get_service)):
    if not service.delete_record(record_id):
        raise HTTPException(status_code=404, detail="Stakeholder engagement record not found")


@router.post("/{record_id}/groups", response_model=StakeholderGroupResponse, status_code=201)
def create_group(
    record_id: int,
    payload: StakeholderGroupCreate,
    service: StakeholderEngagementRecordService = Depends(get_service),
):
    result = service.create_group(record_id, payload.model_dump())
    if result is None:
        raise HTTPException(status_code=404, detail="Stakeholder engagement record not found")
    return result


@router.put("/groups/{group_id}", response_model=StakeholderGroupResponse)
def update_group(
    group_id: int,
    payload: StakeholderGroupUpdate,
    service: StakeholderEngagementRecordService = Depends(get_service),
):
    result = service.update_group(group_id, payload.model_dump(exclude_unset=True))
    if result is None:
        raise HTTPException(status_code=404, detail="Stakeholder group not found")
    return result


@router.delete("/groups/{group_id}", status_code=204)
def delete_group(group_id: int, service: StakeholderEngagementRecordService = Depends(get_service)):
    if not service.delete_group(group_id):
        raise HTTPException(status_code=404, detail="Stakeholder group not found")
