"""
Human Rights Record Service (BRSR Section C, Principle 5)

One record per organization per reporting year plus three child tables.
Derived values (training coverage %, complaint totals) are computed on
read and never stored. Coverage % is None unless both counts are present
and total > 0 -- "not disclosed" must not render as 0%.
"""
from __future__ import annotations
from decimal import Decimal
from app.repositories.human_rights_record_repository import (
    HumanRightsRecordRepository,
    CHILD_MODELS,
)
from app.models.human_rights_record import HumanRightsRecord

# Re-used by the API for its 409 mapping.
from app.services.sustainable_product_record_service import DuplicateReportingYear  # noqa: F401

RECORD_FIELDS = (
    "reporting_year",
    "has_human_rights_focal_point", "focal_point_details",
    "grievance_mechanism_details", "complainant_protection_details",
    "hr_requirements_in_contracts", "hr_requirements_details",
    "assessed_child_labour_percent", "assessed_forced_labour_percent",
    "assessed_sexual_harassment_percent", "assessed_discrimination_percent",
    "assessed_wages_percent", "assessed_other_percent", "assessed_other_description",
    "corrective_actions_from_assessments",
    "process_modifications_from_grievances", "human_rights_due_diligence_details",
    "premises_accessible_to_differently_abled", "accessibility_details",
    "value_chain_partners_assessed_percent", "value_chain_assessment_details",
    "value_chain_corrective_actions",
    "remarks",
)

CHILD_FIELDS = {
    "workforce": ("category", "total_count", "hr_training_covered",
                  "equal_min_wage_male", "equal_min_wage_female",
                  "more_than_min_wage_male", "more_than_min_wage_female", "remarks"),
    "remuneration": ("category", "male_count", "male_median_inr",
                     "female_count", "female_median_inr", "remarks"),
    "complaint": ("category", "filed_count", "pending_count", "remarks"),
}

# Relationship attribute on the parent for each child kind.
CHILD_RELATION = {"workforce": "workforce_coverage", "remuneration": "remuneration", "complaint": "complaints"}


def _num(value):
    return float(value) if isinstance(value, Decimal) else value


def _pct(part, whole) -> float | None:
    if part is None or whole is None or whole <= 0:
        return None
    return round(part / whole * 100, 2)


def _sum_field(rows, field: str) -> int | None:
    values = [getattr(r, field) for r in rows if getattr(r, field) is not None]
    return sum(values) if values else None


class HumanRightsRecordService:
    def __init__(self, db, organization_id: int):
        self.organization_id = organization_id
        self.repo = HumanRightsRecordRepository(db, organization_id)

    # ---- Records ----

    def create_record(self, data: dict) -> dict:
        if self.repo.get_by_year(data["reporting_year"]) is not None:
            raise DuplicateReportingYear(data["reporting_year"])
        record = HumanRightsRecord(organization_id=self.organization_id, **data)
        return self._serialize(self.repo.create(record))

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
        new_year = data.get("reporting_year")
        if new_year is not None and new_year != record.reporting_year:
            if self.repo.get_by_year(new_year) is not None:
                raise DuplicateReportingYear(new_year)
        return self._serialize(self.repo.update(record, data))

    def delete_record(self, record_id: int) -> bool:
        record = self.repo.get_by_id(record_id)
        if record is None:
            return False
        self.repo.delete(record)
        return True

    # ---- Children (kind in CHILD_MODELS) ----

    def create_child(self, kind: str, record_id: int, data: dict) -> dict | None:
        if self.repo.get_by_id(record_id) is None:
            return None
        child = CHILD_MODELS[kind](human_rights_record_id=record_id, **data)
        return self._serialize_child(kind, self.repo.create_child(child))

    def update_child(self, kind: str, child_id: int, data: dict) -> dict | None:
        child = self.repo.get_child_by_id(kind, child_id)
        if child is None:
            return None
        return self._serialize_child(kind, self.repo.update_child(child, data))

    def delete_child(self, kind: str, child_id: int) -> bool:
        child = self.repo.get_child_by_id(kind, child_id)
        if child is None:
            return False
        self.repo.delete_child(child)
        return True

    # ---- Serialization ----

    def _serialize(self, record: HumanRightsRecord) -> dict:
        out = {"id": record.id, "organization_id": record.organization_id}
        for f in RECORD_FIELDS:
            out[f] = _num(getattr(record, f))
        for kind, rel in CHILD_RELATION.items():
            out[rel] = [self._serialize_child(kind, c) for c in getattr(record, rel)]
        out["total_complaints_filed"] = _sum_field(record.complaints, "filed_count")
        out["total_complaints_pending"] = _sum_field(record.complaints, "pending_count")
        out["created_at"] = record.created_at
        out["updated_at"] = record.updated_at
        return out

    def _serialize_child(self, kind: str, child) -> dict:
        out = {"id": child.id, "human_rights_record_id": child.human_rights_record_id}
        for f in CHILD_FIELDS[kind]:
            out[f] = _num(getattr(child, f))
        if kind == "workforce":
            out["hr_training_coverage_percent"] = _pct(child.hr_training_covered, child.total_count)
        out["created_at"] = child.created_at
        out["updated_at"] = child.updated_at
        return out
