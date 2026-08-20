from datetime import date

from sqlalchemy.orm import Session

from app.models.waste_record import WasteRecord
from app.schemas.waste_record import WasteRecordCreate, WasteRecordUpdate


class WasteRecordRepository:
    """Tenant-scoped data access for BRSR P6 waste records."""

    def __init__(self, db: Session, organization_id: int):
        self.db = db
        self.organization_id = organization_id

    def _base_query(self):
        return self.db.query(WasteRecord).filter(
            WasteRecord.organization_id == self.organization_id,
        )

    def get_all(self, year: int | None = None) -> list[WasteRecord]:
        """Newest first. `year` matches records whose period starts in it."""
        query = self._base_query()
        if year is not None:
            query = query.filter(
                WasteRecord.period_start >= date(year, 1, 1),
                WasteRecord.period_start <= date(year, 12, 31),
            )
        return query.order_by(WasteRecord.period_start.desc()).all()

    def get_by_id(self, record_id: int) -> WasteRecord | None:
        return self._base_query().filter(WasteRecord.id == record_id).first()

    def create(self, data: WasteRecordCreate) -> WasteRecord:
        db_record = WasteRecord(
            **data.model_dump(), organization_id=self.organization_id
        )
        self.db.add(db_record)
        self.db.commit()
        self.db.refresh(db_record)
        return db_record

    def update(
        self, db_record: WasteRecord, data: WasteRecordUpdate
    ) -> WasteRecord:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(db_record, field, value)
        self.db.commit()
        self.db.refresh(db_record)
        return db_record

    def delete(self, db_record: WasteRecord) -> None:
        self.db.delete(db_record)
        self.db.commit()
