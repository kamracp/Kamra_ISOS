from sqlalchemy.orm import Session
from app.models.manufacturing_electricity_record import ManufacturingElectricityRecord
from app.schemas.manufacturing_electricity_record import (
    ManufacturingElectricityRecordCreate,
    ManufacturingElectricityRecordUpdate,
)


class ManufacturingElectricityRecordRepository:
    """All queries are scoped to a single organization (tenant)."""

    def __init__(self, db: Session, organization_id: int):
        self.db = db
        self.organization_id = organization_id

    def _base_query(self):
        return self.db.query(ManufacturingElectricityRecord).filter(
            ManufacturingElectricityRecord.organization_id == self.organization_id,
        )

    def get_all(self, year: int | None = None) -> list[ManufacturingElectricityRecord]:
        """All records for this org, optionally scoped to one calendar
        year (matched against period_start) -- mirrors
        ManufacturingEmissionRecordRepository's filtering pattern.
        """
        query = self._base_query()
        if year is not None:
            query = query.filter(
                ManufacturingElectricityRecord.period_start >= f"{year}-01-01",
                ManufacturingElectricityRecord.period_start <= f"{year}-12-31",
            )
        return query.order_by(ManufacturingElectricityRecord.period_start.asc()).all()

    def get_by_unit(
        self, manufacturing_unit_id: int, year: int | None = None
    ) -> list[ManufacturingElectricityRecord]:
        query = self._base_query().filter(
            ManufacturingElectricityRecord.manufacturing_unit_id == manufacturing_unit_id
        )
        if year is not None:
            query = query.filter(
                ManufacturingElectricityRecord.period_start >= f"{year}-01-01",
                ManufacturingElectricityRecord.period_start <= f"{year}-12-31",
            )
        return query.order_by(ManufacturingElectricityRecord.period_start.asc()).all()

    def get_by_id(self, record_id: int) -> ManufacturingElectricityRecord | None:
        return self._base_query().filter(ManufacturingElectricityRecord.id == record_id).first()

    def create(
        self, data: ManufacturingElectricityRecordCreate
    ) -> ManufacturingElectricityRecord:
        db_record = ManufacturingElectricityRecord(
            **data.model_dump(), organization_id=self.organization_id
        )
        self.db.add(db_record)
        self.db.commit()
        self.db.refresh(db_record)
        return db_record

    def update(
        self,
        db_record: ManufacturingElectricityRecord,
        data: ManufacturingElectricityRecordUpdate,
    ) -> ManufacturingElectricityRecord:
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_record, key, value)
        self.db.commit()
        self.db.refresh(db_record)
        return db_record

    def delete(self, db_record: ManufacturingElectricityRecord) -> None:
        self.db.delete(db_record)
        self.db.commit()
