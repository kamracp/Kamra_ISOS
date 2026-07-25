from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_writer
from app.database.session import get_db
from app.models.user import User
from app.repositories.manufacturing_unit_repository import ManufacturingUnitRepository
from app.schemas.manufacturing_unit import (
    ManufacturingUnitCreate,
    ManufacturingUnitResponse,
    ManufacturingUnitUpdate,
)
from app.services import sec_calculation_service
from app.services.aluminium_ghg_calculator import (
    AluminiumCellTechnology,
    calculate_tier1_default_co2,
)
from app.services.manufacturing_unit_service import ManufacturingUnitService

router = APIRouter(
    prefix="/manufacturing-units",
    tags=["Manufacturing Units"],
)


def get_service(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ManufacturingUnitService:
    repository = ManufacturingUnitRepository(db, organization_id=current_user.organization_id)
    return ManufacturingUnitService(repository)


@router.get("/", response_model=list[ManufacturingUnitResponse])
def get_all_units(service: ManufacturingUnitService = Depends(get_service)):
    return service.get_all()


@router.get("/{unit_id}", response_model=ManufacturingUnitResponse)
def get_unit(unit_id: int, service: ManufacturingUnitService = Depends(get_service)):
    return service.get_by_id(unit_id)


@router.post(
    "/",
    response_model=ManufacturingUnitResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_writer)],
)
def create_unit(unit: ManufacturingUnitCreate, service: ManufacturingUnitService = Depends(get_service)):
    return service.create(unit)


@router.put(
    "/{unit_id}",
    response_model=ManufacturingUnitResponse,
    dependencies=[Depends(require_writer)],
)
def update_unit(
    unit_id: int,
    unit: ManufacturingUnitUpdate,
    service: ManufacturingUnitService = Depends(get_service),
):
    return service.update(unit_id, unit)


@router.delete(
    "/{unit_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_writer)],
)
def delete_unit(unit_id: int, service: ManufacturingUnitService = Depends(get_service)):
    service.delete(unit_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{unit_id}/sec-summary")
def get_sec_summary(
    unit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """SEC (BEE PAT) / EnPI (ISO 50001) summary: baseline vs every period."""
    return sec_calculation_service.get_sec_summary(
        db=db,
        organization_id=current_user.organization_id,
        manufacturing_unit_id=unit_id,
    )


@router.get("/{unit_id}/aluminium-tier1-co2")
def get_aluminium_tier1_co2(
    unit_id: int,
    technology: AluminiumCellTechnology,
    aluminium_production_tonnes: float,
    current_user: User = Depends(get_current_user),
):
    """
    Aluminium GHG Protocol Cluster 1 - Tier 1 Default CO2 from smelting.

    Query params:
        technology: prebake | soderberg
        aluminium_production_tonnes: aluminium produced in the period (t)
    """
    return calculate_tier1_default_co2(
        technology=technology,
        aluminium_production_tonnes=aluminium_production_tonnes,
    )
