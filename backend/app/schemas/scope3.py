"""Scope 3 schemas: activity records (entered categories) and the engine summary."""
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

CategoryBasis = Literal["derived", "entered", "not_tracked"]


class Scope3RecordBase(BaseModel):
    manufacturing_unit_id: int | None = None
    year: int = Field(..., ge=2000, le=2100)
    category: int = Field(..., ge=1, le=15)
    description: str = Field(..., min_length=1, max_length=200)
    quantity: float = Field(..., ge=0)
    unit: str = Field(..., max_length=20)
    emission_factor_id: int
    data_source: str | None = Field(None, max_length=200)
    remarks: str | None = None


class Scope3RecordCreate(Scope3RecordBase):
    pass


class Scope3RecordUpdate(BaseModel):
    manufacturing_unit_id: int | None = None
    year: int | None = Field(None, ge=2000, le=2100)
    category: int | None = Field(None, ge=1, le=15)
    description: str | None = Field(None, min_length=1, max_length=200)
    quantity: float | None = Field(None, ge=0)
    unit: str | None = Field(None, max_length=20)
    emission_factor_id: int | None = None
    data_source: str | None = Field(None, max_length=200)
    remarks: str | None = None


class Scope3RecordResponse(Scope3RecordBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    # engine output, read-time
    status: str = "pending"
    status_reason: str | None = None
    factor_value: float | None = None
    factor_unit: str | None = None
    factor_citation: str | None = None
    tco2e: float | None = None


class Scope3CategoryOut(BaseModel):
    category: int
    name: str
    basis: CategoryBasis
    status: str                      # calculated | partial | not_computed | not_tracked
    status_reason: str | None = None
    tco2e: float | None = None
    lines: list[dict] = []           # per-source lines with quantity, factor, citation
    gaps: list[str] = []             # what could not be computed and why


class Scope3SummaryOut(BaseModel):
    year: int
    total_tco2e: float | None
    computed_categories: int
    categories: list[Scope3CategoryOut]
    factor_sources: list[str] = []
