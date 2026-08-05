from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_writer
from app.database.session import get_db
from app.models.user import User
from app.repositories.climate_risk_repository import ClimateRiskRepository
from app.schemas.climate_risk import (
    ClimateRiskCreate,
    ClimateRiskResponse,
    ClimateRiskUpdate,
)
from app.services.climate_risk_service import ClimateRiskService

router = APIRouter(
    prefix="/climate-risks",
    tags=["Climate Risks (TCFD)"],
)


def get_service(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClimateRiskService:
    repository = ClimateRiskRepository(db, organization_id=current_user.organization_id)
    return ClimateRiskService(repository)


@router.get("/", response_model=list[ClimateRiskResponse])
def get_all_risks(service: ClimateRiskService = Depends(get_service)):
    return service.get_all()


@router.get("/{risk_id}", response_model=ClimateRiskResponse)
def get_risk(risk_id: int, service: ClimateRiskService = Depends(get_service)):
    return service.get_by_id(risk_id)


@router.post(
    "/",
    response_model=ClimateRiskResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_writer)],
)
def create_risk(
    risk: ClimateRiskCreate,
    service: ClimateRiskService = Depends(get_service),
):
    return service.create(risk)


@router.put(
    "/{risk_id}",
    response_model=ClimateRiskResponse,
    dependencies=[Depends(require_writer)],
)
def update_risk(
    risk_id: int,
    risk: ClimateRiskUpdate,
    service: ClimateRiskService = Depends(get_service),
):
    return service.update(risk_id, risk)


@router.delete(
    "/{risk_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_writer)],
)
def delete_risk(risk_id: int, service: ClimateRiskService = Depends(get_service)):
    service.delete(risk_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/reports/summary")
def get_risk_summary(service: ClimateRiskService = Depends(get_service)):
    """TCFD-style portfolio risk summary: total financial exposure, by category."""
    return service.get_summary()
