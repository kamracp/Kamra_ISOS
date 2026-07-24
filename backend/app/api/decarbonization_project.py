from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_writer
from app.database.session import get_db
from app.models.user import User
from app.repositories.decarbonization_project_repository import (
    DecarbonizationProjectRepository,
)
from app.schemas.decarbonization_project import (
    DecarbonizationProjectCreate,
    DecarbonizationProjectResponse,
    DecarbonizationProjectUpdate,
)
from app.services import net_zero_service
from app.services.decarbonization_project_service import DecarbonizationProjectService

router = APIRouter(
    prefix="/decarbonization-projects",
    tags=["Decarbonization Projects"],
)


def get_service(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DecarbonizationProjectService:
    repository = DecarbonizationProjectRepository(db, organization_id=current_user.organization_id)
    return DecarbonizationProjectService(repository)


@router.get("/", response_model=list[DecarbonizationProjectResponse])
def get_all_projects(service: DecarbonizationProjectService = Depends(get_service)):
    return service.get_all()


@router.get("/{project_id}", response_model=DecarbonizationProjectResponse)
def get_project(project_id: int, service: DecarbonizationProjectService = Depends(get_service)):
    return service.get_by_id(project_id)


@router.post(
    "/",
    response_model=DecarbonizationProjectResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_writer)],
)
def create_project(
    project: DecarbonizationProjectCreate,
    service: DecarbonizationProjectService = Depends(get_service),
):
    return service.create(project)


@router.put(
    "/{project_id}",
    response_model=DecarbonizationProjectResponse,
    dependencies=[Depends(require_writer)],
)
def update_project(
    project_id: int,
    project: DecarbonizationProjectUpdate,
    service: DecarbonizationProjectService = Depends(get_service),
):
    return service.update(project_id, project)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_writer)],
)
def delete_project(
    project_id: int, service: DecarbonizationProjectService = Depends(get_service)
):
    service.delete(project_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/reports/macc")
def get_macc(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Standalone MACC list (all projects, cheapest-first), no target needed."""
    return net_zero_service.calculate_macc(db=db, organization_id=current_user.organization_id)
