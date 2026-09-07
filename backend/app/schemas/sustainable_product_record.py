"""Pydantic schemas for SustainableProductRecord and ReclaimedMaterialRecord
(BRSR Section C, Principle 2)."""
from __future__ import annotations
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict

ReclaimCategory = Literal["plastics", "e_waste", "hazardous", "other"]

# Percentage fields: 0-100, None = not disclosed.
Pct = Field(None, ge=0, le=100)
# Tonnage fields: non-negative, None = not disclosed.
Mt = Field(None, ge=0)


class ReclaimedMaterialBase(BaseModel):
    material_category: ReclaimCategory
    reused_mt: float | None = Mt
    recycled_mt: float | None = Mt
    disposed_mt: float | None = Mt
    remarks: str | None = None


class ReclaimedMaterialCreate(ReclaimedMaterialBase):
    pass


class ReclaimedMaterialUpdate(BaseModel):
    material_category: ReclaimCategory | None = None
    reused_mt: float | None = Mt
    recycled_mt: float | None = Mt
    disposed_mt: float | None = Mt
    remarks: str | None = None


class ReclaimedMaterialResponse(ReclaimedMaterialBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    sustainable_product_record_id: int
    created_at: datetime
    updated_at: datetime | None = None


class SustainableProductRecordBase(BaseModel):
    reporting_year: int = Field(..., ge=2000, le=2100)
    # EI 1
    rnd_sustainable_percent_current: float | None = Pct
    rnd_sustainable_percent_previous: float | None = Pct
    capex_sustainable_percent_current: float | None = Pct
    capex_sustainable_percent_previous: float | None = Pct
    rnd_capex_details: str | None = None
    # EI 2
    has_sustainable_sourcing_procedure: bool | None = None
    sustainable_sourcing_percent: float | None = Pct
    sustainable_sourcing_details: str | None = None
    # EI 3
    reclaim_process_plastics: str | None = None
    reclaim_process_e_waste: str | None = None
    reclaim_process_hazardous: str | None = None
    reclaim_process_other: str | None = None
    # EI 4
    epr_applicable: bool | None = None
    epr_plan_in_line: bool | None = None
    epr_details: str | None = None
    # Leadership
    has_conducted_lca: bool | None = None
    lca_details: str | None = None
    recycled_input_percent: float | None = Pct
    reclaimed_products_percent_details: str | None = None
    remarks: str | None = None


class SustainableProductRecordCreate(SustainableProductRecordBase):
    pass


class SustainableProductRecordUpdate(BaseModel):
    reporting_year: int | None = Field(None, ge=2000, le=2100)
    rnd_sustainable_percent_current: float | None = Pct
    rnd_sustainable_percent_previous: float | None = Pct
    capex_sustainable_percent_current: float | None = Pct
    capex_sustainable_percent_previous: float | None = Pct
    rnd_capex_details: str | None = None
    has_sustainable_sourcing_procedure: bool | None = None
    sustainable_sourcing_percent: float | None = Pct
    sustainable_sourcing_details: str | None = None
    reclaim_process_plastics: str | None = None
    reclaim_process_e_waste: str | None = None
    reclaim_process_hazardous: str | None = None
    reclaim_process_other: str | None = None
    epr_applicable: bool | None = None
    epr_plan_in_line: bool | None = None
    epr_details: str | None = None
    has_conducted_lca: bool | None = None
    lca_details: str | None = None
    recycled_input_percent: float | None = Pct
    reclaimed_products_percent_details: str | None = None
    remarks: str | None = None


class SustainableProductRecordResponse(SustainableProductRecordBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    organization_id: int
    reclaimed_materials: list[ReclaimedMaterialResponse] = []
    # Derived by the service from the child rows -- never stored.
    # None when no category discloses that quantity.
    total_reused_mt: float | None = None
    total_recycled_mt: float | None = None
    total_disposed_mt: float | None = None
    created_at: datetime
    updated_at: datetime | None = None
