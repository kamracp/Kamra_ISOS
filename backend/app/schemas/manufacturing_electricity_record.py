"""
Pydantic schemas for ManufacturingElectricityRecord.
Mirrors ManufacturingEmissionRecord's Base -> Create/Update/Response
pattern. scope2_co2e_kg is derived (country grid factor x consumed
kWh minus renewable) and attached only in the Response, by the
service -- never stored, never accepted on Create/Update.
"""
from __future__ import annotations
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict


class ManufacturingElectricityRecordBase(BaseModel):
    manufacturing_unit_id: int
    period_start: date
    period_end: date
    electricity_consumed_kwh: float
    renewable_kwh: float = 0.0
    source: str | None = None
    remarks: str | None = None


class ManufacturingElectricityRecordCreate(ManufacturingElectricityRecordBase):
    pass


class ManufacturingElectricityRecordUpdate(BaseModel):
    period_start: date | None = None
    period_end: date | None = None
    electricity_consumed_kwh: float | None = None
    renewable_kwh: float | None = None
    source: str | None = None
    remarks: str | None = None


class ManufacturingElectricityRecordResponse(ManufacturingElectricityRecordBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    organization_id: int
    # Derived, never stored -- attached by the service using the unit's
    # country_code grid factor. None if that country has no verified
    # grid factor yet (needs_verification=True in country_config).
    scope2_co2e_kg: float | None = None
    grid_factor_kgco2e_per_kwh: float | None = None
    grid_factor_source: str | None = None
    created_at: datetime
    updated_at: datetime
