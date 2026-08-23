"""Repository for EnergyProductionRecord -- tenant-scoped via organization_id."""
from __future__ import annotations
from sqlalchemy import select, extract
from sqlalchemy.orm import Session
from app.models.energy_production_record import EnergyProductionRecord


class EnergyProductionRecordRepository:
    def __init__(self, db: Session, organization_id: int):
        self.db = db
        self.organization_id = organization_id

    def _base_query(self):
        return select(EnergyProductionRecord).where(
            EnergyProductionRecord.organization_id == self.organization_id
        )

    def get_by_id(self, record_id: int) -> EnergyProductionRecord | None:
        stmt = self._base_query().where(EnergyProductionRecord.id == record_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_unit(
        self, manufacturing_unit_id: int, year: int | None = None
    ) -> list[EnergyProductionRecord]:
        stmt = self._base_query().where(
            EnergyProductionRecord.manufacturing_unit_id == manufacturing_unit_id
        )
        if year is not None:
            # Same convention platform-wide: reporting year = period_start's year.
            stmt = stmt.where(extract("year", EnergyProductionRecord.period_start) == year)
        return list(self.db.execute(stmt).scalars().all())

    def create(self, record: EnergyProductionRecord) -> EnergyProductionRecord:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def update(self, record: EnergyProductionRecord, data: dict) -> EnergyProductionRecord:
        for key, value in data.items():
            setattr(record, key, value)
        self.db.commit()
        self.db.refresh(record)
        return record

    def delete(self, record: EnergyProductionRecord) -> None:
        self.db.delete(record)
        self.db.commit()
