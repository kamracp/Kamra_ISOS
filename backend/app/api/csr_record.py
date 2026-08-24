"""
CSR Record + Project endpoints (BRSR Section C, Principle 8).
Prefix /csr-records. organization_id always from JWT.
"""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.api.deps import get_current_user
from app.services.csr_record_service import CsrRecordService
from app.schemas.csr_record import (
    CsrRecordCreate,
    CsrRecordUpdate,
    CsrRecordResponse,
    CsrProjectCreate,
    CsrProjectUpdate,
    CsrProjectResponse,
)

router = APIRouter(prefix="/csr-records", tags=["csr-records"])


def get_service(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> CsrRecordService:
    return CsrRecordService(db, current_user.organization_id)


@router.post("/", response_model=CsrRecordResponse, status_code=201)
def create_record(payload: CsrRecordCreate, service: CsrRecordService = Depends(get_service)):
    return service.create_record(payload.model_dump())


@router.get("/", response_model=list[CsrRecordResponse])
def list_records(service: CsrRecordService = Depends(get_service)):
    return service.list_records()


@router.get("/{record_id}", response_model=CsrRecordResponse)
def get_record(record_id: int, service: CsrRecordService = Depends(get_service)):
    result = service.get_record(record_id)
    if result is None:
        raise HTTPException(status_code=404, detail="CSR record not found")
    return result


@router.put("/{record_id}", response_model=CsrRecordResponse)
def update_record(
    record_id: int,
    payload: CsrRecordUpdate,
    service: CsrRecordService = Depends(get_service),
):
    result = service.update_record(record_id, payload.model_dump(exclude_unset=True))
    if result is None:
        raise HTTPException(status_code=404, detail="CSR record not found")
    return result


@router.delete("/{record_id}", status_code=204)
def delete_record(record_id: int, service: CsrRecordService = Depends(get_service)):
    if not service.delete_record(record_id):
        raise HTTPException(status_code=404, detail="CSR record not found")


@router.post("/{record_id}/projects", response_model=CsrProjectResponse, status_code=201)
def create_project(
    record_id: int,
    payload: CsrProjectCreate,
    service: CsrRecordService = Depends(get_service),
):
    result = service.create_project(record_id, payload.model_dump())
    if result is None:
        raise HTTPException(status_code=404, detail="CSR record not found")
    return result


@router.put("/projects/{project_id}", response_model=CsrProjectResponse)
def update_project(
    project_id: int,
    payload: CsrProjectUpdate,
    service: CsrRecordService = Depends(get_service),
):
    result = service.update_project(project_id, payload.model_dump(exclude_unset=True))
    if result is None:
        raise HTTPException(status_code=404, detail="CSR project not found")
    return result


@router.delete("/projects/{project_id}", status_code=204)
def delete_project(project_id: int, service: CsrRecordService = Depends(get_service)):
    if not service.delete_project(project_id):
        raise HTTPException(status_code=404, detail="CSR project not found")
