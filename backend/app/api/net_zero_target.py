from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_writer
from app.database.session import get_db
from app.models.user import User
from app.repositories.net_zero_target_repository import NetZeroTargetRepository
from app.schemas.net_zero_target import (
    NetZeroTargetCreate,
    NetZeroTargetResponse,
    NetZeroTargetUpdate,
)
from app.services import net_zero_service
from app.services.net_zero_target_service import NetZeroTargetService

router = APIRouter(
    prefix="/net-zero-targets",
    tags=["Net Zero Targets"],
)


def get_service(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NetZeroTargetService:
    repository = NetZeroTargetRepository(db, organization_id=current_user.organization_id)
    return NetZeroTargetService(repository)


@router.get("/", response_model=list[NetZeroTargetResponse])
def get_all_targets(service: NetZeroTargetService = Depends(get_service)):
    return service.get_all()


@router.get("/{target_id}", response_model=NetZeroTargetResponse)
def get_target(target_id: int, service: NetZeroTargetService = Depends(get_service)):
    return service.get_by_id(target_id)


@router.post(
    "/",
    response_model=NetZeroTargetResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_writer)],
)
def create_target(
    target: NetZeroTargetCreate, service: NetZeroTargetService = Depends(get_service)
):
    return service.create(target)


@router.put(
    "/{target_id}",
    response_model=NetZeroTargetResponse,
    dependencies=[Depends(require_writer)],
)
def update_target(
    target_id: int,
    target: NetZeroTargetUpdate,
    service: NetZeroTargetService = Depends(get_service),
):
    return service.update(target_id, target)


@router.delete(
    "/{target_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_writer)],
)
def delete_target(target_id: int, service: NetZeroTargetService = Depends(get_service)):
    service.delete(target_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{target_id}/summary")
def get_target_summary(
    target_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """BAU vs target trajectory + gap + full MACC list."""
    return net_zero_service.get_net_zero_summary(
        db=db,
        organization_id=current_user.organization_id,
        target_id=target_id,
    )
