from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.repositories.manufacturing_emission_record_repository import (
    ManufacturingEmissionRecordRepository,
)
from app.repositories.manufacturing_unit_repository import ManufacturingUnitRepository
from app.services.manufacturing_carbon_service import ManufacturingCarbonService

router = APIRouter(
    prefix="/manufacturing-carbon",
    tags=["Manufacturing Carbon Engine"],
)


def get_service(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ManufacturingCarbonService:
    org_id = current_user.organization_id

    return ManufacturingCarbonService(
        # Tenant-scoped: this org's emission records and units only.
        emission_record_repository=ManufacturingEmissionRecordRepository(
            db, organization_id=org_id
        ),
        unit_repository=ManufacturingUnitRepository(db, organization_id=org_id),
    )


@router.get("/summary")
def get_manufacturing_carbon_summary(
    year: int | None = None,
    service: ManufacturingCarbonService = Depends(get_service),
):
    """Organization-wide manufacturing Scope 1 process-emissions summary:
    totals by sector, per-unit breakdown, biogenic CO2 tracked separately.
    Optional year filter (matched against period_start)."""
    return service.get_summary(year=year)
