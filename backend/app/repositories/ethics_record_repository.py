"""Repository for EthicsRecord -- tenant-scoped via organization_id."""
from __future__ import annotations
from sqlalchemy.orm import Session
from app.models.ethics_record import EthicsRecord


class EthicsRecordRepository:
    def __init__(self, db: Session, organization_id: int):
        self.db = db
        self.organization_id = organization_id

    def _base_query(self):
        return self.db.query(EthicsRecord).filter(
            EthicsRecord.organization_id == self.organization_id
        )

    def get_all(self) -> list[EthicsRecord]:
        return self._base_query().order_by(EthicsRecord.reporting_year.desc()).all()

    def get_by_id(self, record_id: int) -> EthicsRecord | None:
        return self._base_query().filter(EthicsRecord.id == record_id).first()

    def get_by_year(self, year: int) -> EthicsRecord | None:
        return self._base_query().filter(EthicsRecord.reporting_year == year).first()

    def create(self, record: EthicsRecord) -> EthicsRecord:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def update(self, record: EthicsRecord, data: dict) -> EthicsRecord:
        for key, value in data.items():
            setattr(record, key, value)
        self.db.commit()
        self.db.refresh(record)
        return record

    def delete(self, record: EthicsRecord) -> None:
        self.db.delete(record)
        self.db.commit()
