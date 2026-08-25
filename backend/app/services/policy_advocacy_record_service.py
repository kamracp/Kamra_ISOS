"""
Policy Advocacy Record Service (BRSR Section C, Principle 7)
Manages trade/industry association memberships and anti-competitive
conduct disclosures. No derived totals here (unlike CSR/PAT SEC) --
associations are a plain membership list, nothing to compute.
"""
from __future__ import annotations
from app.repositories.policy_advocacy_record_repository import PolicyAdvocacyRecordRepository
from app.models.policy_advocacy_record import PolicyAdvocacyRecord, TradeAssociation


class PolicyAdvocacyRecordService:
    def __init__(self, db, organization_id: int):
        self.organization_id = organization_id
        self.repo = PolicyAdvocacyRecordRepository(db, organization_id)

    # ---- Records ----

    def create_record(self, data: dict) -> dict:
        record = PolicyAdvocacyRecord(organization_id=self.organization_id, **data)
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

    def _serialize(self, record: PolicyAdvocacyRecord) -> dict:
        return {
            "id": record.id,
            "organization_id": record.organization_id,
            "reporting_year": record.reporting_year,
            "has_anti_competitive_conduct_issue": record.has_anti_competitive_conduct_issue,
            "anti_competitive_conduct_details": record.anti_competitive_conduct_details,
            "corrective_action_taken": record.corrective_action_taken,
            "remarks": record.remarks,
            "associations": [self._serialize_association(a) for a in record.associations],
            "created_at": record.created_at,
            "updated_at": record.updated_at,
        }

    def _serialize_association(self, association: TradeAssociation) -> dict:
        return {
            "id": association.id,
            "policy_advocacy_record_id": association.policy_advocacy_record_id,
            "association_name": association.association_name,
            "reach": association.reach,
            "remarks": association.remarks,
            "created_at": association.created_at,
            "updated_at": association.updated_at,
        }

    # ---- Associations ----

    def create_association(self, record_id: int, data: dict) -> dict | None:
        record = self.repo.get_by_id(record_id)
        if record is None:
            return None
        association = TradeAssociation(policy_advocacy_record_id=record_id, **data)
        association = self.repo.create_association(association)
        return self._serialize_association(association)

    def update_association(self, association_id: int, data: dict) -> dict | None:
        association = self.repo.get_association_by_id(association_id)
        if association is None:
            return None
        association = self.repo.update_association(association, data)
        return self._serialize_association(association)

    def delete_association(self, association_id: int) -> bool:
        association = self.repo.get_association_by_id(association_id)
        if association is None:
            return False
        self.repo.delete_association(association)
        return True
