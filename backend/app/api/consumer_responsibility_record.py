"""Consumer Responsibility endpoints (BRSR Section C, Principle 9).
Prefix /consumer-responsibility-records. organization_id always from JWT."""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.api.deps import get_current_user
from app.services.consumer_responsibility_record_service import ConsumerResponsibilityRecordService, DuplicateReportingYear
from app.schemas.consumer_responsibility_record import (
    ConsumerResponsibilityRecordCreate, ConsumerResponsibilityRecordUpdate, ConsumerResponsibilityRecordResponse,
    ConsumerComplaintCreate, ConsumerComplaintUpdate, ConsumerComplaintResponse,
)

router = APIRouter(prefix="/consumer-responsibility-records", tags=["consumer-responsibility-records"])
NOT_FOUND = "Consumer responsibility record not found"
COMPLAINT_NOT_FOUND = "Consumer complaint row not found"


def get_service(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> ConsumerResponsibilityRecordService:
    return ConsumerResponsibilityRecordService(db, current_user.organization_id)


def _conflict(exc: DuplicateReportingYear) -> HTTPException:
    return HTTPException(status_code=409, detail=f"A Principle 9 record already exists for reporting year {exc.args[0]}")


@router.post("/", response_model=ConsumerResponsibilityRecordResponse, status_code=201)
def create_record(payload: ConsumerResponsibilityRecordCreate, service: ConsumerResponsibilityRecordService = Depends(get_service)):
    try:
        return service.create_record(payload.model_dump())
    except DuplicateReportingYear as exc:
        raise _conflict(exc)


@router.get("/", response_model=list[ConsumerResponsibilityRecordResponse])
def list_records(service: ConsumerResponsibilityRecordService = Depends(get_service)):
    return service.list_records()


@router.get("/{record_id}", response_model=ConsumerResponsibilityRecordResponse)
def get_record(record_id: int, service: ConsumerResponsibilityRecordService = Depends(get_service)):
    result = service.get_record(record_id)
    if result is None:
        raise HTTPException(status_code=404, detail=NOT_FOUND)
    return result


@router.put("/{record_id}", response_model=ConsumerResponsibilityRecordResponse)
def update_record(record_id: int, payload: ConsumerResponsibilityRecordUpdate, service: ConsumerResponsibilityRecordService = Depends(get_service)):
    try:
        result = service.update_record(record_id, payload.model_dump(exclude_unset=True))
    except DuplicateReportingYear as exc:
        raise _conflict(exc)
    if result is None:
        raise HTTPException(status_code=404, detail=NOT_FOUND)
    return result


@router.delete("/{record_id}", status_code=204)
def delete_record(record_id: int, service: ConsumerResponsibilityRecordService = Depends(get_service)):
    if not service.delete_record(record_id):
        raise HTTPException(status_code=404, detail=NOT_FOUND)


@router.post("/{record_id}/complaints", response_model=ConsumerComplaintResponse, status_code=201)
def create_complaint(record_id: int, payload: ConsumerComplaintCreate, service: ConsumerResponsibilityRecordService = Depends(get_service)):
    result = service.create_complaint(record_id, payload.model_dump())
    if result is None:
        raise HTTPException(status_code=404, detail=NOT_FOUND)
    return result


@router.put("/complaints/{complaint_id}", response_model=ConsumerComplaintResponse)
def update_complaint(complaint_id: int, payload: ConsumerComplaintUpdate, service: ConsumerResponsibilityRecordService = Depends(get_service)):
    result = service.update_complaint(complaint_id, payload.model_dump(exclude_unset=True))
    if result is None:
        raise HTTPException(status_code=404, detail=COMPLAINT_NOT_FOUND)
    return result


@router.delete("/complaints/{complaint_id}", status_code=204)
def delete_complaint(complaint_id: int, service: ConsumerResponsibilityRecordService = Depends(get_service)):
    if not service.delete_complaint(complaint_id):
        raise HTTPException(status_code=404, detail=COMPLAINT_NOT_FOUND)
