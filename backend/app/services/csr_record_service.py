"""
CSR Record Service (BRSR Section C, Principle 8)
Manages CSR spend/project records and derives comparison figures --
never stores them, same discipline as PAT SEC / water-waste totals.
"""
from __future__ import annotations
from app.repositories.csr_record_repository import CsrRecordRepository
from app.models.csr_record import CsrRecord, CsrProject


class CsrRecordService:
    def __init__(self, db, organization_id: int):
        self.organization_id = organization_id
        self.repo = CsrRecordRepository(db, organization_id)

    # ---- Records ----

    def create_record(self, data: dict) -> dict:
        record = CsrRecord(organization_id=self.organization_id, **data)
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

    def _serialize(self, record: CsrRecord) -> dict:
        percent_spent = None
        if record.csr_budget_inr and record.csr_budget_inr > 0 and record.csr_amount_spent_inr is not None:
            percent_spent = round(
                float(record.csr_amount_spent_inr) / float(record.csr_budget_inr) * 100, 2
            )
        total_project_spend = sum(
            (p.amount_spent_inr or 0) for p in record.projects
        ) or None

        return {
            "id": record.id,
            "organization_id": record.organization_id,
            "reporting_year": record.reporting_year,
            "csr_budget_inr": record.csr_budget_inr,
            "csr_amount_spent_inr": record.csr_amount_spent_inr,
            "csr_admin_overhead_inr": record.csr_admin_overhead_inr,
            "remarks": record.remarks,
            "percent_spent_vs_budget": percent_spent,
            "total_project_spend_inr": total_project_spend,
            "projects": [self._serialize_project(p) for p in record.projects],
            "created_at": record.created_at,
            "updated_at": record.updated_at,
        }

    def _serialize_project(self, project: CsrProject) -> dict:
        return {
            "id": project.id,
            "csr_record_id": project.csr_record_id,
            "project_name": project.project_name,
            "activity_category": project.activity_category,
            "location": project.location,
            "is_local_area": project.is_local_area,
            "amount_spent_inr": project.amount_spent_inr,
            "direct_beneficiaries_count": project.direct_beneficiaries_count,
            "remarks": project.remarks,
            "created_at": project.created_at,
            "updated_at": project.updated_at,
        }

    # ---- Projects ----

    def create_project(self, record_id: int, data: dict) -> dict | None:
        record = self.repo.get_by_id(record_id)
        if record is None:
            return None
        project = CsrProject(csr_record_id=record_id, **data)
        project = self.repo.create_project(project)
        return self._serialize_project(project)

    def update_project(self, project_id: int, data: dict) -> dict | None:
        project = self.repo.get_project_by_id(project_id)
        if project is None:
            return None
        project = self.repo.update_project(project, data)
        return self._serialize_project(project)

    def delete_project(self, project_id: int) -> bool:
        project = self.repo.get_project_by_id(project_id)
        if project is None:
            return False
        self.repo.delete_project(project)
        return True
