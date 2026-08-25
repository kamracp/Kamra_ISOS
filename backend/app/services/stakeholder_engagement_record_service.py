"""
Stakeholder Engagement Record Service (BRSR Section C, Principle 4)
Manages stakeholder group identification and consultation-process
disclosures. No derived totals -- stakeholder groups are a plain list,
same as trade associations (P7), nothing to compute.
"""
from __future__ import annotations
from app.repositories.stakeholder_engagement_record_repository import StakeholderEngagementRecordRepository
from app.models.stakeholder_engagement_record import StakeholderEngagementRecord, StakeholderGroup


class StakeholderEngagementRecordService:
    def __init__(self, db, organization_id: int):
        self.organization_id = organization_id
        self.repo = StakeholderEngagementRecordRepository(db, organization_id)

    # ---- Records ----

    def create_record(self, data: dict) -> dict:
        record = StakeholderEngagementRecord(organization_id=self.organization_id, **data)
        record = self.repo.create(record)
        return self._serialize(record)

    def list_records(self) -> list[dict]:
        return [self._serialize(r) for r in self.repo.get_all()]

    def get_record(self, record_id: int) -> dict | None:
        record = self.repo.get_by_id(record_id)
        return self._serialize(record) if record else None

    def get_by_year(self, year: int) -> dict | None:
        record = self.repo.get_by_year(year)
        return self._serialize(record) if record else None

    def update_record(self, record_id: int, data: dict) -> dict | None:
        record = self.repo.get_by_id(record_id)
        if record is None:
            return None
        record = self.repo.update(record, data)
        return self._serialize(record)

    def delete_record(self, record_id: int) -> bool:
        record = self.repo.get_by_id(record_id)
        if record is None:
            return False
        self.repo.delete(record)
        return True

    def _serialize(self, record: StakeholderEngagementRecord) -> dict:
        return {
            "id": record.id,
            "organization_id": record.organization_id,
            "reporting_year": record.reporting_year,
            "has_consultation_process": record.has_consultation_process,
            "consultation_process_details": record.consultation_process_details,
            "resulted_in_policy_change": record.resulted_in_policy_change,
            "policy_change_details": record.policy_change_details,
            "remarks": record.remarks,
            "stakeholder_groups": [self._serialize_group(g) for g in record.stakeholder_groups],
            "created_at": record.created_at,
            "updated_at": record.updated_at,
        }

    def _serialize_group(self, group: StakeholderGroup) -> dict:
        return {
            "id": group.id,
            "engagement_record_id": group.engagement_record_id,
            "group_name": group.group_name,
            "is_vulnerable_marginalized": group.is_vulnerable_marginalized,
            "communication_channels": group.communication_channels,
            "frequency_of_engagement": group.frequency_of_engagement,
            "purpose_and_scope": group.purpose_and_scope,
            "remarks": group.remarks,
            "created_at": group.created_at,
            "updated_at": group.updated_at,
        }

    # ---- Stakeholder groups ----

    def create_group(self, record_id: int, data: dict) -> dict | None:
        record = self.repo.get_by_id(record_id)
        if record is None:
            return None
        group = StakeholderGroup(engagement_record_id=record_id, **data)
        group = self.repo.create_group(group)
        return self._serialize_group(group)

    def update_group(self, group_id: int, data: dict) -> dict | None:
        group = self.repo.get_group_by_id(group_id)
        if group is None:
            return None
        group = self.repo.update_group(group, data)
        return self._serialize_group(group)

    def delete_group(self, group_id: int) -> bool:
        group = self.repo.get_group_by_id(group_id)
        if group is None:
            return False
        self.repo.delete_group(group)
        return True
