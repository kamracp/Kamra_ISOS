from sqlalchemy.orm import Session, selectinload

from app.models.scope3_activity_record import Scope3ActivityRecord
from app.schemas.scope3 import Scope3RecordCreate, Scope3RecordUpdate


class Scope3Repository:
    """Tenant-scoped access to scope3_activity_records."""

    def __init__(self, db: Session, organization_id: int):
        self.db = db
        self.organization_id = organization_id

    def _base_query(self):
        return (self.db.query(Scope3ActivityRecord)
                .options(selectinload(Scope3ActivityRecord.emission_factor))
                .filter(Scope3ActivityRecord.organization_id == self.organization_id))

    def get_all(self, year: int | None = None, category: int | None = None) -> list[Scope3ActivityRecord]:
        q = self._base_query()
        if year is not None:
            q = q.filter(Scope3ActivityRecord.year == year)
        if category is not None:
            q = q.filter(Scope3ActivityRecord.category == category)
        return q.order_by(Scope3ActivityRecord.year.desc(), Scope3ActivityRecord.category, Scope3ActivityRecord.id).all()

    def get_by_id(self, record_id: int) -> Scope3ActivityRecord | None:
        return self._base_query().filter(Scope3ActivityRecord.id == record_id).first()

    def create(self, data: Scope3RecordCreate) -> Scope3ActivityRecord:
        obj = Scope3ActivityRecord(organization_id=self.organization_id, **data.model_dump())
        self.db.add(obj); self.db.commit(); self.db.refresh(obj)
        return obj

    def update(self, obj: Scope3ActivityRecord, data: Scope3RecordUpdate) -> Scope3ActivityRecord:
        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(obj, k, v)
        self.db.commit(); self.db.refresh(obj)
        return obj

    def delete(self, obj: Scope3ActivityRecord) -> None:
        self.db.delete(obj); self.db.commit()
