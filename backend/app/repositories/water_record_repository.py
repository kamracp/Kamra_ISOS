from datetime import date

from sqlalchemy.orm import Session

from app.models.water_record import WaterRecord
from app.schemas.water_record import WaterRecordCreate, WaterRecordUpdate


class WaterRecordRepository:
    """Tenant-scoped data access for BRSR P6 water records."""

    def __init__(self, db: Session, organization_id: int):
        self.db = db
        self.organization_id = organization_id

    def _base_query(self):
        return self.db.query(WaterRecord).filter(
            WaterRecord.organization_id == self.organization_id,
        )

    def get_all(self, year: int | None = None) -> list[WaterRecord]:
        """
        Records ordered newest first. `year` selects records whose period
        STARTS within that calendar year - the same convention
        UtilityBillRepository uses, so a report year means the same thing
        across the platform.
        """
        query = self._base_query()
        if year is not None:
            query = query.filter(
                WaterRecord.period_start >= date(year, 1, 1),
                WaterRecord.period_start <= date(year, 12, 31),
            )
        return query.order_by(WaterRecord.period_start.desc()).all()

    def get_by_id(self, record_id: int) -> WaterRecord | None:
        return self._base_query().filter(WaterRecord.id == record_id).first()

    def create(self, data: WaterRecordCreate) -> WaterRecord:
        db_record = WaterRecord(
            **data.model_dump(), organization_id=self.organization_id
        )
        self.db.add(db_record)
        self.db.commit()
        self.db.refresh(db_record)
        return db_record

    def update(
        self, db_record: WaterRecord, data: WaterRecordUpdate
    ) -> WaterRecord:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(db_record, field, value)
        self.db.commit()
        self.db.refresh(db_record)
        return db_record

    def delete(self, db_record: WaterRecord) -> None:
        self.db.delete(db_record)
        self.db.commit()
