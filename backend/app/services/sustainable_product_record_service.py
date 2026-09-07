"""
Sustainable Product Record Service (BRSR Section C, Principle 2)

Manages one P2 disclosure record per organization per reporting year,
plus its reclaimed-material child rows (Leadership Indicator Q4).

Derived totals across material categories are computed here on read and
never stored -- same rule as water/waste. A total is None only when NO
category discloses that quantity; an explicit 0 among Nones does produce
a total, so "not disclosed" and "zero" stay distinct end to end.
"""
from __future__ import annotations
from decimal import Decimal
from app.repositories.sustainable_product_record_repository import (
    SustainableProductRecordRepository,
)
from app.models.sustainable_product_record import (
    SustainableProductRecord,
    ReclaimedMaterialRecord,
)


class DuplicateReportingYear(Exception):
    """Raised when a second P2 record is attempted for a year that already
    has one. The API layer maps this to HTTP 409."""


# Scalar fields copied straight from the model on serialize. Kept as one
# tuple so the response cannot silently drop a column added later.
RECORD_FIELDS = (
    "reporting_year",
    "rnd_sustainable_percent_current",
    "rnd_sustainable_percent_previous",
    "capex_sustainable_percent_current",
    "capex_sustainable_percent_previous",
    "rnd_capex_details",
    "has_sustainable_sourcing_procedure",
    "sustainable_sourcing_percent",
    "sustainable_sourcing_details",
    "reclaim_process_plastics",
    "reclaim_process_e_waste",
    "reclaim_process_hazardous",
    "reclaim_process_other",
    "epr_applicable",
    "epr_plan_in_line",
    "epr_details",
    "has_conducted_lca",
    "lca_details",
    "recycled_input_percent",
    "reclaimed_products_percent_details",
    "remarks",
)

MATERIAL_FIELDS = ("material_category", "reused_mt", "recycled_mt", "disposed_mt", "remarks")


def _num(value):
    """Numeric columns come back as Decimal; JSON wants float."""
    return float(value) if isinstance(value, Decimal) else value


def _sum_field(rows, field: str) -> float | None:
    values = [getattr(r, field) for r in rows if getattr(r, field) is not None]
    if not values:
        return None
    return float(sum(values))


class SustainableProductRecordService:
    def __init__(self, db, organization_id: int):
        self.organization_id = organization_id
        self.repo = SustainableProductRecordRepository(db, organization_id)

    # ---- Records ----

    def create_record(self, data: dict) -> dict:
        if self.repo.get_by_year(data["reporting_year"]) is not None:
            raise DuplicateReportingYear(data["reporting_year"])
        record = SustainableProductRecord(organization_id=self.organization_id, **data)
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
        new_year = data.get("reporting_year")
        if new_year is not None and new_year != record.reporting_year:
            if self.repo.get_by_year(new_year) is not None:
                raise DuplicateReportingYear(new_year)
        record = self.repo.update(record, data)
        return self._serialize(record)

    def delete_record(self, record_id: int) -> bool:
        record = self.repo.get_by_id(record_id)
        if record is None:
            return False
        self.repo.delete(record)
        return True

    def _serialize(self, record: SustainableProductRecord) -> dict:
        out = {"id": record.id, "organization_id": record.organization_id}
        for f in RECORD_FIELDS:
            out[f] = _num(getattr(record, f))
        rows = record.reclaimed_materials
        out["reclaimed_materials"] = [self._serialize_material(m) for m in rows]
        out["total_reused_mt"] = _sum_field(rows, "reused_mt")
        out["total_recycled_mt"] = _sum_field(rows, "recycled_mt")
        out["total_disposed_mt"] = _sum_field(rows, "disposed_mt")
        out["created_at"] = record.created_at
        out["updated_at"] = record.updated_at
        return out

    def _serialize_material(self, material: ReclaimedMaterialRecord) -> dict:
        out = {
            "id": material.id,
            "sustainable_product_record_id": material.sustainable_product_record_id,
        }
        for f in MATERIAL_FIELDS:
            out[f] = _num(getattr(material, f))
        out["created_at"] = material.created_at
        out["updated_at"] = material.updated_at
        return out

    # ---- Reclaimed materials ----

    def create_material(self, record_id: int, data: dict) -> dict | None:
        record = self.repo.get_by_id(record_id)
        if record is None:
            return None
        material = ReclaimedMaterialRecord(sustainable_product_record_id=record_id, **data)
        material = self.repo.create_material(material)
        return self._serialize_material(material)

    def update_material(self, material_id: int, data: dict) -> dict | None:
        material = self.repo.get_material_by_id(material_id)
        if material is None:
            return None
        material = self.repo.update_material(material, data)
        return self._serialize_material(material)

    def delete_material(self, material_id: int) -> bool:
        material = self.repo.get_material_by_id(material_id)
        if material is None:
            return False
        self.repo.delete_material(material)
        return True
