"""
Pydantic schemas for LCA/PCF Studio (LcaProduct + LcaInventoryItem).

Every inventory item names exactly one factor reference matching its
factor_source. That cross-field rule lives in check_factor_reference() so
the create validator and the service's partial-update path share it.
GWP figures (per item, per stage, per product) are derived by the engine
and attached only on Response models -- never stored.
"""
from __future__ import annotations
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from app.services.cross_sector_ef_library import FUEL_LIBRARY
from app.services.country_config import get_country_config

SystemBoundary = Literal["cradle_to_gate", "gate_to_gate", "cradle_to_grave"]
LcaStage = Literal["raw_materials", "inbound_transport", "manufacturing", "packaging", "outbound_transport"]
FactorSource = Literal["fuel", "electricity", "factor"]
QuantityBasis = Literal["per_functional_unit", "annual_total"]


def _check_fuel_key(v: str) -> str:
    if v not in FUEL_LIBRARY:
        raise ValueError(f"unknown fuel_key '{v}'; see GET /manufacturing-fuel-records/library")
    return v


def _check_country(v: str) -> str:
    v = v.upper()
    if get_country_config(v) is None:
        raise ValueError(f"unknown country_code '{v}'; see GET /countries")
    return v


def check_factor_reference(
    factor_source: str,
    fuel_key: str | None,
    country_code: str | None,
    emission_factor_id: int | None,
) -> None:
    """Exactly the reference matching factor_source must be set, the others None."""
    refs = {"fuel": fuel_key, "electricity": country_code, "factor": emission_factor_id}
    if refs.get(factor_source) is None:
        needed = {"fuel": "fuel_key", "electricity": "country_code", "factor": "emission_factor_id"}[factor_source]
        raise ValueError(f"factor_source '{factor_source}' requires {needed}")
    extra = [k for k, val in refs.items() if k != factor_source and val is not None]
    if extra:
        raise ValueError(f"factor_source '{factor_source}' must not also set {', '.join(extra)} reference")


# ---------------------------------------------------------------- items ---

class LcaInventoryItemBase(BaseModel):
    name: str = Field(..., max_length=200)
    stage: LcaStage
    factor_source: FactorSource
    fuel_key: str | None = None
    country_code: str | None = None
    emission_factor_id: int | None = None
    quantity: float = Field(..., ge=0)
    unit: str = Field(..., max_length=20)
    basis: QuantityBasis = "per_functional_unit"
    data_source: str | None = Field(None, max_length=200)
    remarks: str | None = None

    @field_validator("fuel_key")
    @classmethod
    def fuel_key_known(cls, v: str | None) -> str | None:
        return None if v is None else _check_fuel_key(v)

    @field_validator("country_code")
    @classmethod
    def country_known(cls, v: str | None) -> str | None:
        return None if v is None else _check_country(v)

    @model_validator(mode="after")
    def reference_matches_source(self):
        check_factor_reference(self.factor_source, self.fuel_key, self.country_code, self.emission_factor_id)
        return self


class LcaInventoryItemCreate(LcaInventoryItemBase):
    pass


class LcaInventoryItemUpdate(BaseModel):
    # Cross-field consistency is checked by the service after merging with
    # the stored row (a partial payload cannot see the other fields).
    name: str | None = Field(None, max_length=200)
    stage: LcaStage | None = None
    factor_source: FactorSource | None = None
    fuel_key: str | None = None
    country_code: str | None = None
    emission_factor_id: int | None = None
    quantity: float | None = Field(None, ge=0)
    unit: str | None = Field(None, max_length=20)
    basis: QuantityBasis | None = None
    data_source: str | None = Field(None, max_length=200)
    remarks: str | None = None

    @field_validator("fuel_key")
    @classmethod
    def fuel_key_known(cls, v: str | None) -> str | None:
        return None if v is None else _check_fuel_key(v)

    @field_validator("country_code")
    @classmethod
    def country_known(cls, v: str | None) -> str | None:
        return None if v is None else _check_country(v)


class LcaInventoryItemResponse(LcaInventoryItemBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    product_id: int
    organization_id: int
    # Derived by the engine, never stored. None when the factor could not be
    # resolved (status explains why) -- never silently 0.
    status: str = "pending"                 # calculated | no_factor | unit_mismatch | no_annual_output
    quantity_per_fu: float | None = None
    factor_value: float | None = None       # kgCO2e per factor_unit (fossil)
    factor_unit: str | None = None
    factor_citation: str | None = None
    is_biogenic: bool = False
    co2e_kg_per_fu: float | None = None     # fossil CO2e per functional unit
    biogenic_co2_kg_per_fu: float | None = None
    created_at: datetime
    updated_at: datetime


# ------------------------------------------------------------- products ---

class LcaProductBase(BaseModel):
    manufacturing_unit_id: int | None = None
    name: str = Field(..., max_length=200)
    product_code: str | None = Field(None, max_length=50)
    description: str | None = None
    functional_unit_qty: float = Field(1.0, gt=0)
    functional_unit: str = Field(..., max_length=30)
    system_boundary: SystemBoundary = "cradle_to_gate"
    reference_year: int | None = Field(None, ge=2000, le=2100)
    annual_output_qty: float | None = Field(None, gt=0)
    production_country_code: str = "IN"
    remarks: str | None = None

    @field_validator("production_country_code")
    @classmethod
    def country_known(cls, v: str) -> str:
        return _check_country(v)


class LcaProductCreate(LcaProductBase):
    pass


class LcaProductUpdate(BaseModel):
    manufacturing_unit_id: int | None = None
    name: str | None = Field(None, max_length=200)
    product_code: str | None = Field(None, max_length=50)
    description: str | None = None
    functional_unit_qty: float | None = Field(None, gt=0)
    functional_unit: str | None = Field(None, max_length=30)
    system_boundary: SystemBoundary | None = None
    reference_year: int | None = Field(None, ge=2000, le=2100)
    annual_output_qty: float | None = Field(None, gt=0)
    production_country_code: str | None = None
    remarks: str | None = None

    @field_validator("production_country_code")
    @classmethod
    def country_known(cls, v: str | None) -> str | None:
        return None if v is None else _check_country(v)


class LcaStageTotal(BaseModel):
    stage: LcaStage
    co2e_kg_per_fu: float | None = None
    share_percent: float | None = None
    item_count: int = 0


class LcaProductSummary(LcaProductBase):
    """List row: no items, headline GWP only."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    organization_id: int
    item_count: int = 0
    unresolved_count: int = 0
    gwp_kgco2e_per_fu: float | None = None
    created_at: datetime
    updated_at: datetime


class LcaProductResponse(LcaProductSummary):
    items: list[LcaInventoryItemResponse] = []
    by_stage: list[LcaStageTotal] = []
    biogenic_co2_kg_per_fu: float | None = None
    # Distinct factor citations used (list, never collapsed to one string).
    factor_sources: list[str] = []
    method: str = "ISO 14067 carbon footprint, GWP100 (AR5); cradle-to-gate unless stated; not a verified ISO 14040/44 LCA"
