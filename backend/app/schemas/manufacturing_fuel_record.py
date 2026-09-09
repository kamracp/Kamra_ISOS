"""
Pydantic schemas for ManufacturingFuelRecord. fuel_key is validated
against cross_sector_ef_library at the API boundary so a typo can never
reach the DB. Energy (GJ, toe) and Scope 1 CO2e are derived by the
service and attached only on the Response -- never stored.
"""
from __future__ import annotations
from datetime import date, datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.services.cross_sector_ef_library import FUEL_LIBRARY

FuelPurpose = Literal["process_heat", "captive_power", "steam_boiler", "transport", "other"]


def _check_fuel_key(v: str) -> str:
    if v not in FUEL_LIBRARY:
        raise ValueError(f"unknown fuel_key '{v}'; see GET /manufacturing-fuel-records/library")
    return v


class ManufacturingFuelRecordBase(BaseModel):
    manufacturing_unit_id: int
    period_start: date
    period_end: date
    fuel_key: str
    quantity_tonnes: float = Field(..., ge=0)
    purpose: FuelPurpose = "process_heat"
    source: str | None = Field(None, max_length=100)
    remarks: str | None = None

    @field_validator("fuel_key")
    @classmethod
    def fuel_key_known(cls, v: str) -> str:
        return _check_fuel_key(v)


class ManufacturingFuelRecordCreate(ManufacturingFuelRecordBase):
    pass


class ManufacturingFuelRecordUpdate(BaseModel):
    period_start: date | None = None
    period_end: date | None = None
    fuel_key: str | None = None
    quantity_tonnes: float | None = Field(None, ge=0)
    purpose: FuelPurpose | None = None
    source: str | None = Field(None, max_length=100)
    remarks: str | None = None

    @field_validator("fuel_key")
    @classmethod
    def fuel_key_known(cls, v: str | None) -> str | None:
        return None if v is None else _check_fuel_key(v)


class ManufacturingFuelRecordResponse(ManufacturingFuelRecordBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    organization_id: int
    fuel_name: str | None = None
    fuel_category: str | None = None
    is_biogenic: bool | None = None
    # Derived, never stored.
    lhv_gj_per_tonne: float | None = None
    energy_gj: float | None = None
    energy_toe: float | None = None
    scope1_co2e_kg: float | None = None       # fossil CO2e (biogenic CO2 excluded)
    biogenic_co2_kg: float | None = None      # reported separately, GHG Protocol
    factor_source: str = "IPCC 2006 Vol.2 Ch.2 (AR5 GWP-100)"
    created_at: datetime
    updated_at: datetime
