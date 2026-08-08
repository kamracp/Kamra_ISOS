from sqlalchemy.orm import Session

from app.models.manufacturing_emission_record import ManufacturingEmissionRecord
from app.schemas.manufacturing_emission_record import (
    ManufacturingEmissionRecordCreate,
    ManufacturingEmissionRecordUpdate,
)


class ManufacturingEmissionRecordRepository:
    """All queries are scoped to a single organization (tenant)."""

    def __init__(self, db: Session, organization_id: int):
        self.db = db
        self.organization_id = organization_id

    def _base_query(self):
        return self.db.query(ManufacturingEmissionRecord).filter(
            ManufacturingEmissionRecord.organization_id == self.organization_id,
        )

    def get_all(self, year: int | None = None) -> list[ManufacturingEmissionRecord]:
        """All records for this org, optionally scoped to one calendar
        year (matched against period_start) -- mirrors CarbonService's
        get_summary(year=...) filtering pattern for consistency across
        both BENAS and ManufactureOS summaries.
        """
        query = self._base_query()
        if year is not None:
            query = query.filter(
                ManufacturingEmissionRecord.period_start >= f"{year}-01-01",
                ManufacturingEmissionRecord.period_start <= f"{year}-12-31",
            )
        return query.order_by(ManufacturingEmissionRecord.period_start.asc()).all()

    def get_by_unit(
        self, manufacturing_unit_id: int, year: int | None = None
    ) -> list[ManufacturingEmissionRecord]:
        query = self._base_query().filter(
            ManufacturingEmissionRecord.manufacturing_unit_id == manufacturing_unit_id
        )
        if year is not None:
            query = query.filter(
                ManufacturingEmissionRecord.period_start >= f"{year}-01-01",
                ManufacturingEmissionRecord.period_start <= f"{year}-12-31",
            )
        return query.order_by(ManufacturingEmissionRecord.period_start.asc()).all()

    def get_by_id(self, record_id: int) -> ManufacturingEmissionRecord | None:
        return self._base_query().filter(ManufacturingEmissionRecord.id == record_id).first()

    def create(
        self, data: ManufacturingEmissionRecordCreate
    ) -> ManufacturingEmissionRecord:
        db_record = ManufacturingEmissionRecord(
            **data.model_dump(), organization_id=self.organization_id
        )
        self.db.add(db_record)
        self.db.commit()
        self.db.refresh(db_record)
        return db_record

    def update(
        self,
        db_record: ManufacturingEmissionRecord,
        data: ManufacturingEmissionRecordUpdate,
    ) -> ManufacturingEmissionRecord:
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_record, key, value)
        self.db.commit()
        self.db.refresh(db_record)
        return db_record

    def delete(self, db_record: ManufacturingEmissionRecord) -> None:
        self.db.delete(db_record)
        self.db.commit()
