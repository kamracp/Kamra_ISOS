"""Repository for EmployeeWellbeingRecord + four child tables -- tenant-scoped (BRSR Principle 3)."""
from __future__ import annotations
from sqlalchemy.orm import Session, joinedload
from app.models.employee_wellbeing_record import (
    EmployeeWellbeingRecord, EmployeeWellbeingMeasure, EmployeeWellbeingParentalLeave,
    EmployeeWellbeingTraining, EmployeeWellbeingComplaint,
)

CHILD_MODELS = {
    "measure": EmployeeWellbeingMeasure,
    "parental": EmployeeWellbeingParentalLeave,
    "training": EmployeeWellbeingTraining,
    "complaint": EmployeeWellbeingComplaint,
}


class EmployeeWellbeingRecordRepository:
    def __init__(self, db: Session, organization_id: int):
        self.db = db
        self.organization_id = organization_id

    def _base_query(self):
        return (
            self.db.query(EmployeeWellbeingRecord)
            .options(
                joinedload(EmployeeWellbeingRecord.wellbeing_measures),
                joinedload(EmployeeWellbeingRecord.parental_leave),
                joinedload(EmployeeWellbeingRecord.training),
                joinedload(EmployeeWellbeingRecord.complaints),
            )
            .filter(EmployeeWellbeingRecord.organization_id == self.organization_id)
        )

    def get_all(self):
        return self._base_query().order_by(EmployeeWellbeingRecord.reporting_year.desc()).all()

    def get_by_id(self, record_id: int):
        return self._base_query().filter(EmployeeWellbeingRecord.id == record_id).first()

    def get_by_year(self, year: int):
        return self._base_query().filter(EmployeeWellbeingRecord.reporting_year == year).first()

    def create(self, record):
        self.db.add(record); self.db.commit(); self.db.refresh(record); return record

    def update(self, record, data: dict):
        for k, v in data.items(): setattr(record, k, v)
        self.db.commit(); self.db.refresh(record); return record

    def delete(self, record) -> None:
        self.db.delete(record); self.db.commit()

    # Children -- parent join is the tenant filter.
    def get_child_by_id(self, kind: str, child_id: int):
        model = CHILD_MODELS[kind]
        return (
            self.db.query(model).join(EmployeeWellbeingRecord)
            .filter(model.id == child_id, EmployeeWellbeingRecord.organization_id == self.organization_id)
            .first()
        )

    def create_child(self, child):
        self.db.add(child); self.db.commit(); self.db.refresh(child); return child

    def update_child(self, child, data: dict):
        for k, v in data.items(): setattr(child, k, v)
        self.db.commit(); self.db.refresh(child); return child

    def delete_child(self, child) -> None:
        self.db.delete(child); self.db.commit()
