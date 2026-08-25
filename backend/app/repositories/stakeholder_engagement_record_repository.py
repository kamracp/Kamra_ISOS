"""Repository for StakeholderEngagementRecord + StakeholderGroup -- tenant-scoped via organization_id."""
from __future__ import annotations
from sqlalchemy.orm import Session, joinedload
from app.models.stakeholder_engagement_record import StakeholderEngagementRecord, StakeholderGroup


class StakeholderEngagementRecordRepository:
    def __init__(self, db: Session, organization_id: int):
        self.db = db
        self.organization_id = organization_id

    def _base_query(self):
        return (
            self.db.query(StakeholderEngagementRecord)
            .options(joinedload(StakeholderEngagementRecord.stakeholder_groups))
            .filter(StakeholderEngagementRecord.organization_id == self.organization_id)
        )

    def get_all(self) -> list[StakeholderEngagementRecord]:
        return self._base_query().order_by(StakeholderEngagementRecord.reporting_year.desc()).all()

    def get_by_id(self, record_id: int) -> StakeholderEngagementRecord | None:
        return self._base_query().filter(StakeholderEngagementRecord.id == record_id).first()

    def get_by_year(self, year: int) -> StakeholderEngagementRecord | None:
        return self._base_query().filter(StakeholderEngagementRecord.reporting_year == year).first()

    def create(self, record: StakeholderEngagementRecord) -> StakeholderEngagementRecord:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def update(self, record: StakeholderEngagementRecord, data: dict) -> StakeholderEngagementRecord:
        for key, value in data.items():
            setattr(record, key, value)
        self.db.commit()
        self.db.refresh(record)
        return record

    def delete(self, record: StakeholderEngagementRecord) -> None:
        self.db.delete(record)
        self.db.commit()

    # ---- Stakeholder groups (child of a record the caller already owns/verified) ----
    def get_group_by_id(self, group_id: int) -> StakeholderGroup | None:
        return (
            self.db.query(StakeholderGroup)
            .join(StakeholderEngagementRecord)
            .filter(
                StakeholderGroup.id == group_id,
                StakeholderEngagementRecord.organization_id == self.organization_id,
            )
            .first()
        )

    def create_group(self, group: StakeholderGroup) -> StakeholderGroup:
        self.db.add(group)
        self.db.commit()
        self.db.refresh(group)
        return group

    def update_group(self, group: StakeholderGroup, data: dict) -> StakeholderGroup:
        for key, value in data.items():
            setattr(group, key, value)
        self.db.commit()
        self.db.refresh(group)
        return group

    def delete_group(self, group: StakeholderGroup) -> None:
        self.db.delete(group)
        self.db.commit()
