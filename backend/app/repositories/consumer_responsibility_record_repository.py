"""Repository for ConsumerResponsibilityRecord + ConsumerComplaint -- tenant-scoped (BRSR Principle 9)."""
from __future__ import annotations
from sqlalchemy.orm import Session, joinedload
from app.models.consumer_responsibility_record import ConsumerResponsibilityRecord, ConsumerComplaint


class ConsumerResponsibilityRecordRepository:
    def __init__(self, db: Session, organization_id: int):
        self.db = db
        self.organization_id = organization_id

    def _base_query(self):
        return (
            self.db.query(ConsumerResponsibilityRecord)
            .options(joinedload(ConsumerResponsibilityRecord.complaints))
            .filter(ConsumerResponsibilityRecord.organization_id == self.organization_id)
        )

    def get_all(self):
        return self._base_query().order_by(ConsumerResponsibilityRecord.reporting_year.desc()).all()

    def get_by_id(self, record_id: int):
        return self._base_query().filter(ConsumerResponsibilityRecord.id == record_id).first()

    def get_by_year(self, year: int):
        return self._base_query().filter(ConsumerResponsibilityRecord.reporting_year == year).first()

    def create(self, record):
        self.db.add(record); self.db.commit(); self.db.refresh(record); return record

    def update(self, record, data: dict):
        for k, v in data.items(): setattr(record, k, v)
        self.db.commit(); self.db.refresh(record); return record

    def delete(self, record) -> None:
        self.db.delete(record); self.db.commit()

    def get_complaint_by_id(self, complaint_id: int):
        return (
            self.db.query(ConsumerComplaint).join(ConsumerResponsibilityRecord)
            .filter(ConsumerComplaint.id == complaint_id,
                    ConsumerResponsibilityRecord.organization_id == self.organization_id)
            .first()
        )

    def create_complaint(self, complaint):
        self.db.add(complaint); self.db.commit(); self.db.refresh(complaint); return complaint

    def update_complaint(self, complaint, data: dict):
        for k, v in data.items(): setattr(complaint, k, v)
        self.db.commit(); self.db.refresh(complaint); return complaint

    def delete_complaint(self, complaint) -> None:
        self.db.delete(complaint); self.db.commit()
