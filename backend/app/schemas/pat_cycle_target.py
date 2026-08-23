"""Pydantic schemas for PatCycleTarget."""
from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator


class PatCycleTargetBase(BaseModel):
    cycle_number: int = Field(..., ge=1)
    cycle_start_year: int = Field(..., ge=2000, le=2100)
    cycle_end_year: int = Field(..., ge=2000, le=2100)
    baseline_production_qty: float = Field(..., gt=0)
    production_unit: str = Field(..., min_length=1, max_length=50)
    baseline_energy_gj: float = Field(..., gt=0)
    mandated_reduction_percent: float = Field(..., ge=0, le=100)

    @field_validator("cycle_end_year")
    @classmethod
    def end_after_start(cls, v: int, info) -> int:
        start = info.data.get("cycle_start_year")
        if start is not None and v < start:
            raise ValueError("cycle_end_year must be >= cycle_start_year")
        return v


class PatCycleTargetCreate(PatCycleTargetBase):
    # manufacturing_unit_id deliberately NOT here -- comes from the URL
    # path, same rule as organization_id always from JWT never body.
    pass


class PatCycleTargetUpdate(BaseModel):
    cycle_start_year: int | None = Field(None, ge=2000, le=2100)
    cycle_end_year: int | None = Field(None, ge=2000, le=2100)
    baseline_production_qty: float | None = Field(None, gt=0)
    production_unit: str | None = Field(None, min_length=1, max_length=50)
    baseline_energy_gj: float | None = Field(None, gt=0)
    mandated_reduction_percent: float | None = Field(None, ge=0, le=100)


class PatCycleTargetResponse(PatCycleTargetBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: int
    manufacturing_unit_id: int
    baseline_sec_gj_per_unit: float
    target_sec_gj_per_unit: float
    created_at: datetime
    updated_at: datetime
