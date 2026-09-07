"""
Sustainable Product Record + Reclaimed Material endpoints
(BRSR Section C, Principle 2). Prefix /sustainable-product-records.
organization_id always from JWT, never from path or body.
"""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.api.deps import get_current_user
from app.services.sustainable_product_record_service import (
    SustainableProductRecordService,
    DuplicateReportingYear,
)
from app.schemas.sustainable_product_record import (
    SustainableProductRecordCreate,
    SustainableProductRecordUpdate,
    SustainableProductRecordResponse,
    ReclaimedMaterialCreate,
    ReclaimedMaterialUpdate,
    ReclaimedMaterialResponse,
)

router = APIRouter(prefix="/sustainable-product-records", tags=["sustainable-product-records"])

NOT_FOUND = "Sustainable product record not found"
MATERIAL_NOT_FOUND = "Reclaimed material record not found"


def get_service(
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
) -> SustainableProductRecordService:
    return SustainableProductRecordService(db, current_user.organization_id)


def _conflict(exc: DuplicateReportingYear) -> HTTPException:
    return HTTPException(
        status_code=409,
        detail=f"A Principle 2 record already exists for reporting year {exc.args[0]}",
    )


@router.post("/", response_model=SustainableProductRecordResponse, status_code=201)
def create_record(
    payload: SustainableProductRecordCreate,
    service: SustainableProductRecordService = Depends(get_service),
):
    try:
        return service.create_record(payload.model_dump())
    except DuplicateReportingYear as exc:
        raise _conflict(exc)


@router.get("/", response_model=list[SustainableProductRecordResponse])
def list_records(service: SustainableProductRecordService = Depends(get_service)):
    return service.list_records()


@router.get("/{record_id}", response_model=SustainableProductRecordResponse)
def get_record(record_id: int, service: SustainableProductRecordService = Depends(get_service)):
    result = service.get_record(record_id)
    if result is None:
        raise HTTPException(status_code=404, detail=NOT_FOUND)
    return result


@router.put("/{record_id}", response_model=SustainableProductRecordResponse)
def update_record(
    record_id: int,
    payload: SustainableProductRecordUpdate,
    service: SustainableProductRecordService = Depends(get_service),
):
    try:
        result = service.update_record(record_id, payload.model_dump(exclude_unset=True))
    except DuplicateReportingYear as exc:
        raise _conflict(exc)
    if result is None:
        raise HTTPException(status_code=404, detail=NOT_FOUND)
    return result


@router.delete("/{record_id}", status_code=204)
def delete_record(record_id: int, service: SustainableProductRecordService = Depends(get_service)):
    if not service.delete_record(record_id):
        raise HTTPException(status_code=404, detail=NOT_FOUND)


@router.post("/{record_id}/materials", response_model=ReclaimedMaterialResponse, status_code=201)
def create_material(
    record_id: int,
    payload: ReclaimedMaterialCreate,
    service: SustainableProductRecordService = Depends(get_service),
):
    result = service.create_material(record_id, payload.model_dump())
    if result is None:
        raise HTTPException(status_code=404, detail=NOT_FOUND)
    return result


@router.put("/materials/{material_id}", response_model=ReclaimedMaterialResponse)
def update_material(
    material_id: int,
    payload: ReclaimedMaterialUpdate,
    service: SustainableProductRecordService = Depends(get_service),
):
    result = service.update_material(material_id, payload.model_dump(exclude_unset=True))
    if result is None:
        raise HTTPException(status_code=404, detail=MATERIAL_NOT_FOUND)
    return result


@router.delete("/materials/{material_id}", status_code=204)
def delete_material(material_id: int, service: SustainableProductRecordService = Depends(get_service)):
    if not service.delete_material(material_id):
        raise HTTPException(status_code=404, detail=MATERIAL_NOT_FOUND)
