from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.repositories.water_record_repository import WaterRecordRepository
from app.repositories.waste_record_repository import WasteRecordRepository
from app.schemas.water_record import (
    WaterRecordCreate,
    WaterRecordRead,
    WaterRecordUpdate,
)
from app.schemas.waste_record import (
    WasteRecordCreate,
    WasteRecordRead,
    WasteRecordUpdate,
)
from app.services.water_waste_service import WaterWasteService

router = APIRouter(
    prefix="/water-waste",
    tags=["BRSR P6 - Water and Waste"],
)


def get_service(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WaterWasteService:
    # Tenant-scoped: organization_id always from the JWT.
    return WaterWasteService(db, organization_id=current_user.organization_id)


def get_org_id(current_user: User = Depends(get_current_user)) -> int:
    return current_user.organization_id


# --- summary ---


@router.get("/summary")
def get_summary(
    year: int | None = None,
    service: WaterWasteService = Depends(get_service),
):
    """Organisation water and waste totals for BRSR P6. Figures stay null
    where nothing was disclosed, so 'not tracked' never reads as zero."""
    return service.get_summary(year)


# --- water ---


@router.get("/water", response_model=list[WaterRecordRead])
def list_water_records(
    year: int | None = None,
    service: WaterWasteService = Depends(get_service),
):
    """Water records with derived withdrawal/discharge/consumption totals."""
    return service.get_water_records(year)


@router.post("/water", response_model=WaterRecordRead, status_code=201)
def create_water_record(
    data: WaterRecordCreate,
    db: Session = Depends(get_db),
    org_id: int = Depends(get_org_id),
    service: WaterWasteService = Depends(get_service),
):
    record = WaterRecordRepository(db, org_id).create(data)
    return service.enrich_water(record)


@router.put("/water/{record_id}", response_model=WaterRecordRead)
def update_water_record(
    record_id: int,
    data: WaterRecordUpdate,
    db: Session = Depends(get_db),
    org_id: int = Depends(get_org_id),
    service: WaterWasteService = Depends(get_service),
):
    repo = WaterRecordRepository(db, org_id)
    record = repo.get_by_id(record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Water record not found")
    return service.enrich_water(repo.update(record, data))


@router.delete("/water/{record_id}", status_code=204)
def delete_water_record(
    record_id: int,
    db: Session = Depends(get_db),
    org_id: int = Depends(get_org_id),
):
    repo = WaterRecordRepository(db, org_id)
    record = repo.get_by_id(record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Water record not found")
    repo.delete(record)


# --- waste ---


@router.get("/waste", response_model=list[WasteRecordRead])
def list_waste_records(
    year: int | None = None,
    service: WaterWasteService = Depends(get_service),
):
    """Waste records with derived generated/recovered/disposed totals."""
    return service.get_waste_records(year)


@router.post("/waste", response_model=WasteRecordRead, status_code=201)
def create_waste_record(
    data: WasteRecordCreate,
    db: Session = Depends(get_db),
    org_id: int = Depends(get_org_id),
    service: WaterWasteService = Depends(get_service),
):
    record = WasteRecordRepository(db, org_id).create(data)
    return service.enrich_waste(record)


@router.put("/waste/{record_id}", response_model=WasteRecordRead)
def update_waste_record(
    record_id: int,
    data: WasteRecordUpdate,
    db: Session = Depends(get_db),
    org_id: int = Depends(get_org_id),
    service: WaterWasteService = Depends(get_service),
):
    repo = WasteRecordRepository(db, org_id)
    record = repo.get_by_id(record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Waste record not found")
    return service.enrich_waste(repo.update(record, data))


@router.delete("/waste/{record_id}", status_code=204)
def delete_waste_record(
    record_id: int,
    db: Session = Depends(get_db),
    org_id: int = Depends(get_org_id),
):
    repo = WasteRecordRepository(db, org_id)
    record = repo.get_by_id(record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Waste record not found")
    repo.delete(record)
