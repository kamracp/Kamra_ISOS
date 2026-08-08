"""
Pydantic schemas for ManufacturingEmissionRecord.

Mirrors ProductionRecord's schema pattern (Base -> Create/Update/Response).
calculator_inputs stays a generic dict[str, float | str] since each sector
calculator's input shape differs (see the model's docstring).
"""
from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.models.manufacturing_unit import PatSector


class ManufacturingEmissionRecordBase(BaseModel):
    manufacturing_unit_id: int
    sector: PatSector
    period_start: date
    period_end: date
    calculation_source: str
    calculator_inputs: dict[str, float | str]
    co2_tonnes: float
    is_biogenic: bool = False
    remarks: str | None = None


class ManufacturingEmissionRecordCreate(ManufacturingEmissionRecordBase):
    pass


class ManufacturingEmissionRecordUpdate(BaseModel):
    period_start: date | None = None
    period_end: date | None = None
    calculation_source: str | None = None
    calculator_inputs: dict[str, float | str] | None = None
    co2_tonnes: float | None = None
    is_biogenic: bool | None = None
    remarks: str | None = None


class ManufacturingEmissionRecordResponse(ManufacturingEmissionRecordBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: int
    created_at: datetime
    updated_at: datetime
