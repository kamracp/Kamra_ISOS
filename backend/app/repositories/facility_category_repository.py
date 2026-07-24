from sqlalchemy.orm import Session

from app.models.facility_category import FacilityCategory
from app.schemas.facility_category import FacilityCategoryCreate, FacilityCategoryUpdate


class FacilityCategoryRepository:
    def __init__(self, db: Session, organization_id: int):
        self.db = db
        self.organization_id = organization_id

    def _base_query(self):
        return self.db.query(FacilityCategory).filter(
            FacilityCategory.organization_id == self.organization_id,
        )

    def get_by_segment(self, segment: str) -> list[FacilityCategory]:
        return (
            self._base_query()
            .filter(FacilityCategory.segment == segment)
            .order_by(FacilityCategory.display_order.asc(), FacilityCategory.id.asc())
            .all()
        )

    def get_by_id(self, category_id: int) -> FacilityCategory | None:
        return self._base_query().filter(FacilityCategory.id == category_id).first()

    def create(self, data: FacilityCategoryCreate) -> FacilityCategory:
        db_category = FacilityCategory(**data.model_dump(), organization_id=self.organization_id)
        self.db.add(db_category)
        self.db.commit()
        self.db.refresh(db_category)
        return db_category

    def update(self, db_category: FacilityCategory, data: FacilityCategoryUpdate) -> FacilityCategory:
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_category, key, value)
        self.db.commit()
        self.db.refresh(db_category)
        return db_category

    def delete(self, db_category: FacilityCategory) -> None:
        self.db.delete(db_category)
        self.db.commit()
