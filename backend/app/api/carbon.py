from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.repositories.emission_factor_repository import (
    EmissionFactorRepository,
)
from app.repositories.energy_meter_repository import EnergyMeterRepository
from app.repositories.utility_bill_repository import UtilityBillRepository
from app.services.carbon_service import CarbonService

router = APIRouter(
    prefix="/carbon",
    tags=["Carbon Engine"],
)


def get_service(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CarbonService:
    org_id = current_user.organization_id

    return CarbonService(
        # Tenant-scoped: this org's bills and meters only...
        bill_repository=UtilityBillRepository(db, organization_id=org_id),
        meter_repository=EnergyMeterRepository(db, organization_id=org_id),
        # ...multiplied by the GLOBAL official factor library.
        factor_repository=EmissionFactorRepository(db),
    )


@router.get("/summary")
def get_carbon_summary(
    year: int | None = Query(
        None, ge=2000, le=2100,
        description="Calendar year (matched on billing_period_start); omit for all bills",
    ),
    service: CarbonService = Depends(get_service),
):
    """Organization-wide CO2e summary: totals by scope, monthly trend,
    avoided emissions, pending bills, and a per-bill audit trail.
    Optional year keeps the Dashboard's no-year behaviour unchanged."""
    return service.get_summary(year=year)
