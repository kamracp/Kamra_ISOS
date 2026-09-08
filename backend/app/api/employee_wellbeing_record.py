"""
Employee Well-being endpoints (BRSR Section C, Principle 3).
Prefix /employee-wellbeing-records. organization_id always from JWT.

Child routes for the four tables come from _register_child(). No
`from __future__ import annotations` here -- see human_rights_record.py.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.api.deps import get_current_user
from app.services.employee_wellbeing_record_service import EmployeeWellbeingRecordService, DuplicateReportingYear
from app.schemas.employee_wellbeing_record import (
    EmployeeWellbeingRecordCreate, EmployeeWellbeingRecordUpdate, EmployeeWellbeingRecordResponse,
    MeasureCreate, MeasureUpdate, MeasureResponse,
    ParentalLeaveCreate, ParentalLeaveUpdate, ParentalLeaveResponse,
    TrainingCreate, TrainingUpdate, TrainingResponse,
    WellbeingComplaintCreate, WellbeingComplaintUpdate, WellbeingComplaintResponse,
)

router = APIRouter(prefix="/employee-wellbeing-records", tags=["employee-wellbeing-records"])
NOT_FOUND = "Employee well-being record not found"


def get_service(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> EmployeeWellbeingRecordService:
    return EmployeeWellbeingRecordService(db, current_user.organization_id)


def _conflict(exc: DuplicateReportingYear) -> HTTPException:
    return HTTPException(status_code=409, detail=f"A Principle 3 record already exists for reporting year {exc.args[0]}")


@router.post("/", response_model=EmployeeWellbeingRecordResponse, status_code=201)
def create_record(payload: EmployeeWellbeingRecordCreate, service: EmployeeWellbeingRecordService = Depends(get_service)):
    try:
        return service.create_record(payload.model_dump())
    except DuplicateReportingYear as exc:
        raise _conflict(exc)


@router.get("/", response_model=list[EmployeeWellbeingRecordResponse])
def list_records(service: EmployeeWellbeingRecordService = Depends(get_service)):
    return service.list_records()


@router.get("/{record_id}", response_model=EmployeeWellbeingRecordResponse)
def get_record(record_id: int, service: EmployeeWellbeingRecordService = Depends(get_service)):
    result = service.get_record(record_id)
    if result is None:
        raise HTTPException(status_code=404, detail=NOT_FOUND)
    return result


@router.put("/{record_id}", response_model=EmployeeWellbeingRecordResponse)
def update_record(record_id: int, payload: EmployeeWellbeingRecordUpdate, service: EmployeeWellbeingRecordService = Depends(get_service)):
    try:
        result = service.update_record(record_id, payload.model_dump(exclude_unset=True))
    except DuplicateReportingYear as exc:
        raise _conflict(exc)
    if result is None:
        raise HTTPException(status_code=404, detail=NOT_FOUND)
    return result


@router.delete("/{record_id}", status_code=204)
def delete_record(record_id: int, service: EmployeeWellbeingRecordService = Depends(get_service)):
    if not service.delete_record(record_id):
        raise HTTPException(status_code=404, detail=NOT_FOUND)


def _register_child(kind, path, label, create_schema, update_schema, response_schema):
    child_not_found = f"{label} row not found"

    @router.post(f"/{{record_id}}/{path}", response_model=response_schema, status_code=201, name=f"create_{kind}")
    def create_child(record_id: int, payload: create_schema, service: EmployeeWellbeingRecordService = Depends(get_service)):  # type: ignore[valid-type]
        result = service.create_child(kind, record_id, payload.model_dump())
        if result is None:
            raise HTTPException(status_code=404, detail=NOT_FOUND)
        return result

    @router.put(f"/{path}/{{child_id}}", response_model=response_schema, name=f"update_{kind}")
    def update_child(child_id: int, payload: update_schema, service: EmployeeWellbeingRecordService = Depends(get_service)):  # type: ignore[valid-type]
        result = service.update_child(kind, child_id, payload.model_dump(exclude_unset=True))
        if result is None:
            raise HTTPException(status_code=404, detail=child_not_found)
        return result

    @router.delete(f"/{path}/{{child_id}}", status_code=204, name=f"delete_{kind}")
    def delete_child(child_id: int, service: EmployeeWellbeingRecordService = Depends(get_service)):
        if not service.delete_child(kind, child_id):
            raise HTTPException(status_code=404, detail=child_not_found)


_register_child("measure", "measures", "Well-being measure", MeasureCreate, MeasureUpdate, MeasureResponse)
_register_child("parental", "parental-leave", "Parental leave", ParentalLeaveCreate, ParentalLeaveUpdate, ParentalLeaveResponse)
_register_child("training", "training", "Training", TrainingCreate, TrainingUpdate, TrainingResponse)
_register_child("complaint", "complaints", "Complaint", WellbeingComplaintCreate, WellbeingComplaintUpdate, WellbeingComplaintResponse)
