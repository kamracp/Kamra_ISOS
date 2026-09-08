"""
Employee Well-being Record Service (BRSR Section C, Principle 3)

One record per organization per reporting year + four child tables.
Derived on read, never stored: per-benefit coverage % (EI 1), training /
review % (EI 8-9), union membership % (EI 7), complaint totals (EI 13).
A percent is None unless both counts are present and total > 0.
"""
from __future__ import annotations
from decimal import Decimal
from app.repositories.employee_wellbeing_record_repository import EmployeeWellbeingRecordRepository, CHILD_MODELS
from app.models.employee_wellbeing_record import EmployeeWellbeingRecord
from app.schemas.employee_wellbeing_record import EmployeeWellbeingFields
from app.services.sustainable_product_record_service import DuplicateReportingYear  # noqa: F401

# Parent scalar fields come straight from the schema so the two cannot drift.
RECORD_FIELDS = ("reporting_year", *EmployeeWellbeingFields.model_fields.keys())

CHILD_FIELDS = {
    "measure": ("category", "total_count", "health_insurance", "accident_insurance",
                "maternity_benefits", "paternity_benefits", "day_care_facilities", "remarks"),
    "parental": ("category", "return_to_work_rate_percent", "retention_rate_percent", "remarks"),
    "training": ("category", "total_count", "health_safety_trained", "skill_upgraded", "performance_reviewed", "remarks"),
    "complaint": ("category", "filed_count", "pending_count", "remarks"),
}
CHILD_RELATION = {"measure": "wellbeing_measures", "parental": "parental_leave", "training": "training", "complaint": "complaints"}
# Count columns that get a derived "<col>_percent" against total_count.
CHILD_PCT_OF_TOTAL = {
    "measure": ("health_insurance", "accident_insurance", "maternity_benefits", "paternity_benefits", "day_care_facilities"),
    "training": ("health_safety_trained", "skill_upgraded", "performance_reviewed"),
}


def _num(v):
    return float(v) if isinstance(v, Decimal) else v


def _pct(part, whole):
    if part is None or whole is None or whole <= 0:
        return None
    return round(float(part) / float(whole) * 100, 2)


def _sum_field(rows, field):
    vals = [getattr(r, field) for r in rows if getattr(r, field) is not None]
    return sum(vals) if vals else None


class EmployeeWellbeingRecordService:
    def __init__(self, db, organization_id: int):
        self.organization_id = organization_id
        self.repo = EmployeeWellbeingRecordRepository(db, organization_id)

    def create_record(self, data: dict) -> dict:
        if self.repo.get_by_year(data["reporting_year"]) is not None:
            raise DuplicateReportingYear(data["reporting_year"])
        return self._serialize(self.repo.create(EmployeeWellbeingRecord(organization_id=self.organization_id, **data)))

    def list_records(self):
        return [self._serialize(r) for r in self.repo.get_all()]

    def get_record(self, record_id: int):
        r = self.repo.get_by_id(record_id)
        return self._serialize(r) if r else None

    def get_by_year(self, year: int):
        r = self.repo.get_by_year(year)
        return self._serialize(r) if r else None

    def update_record(self, record_id: int, data: dict):
        r = self.repo.get_by_id(record_id)
        if r is None:
            return None
        ny = data.get("reporting_year")
        if ny is not None and ny != r.reporting_year and self.repo.get_by_year(ny) is not None:
            raise DuplicateReportingYear(ny)
        return self._serialize(self.repo.update(r, data))

    def delete_record(self, record_id: int) -> bool:
        r = self.repo.get_by_id(record_id)
        if r is None:
            return False
        self.repo.delete(r)
        return True

    def create_child(self, kind: str, record_id: int, data: dict):
        if self.repo.get_by_id(record_id) is None:
            return None
        return self._serialize_child(kind, self.repo.create_child(CHILD_MODELS[kind](employee_wellbeing_record_id=record_id, **data)))

    def update_child(self, kind: str, child_id: int, data: dict):
        c = self.repo.get_child_by_id(kind, child_id)
        return self._serialize_child(kind, self.repo.update_child(c, data)) if c else None

    def delete_child(self, kind: str, child_id: int) -> bool:
        c = self.repo.get_child_by_id(kind, child_id)
        if c is None:
            return False
        self.repo.delete_child(c)
        return True

    def _serialize(self, r) -> dict:
        out = {"id": r.id, "organization_id": r.organization_id}
        for f in RECORD_FIELDS:
            out[f] = _num(getattr(r, f))
        for kind, rel in CHILD_RELATION.items():
            out[rel] = [self._serialize_child(kind, c) for c in getattr(r, rel)]
        out["permanent_employees_union_percent"] = _pct(r.permanent_employees_union_members, r.permanent_employees_total)
        out["permanent_workers_union_percent"] = _pct(r.permanent_workers_union_members, r.permanent_workers_total)
        out["total_complaints_filed"] = _sum_field(r.complaints, "filed_count")
        out["total_complaints_pending"] = _sum_field(r.complaints, "pending_count")
        out["created_at"] = r.created_at
        out["updated_at"] = r.updated_at
        return out

    def _serialize_child(self, kind: str, c) -> dict:
        out = {"id": c.id, "employee_wellbeing_record_id": c.employee_wellbeing_record_id}
        for f in CHILD_FIELDS[kind]:
            out[f] = _num(getattr(c, f))
        for f in CHILD_PCT_OF_TOTAL.get(kind, ()):
            out[f"{f}_percent"] = _pct(getattr(c, f), c.total_count)
        out["created_at"] = c.created_at
        out["updated_at"] = c.updated_at
        return out
