from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_writer
from app.database.session import get_db
from app.models.user import User
from app.repositories.facility_category_repository import FacilityCategoryRepository
from app.schemas.facility_category import (
    FacilityCategoryCreate,
    FacilityCategoryResponse,
    FacilityCategoryUpdate,
)
from app.services.facility_category_service import FacilityCategoryService

router = APIRouter(
    prefix="/facility-categories",
    tags=["Facility Categories"],
)


def get_service(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FacilityCategoryService:
    repository = FacilityCategoryRepository(db, organization_id=current_user.organization_id)
    return FacilityCategoryService(repository)


@router.get("/", response_model=list[FacilityCategoryResponse])
def get_categories(
    segment: str,
    service: FacilityCategoryService = Depends(get_service),
):
    return service.get_by_segment(segment)


@router.post(
    "/",
    response_model=FacilityCategoryResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_writer)],
)
def create_category(
    category: FacilityCategoryCreate,
    service: FacilityCategoryService = Depends(get_service),
):
    return service.create(category)


@router.put(
    "/{category_id}",
    response_model=FacilityCategoryResponse,
    dependencies=[Depends(require_writer)],
)
def update_category(
    category_id: int,
    category: FacilityCategoryUpdate,
    service: FacilityCategoryService = Depends(get_service),
):
    return service.update(category_id, category)


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_writer)],
)
def delete_category(
    category_id: int,
    service: FacilityCategoryService = Depends(get_service),
):
    service.delete(category_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
