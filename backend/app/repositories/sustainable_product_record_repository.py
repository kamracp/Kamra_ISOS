"""Repository for SustainableProductRecord + ReclaimedMaterialRecord --
tenant-scoped via organization_id (BRSR Principle 2)."""
from __future__ import annotations
from sqlalchemy.orm import Session, joinedload
from app.models.sustainable_product_record import (
    SustainableProductRecord,
    ReclaimedMaterialRecord,
)


class SustainableProductRecordRepository:
    def __init__(self, db: Session, organization_id: int):
        self.db = db
        self.organization_id = organization_id

    def _base_query(self):
        # The ONE place the tenant filter lives -- every parent read goes
        # through here, so no method can read another organization's rows.
        return (
            self.db.query(SustainableProductRecord)
            .options(joinedload(SustainableProductRecord.reclaimed_materials))
            .filter(SustainableProductRecord.organization_id == self.organization_id)
        )

    def get_all(self) -> list[SustainableProductRecord]:
        return (
            self._base_query()
            .order_by(SustainableProductRecord.reporting_year.desc())
            .all()
        )

    def get_by_id(self, record_id: int) -> SustainableProductRecord | None:
        return self._base_query().filter(SustainableProductRecord.id == record_id).first()

    def get_by_year(self, year: int) -> SustainableProductRecord | None:
        return (
            self._base_query()
            .filter(SustainableProductRecord.reporting_year == year)
            .first()
        )

    def create(self, record: SustainableProductRecord) -> SustainableProductRecord:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def update(self, record: SustainableProductRecord, data: dict) -> SustainableProductRecord:
        for key, value in data.items():
            setattr(record, key, value)
        self.db.commit()
        self.db.refresh(record)
        return record

    def delete(self, record: SustainableProductRecord) -> None:
        self.db.delete(record)
        self.db.commit()

    # ---- Reclaimed materials (child rows; tenant check via join to parent) ----
    def get_material_by_id(self, material_id: int) -> ReclaimedMaterialRecord | None:
        return (
            self.db.query(ReclaimedMaterialRecord)
            .join(SustainableProductRecord)
            .filter(
                ReclaimedMaterialRecord.id == material_id,
                SustainableProductRecord.organization_id == self.organization_id,
            )
            .first()
        )

    def create_material(self, material: ReclaimedMaterialRecord) -> ReclaimedMaterialRecord:
        self.db.add(material)
        self.db.commit()
        self.db.refresh(material)
        return material

    def update_material(self, material: ReclaimedMaterialRecord, data: dict) -> ReclaimedMaterialRecord:
        for key, value in data.items():
            setattr(material, key, value)
        self.db.commit()
        self.db.refresh(material)
        return material

    def delete_material(self, material: ReclaimedMaterialRecord) -> None:
        self.db.delete(material)
        self.db.commit()
