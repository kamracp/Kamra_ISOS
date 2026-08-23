"""Pydantic schemas for EnergyProductionRecord."""
from __future__ import annotations
from datetime import date, datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator


class EnergyProductionRecordBase(BaseModel):
    period_start: date
    period_end: date
    energy_consumed_gj: float = Field(..., gt=0)
    production_quantity: float = Field(..., gt=0)
    production_unit: str = Field(..., min_length=1, max_length=50)

    @field_validator("period_end")
    @classmethod
    def end_after_start(cls, v: date, info) -> date:
        start = info.data.get("period_start")
        if start is not None and v < start:
            raise ValueError("period_end must be >= period_start")
        return v


class EnergyProductionRecordCreate(EnergyProductionRecordBase):
    # manufacturing_unit_id deliberately NOT here -- comes from the URL
    # path, same rule as organization_id always from JWT never body.
    pass


class EnergyProductionRecordUpdate(BaseModel):
    period_start: date | None = None
    period_end: date | None = None
    energy_consumed_gj: float | None = Field(None, gt=0)
    production_quantity: float | None = Field(None, gt=0)
    production_unit: str | None = Field(None, min_length=1, max_length=50)


class EnergyProductionRecordResponse(EnergyProductionRecordBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: int
    manufacturing_unit_id: int
    energy_consumed_toe: float
    sec_gj_per_unit: float
    created_at: datetime
    updated_at: datetime
