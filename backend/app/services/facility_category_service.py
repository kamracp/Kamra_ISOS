from app.core.exceptions import ResourceNotFoundException
from app.models.building import Building
from app.repositories.facility_category_repository import FacilityCategoryRepository
from app.schemas.facility_category import (
    FacilityCategoryCreate,
    FacilityCategoryResponse,
    FacilityCategoryUpdate,
)


class FacilityCategoryService:
    def __init__(self, repository: FacilityCategoryRepository):
        self.repository = repository

    def get_by_segment(self, segment: str) -> list[FacilityCategoryResponse]:
        categories = self.repository.get_by_segment(segment)
        results = []
        for c in categories:
            count = (
                self.repository.db.query(Building)
                .filter(Building.category_id == c.id)
                .count()
            )
            response = FacilityCategoryResponse.model_validate(c)
            response.buildings_count = count
            results.append(response)
        return results

    def create(self, data: FacilityCategoryCreate) -> FacilityCategoryResponse:
        category = self.repository.create(data)
        return FacilityCategoryResponse.model_validate(category)

    def update(self, category_id: int, data: FacilityCategoryUpdate) -> FacilityCategoryResponse:
        category = self.repository.get_by_id(category_id)
        if not category:
            raise ResourceNotFoundException("Facility Category", category_id)
        updated = self.repository.update(category, data)
        return FacilityCategoryResponse.model_validate(updated)

    def delete(self, category_id: int) -> None:
        category = self.repository.get_by_id(category_id)
        if not category:
            raise ResourceNotFoundException("Facility Category", category_id)
        self.repository.delete(category)
