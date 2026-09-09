from sqlalchemy.orm import Session
from app.models.manufacturing_fuel_record import ManufacturingFuelRecord
from app.schemas.manufacturing_fuel_record import (
    ManufacturingFuelRecordCreate,
    ManufacturingFuelRecordUpdate,
)


class ManufacturingFuelRecordRepository:
    """All queries are scoped to a single organization (tenant)."""

    def __init__(self, db: Session, organization_id: int):
        self.db = db
        self.organization_id = organization_id

    def _base_query(self):
        return self.db.query(ManufacturingFuelRecord).filter(
            ManufacturingFuelRecord.organization_id == self.organization_id,
        )

    def get_all(self, year: int | None = None) -> list[ManufacturingFuelRecord]:
        """All records for this org, optionally scoped to one calendar
        year (matched against period_start) -- mirrors
        ManufacturingEmissionRecordRepository's filtering pattern.
        """
        query = self._base_query()
        if year is not None:
            query = query.filter(
                ManufacturingFuelRecord.period_start >= f"{year}-01-01",
                ManufacturingFuelRecord.period_start <= f"{year}-12-31",
            )
        return query.order_by(ManufacturingFuelRecord.period_start.asc()).all()

    def get_by_unit(
        self, manufacturing_unit_id: int, year: int | None = None
    ) -> list[ManufacturingFuelRecord]:
        query = self._base_query().filter(
            ManufacturingFuelRecord.manufacturing_unit_id == manufacturing_unit_id
        )
        if year is not None:
            query = query.filter(
                ManufacturingFuelRecord.period_start >= f"{year}-01-01",
                ManufacturingFuelRecord.period_start <= f"{year}-12-31",
            )
        return query.order_by(ManufacturingFuelRecord.period_start.asc()).all()

    def get_by_id(self, record_id: int) -> ManufacturingFuelRecord | None:
        return self._base_query().filter(ManufacturingFuelRecord.id == record_id).first()

    def create(
        self, data: ManufacturingFuelRecordCreate
    ) -> ManufacturingFuelRecord:
        db_record = ManufacturingFuelRecord(
            **data.model_dump(), organization_id=self.organization_id
        )
        self.db.add(db_record)
        self.db.commit()
        self.db.refresh(db_record)
        return db_record

    def update(
        self,
        db_record: ManufacturingFuelRecord,
        data: ManufacturingFuelRecordUpdate,
    ) -> ManufacturingFuelRecord:
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_record, key, value)
        self.db.commit()
        self.db.refresh(db_record)
        return db_record

    def delete(self, db_record: ManufacturingFuelRecord) -> None:
        self.db.delete(db_record)
        self.db.commit()
