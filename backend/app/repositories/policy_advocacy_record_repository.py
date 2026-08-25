"""Repository for PolicyAdvocacyRecord + TradeAssociation -- tenant-scoped via organization_id."""
from __future__ import annotations
from sqlalchemy.orm import Session, joinedload
from app.models.policy_advocacy_record import PolicyAdvocacyRecord, TradeAssociation


class PolicyAdvocacyRecordRepository:
    def __init__(self, db: Session, organization_id: int):
        self.db = db
        self.organization_id = organization_id

    def _base_query(self):
        return (
            self.db.query(PolicyAdvocacyRecord)
            .options(joinedload(PolicyAdvocacyRecord.associations))
            .filter(PolicyAdvocacyRecord.organization_id == self.organization_id)
        )

    def get_all(self) -> list[PolicyAdvocacyRecord]:
        return self._base_query().order_by(PolicyAdvocacyRecord.reporting_year.desc()).all()

    def get_by_id(self, record_id: int) -> PolicyAdvocacyRecord | None:
        return self._base_query().filter(PolicyAdvocacyRecord.id == record_id).first()

    def get_by_year(self, year: int) -> PolicyAdvocacyRecord | None:
        return self._base_query().filter(PolicyAdvocacyRecord.reporting_year == year).first()

    def create(self, record: PolicyAdvocacyRecord) -> PolicyAdvocacyRecord:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def update(self, record: PolicyAdvocacyRecord, data: dict) -> PolicyAdvocacyRecord:
        for key, value in data.items():
            setattr(record, key, value)
        self.db.commit()
        self.db.refresh(record)
        return record

    def delete(self, record: PolicyAdvocacyRecord) -> None:
        self.db.delete(record)
        self.db.commit()

    # ---- Associations (child of a record the caller already owns/verified) ----
    def get_association_by_id(self, association_id: int) -> TradeAssociation | None:
        return (
            self.db.query(TradeAssociation)
            .join(PolicyAdvocacyRecord)
            .filter(
                TradeAssociation.id == association_id,
                PolicyAdvocacyRecord.organization_id == self.organization_id,
            )
            .first()
        )

    def create_association(self, association: TradeAssociation) -> TradeAssociation:
        self.db.add(association)
        self.db.commit()
        self.db.refresh(association)
        return association

    def update_association(self, association: TradeAssociation, data: dict) -> TradeAssociation:
        for key, value in data.items():
            setattr(association, key, value)
        self.db.commit()
        self.db.refresh(association)
        return association

    def delete_association(self, association: TradeAssociation) -> None:
        self.db.delete(association)
        self.db.commit()
