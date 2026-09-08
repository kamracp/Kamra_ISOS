"""Repository for HumanRightsRecord + its three child tables --
tenant-scoped via organization_id (BRSR Principle 5)."""
from __future__ import annotations
from sqlalchemy.orm import Session, joinedload
from app.models.human_rights_record import (
    HumanRightsRecord,
    HumanRightsWorkforceCoverage,
    HumanRightsRemuneration,
    HumanRightsComplaint,
)

# Child model classes keyed by the name used in service/API paths.
CHILD_MODELS = {
    "workforce": HumanRightsWorkforceCoverage,
    "remuneration": HumanRightsRemuneration,
    "complaint": HumanRightsComplaint,
}


class HumanRightsRecordRepository:
    def __init__(self, db: Session, organization_id: int):
        self.db = db
        self.organization_id = organization_id

    def _base_query(self):
        # The ONE place the tenant filter lives for parent reads.
        return (
            self.db.query(HumanRightsRecord)
            .options(
                joinedload(HumanRightsRecord.workforce_coverage),
                joinedload(HumanRightsRecord.remuneration),
                joinedload(HumanRightsRecord.complaints),
            )
            .filter(HumanRightsRecord.organization_id == self.organization_id)
        )

    def get_all(self) -> list[HumanRightsRecord]:
        return self._base_query().order_by(HumanRightsRecord.reporting_year.desc()).all()

    def get_by_id(self, record_id: int) -> HumanRightsRecord | None:
        return self._base_query().filter(HumanRightsRecord.id == record_id).first()

    def get_by_year(self, year: int) -> HumanRightsRecord | None:
        return self._base_query().filter(HumanRightsRecord.reporting_year == year).first()

    def create(self, record: HumanRightsRecord) -> HumanRightsRecord:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def update(self, record: HumanRightsRecord, data: dict) -> HumanRightsRecord:
        for key, value in data.items():
            setattr(record, key, value)
        self.db.commit()
        self.db.refresh(record)
        return record

    def delete(self, record: HumanRightsRecord) -> None:
        self.db.delete(record)
        self.db.commit()

    # ---- Children: one generic path for all three tables. The join to
    # the parent applies the tenant filter, so a child id from another
    # organization is simply not found. ----
    def get_child_by_id(self, kind: str, child_id: int):
        model = CHILD_MODELS[kind]
        return (
            self.db.query(model)
            .join(HumanRightsRecord)
            .filter(model.id == child_id, HumanRightsRecord.organization_id == self.organization_id)
            .first()
        )

    def create_child(self, child):
        self.db.add(child)
        self.db.commit()
        self.db.refresh(child)
        return child

    def update_child(self, child, data: dict):
        for key, value in data.items():
            setattr(child, key, value)
        self.db.commit()
        self.db.refresh(child)
        return child

    def delete_child(self, child) -> None:
        self.db.delete(child)
        self.db.commit()
