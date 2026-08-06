"""
Pydantic schemas for ManufacturingUnit (Phase 6 -- Manufacturing module)
"""
from pydantic import BaseModel, ConfigDict, Field
from app.models.manufacturing_unit import PatSector


class ManufacturingUnitBase(BaseModel):
    building_id: int | None = None
    unit_code: str = Field(..., min_length=1, max_length=30)
    unit_name: str = Field(..., min_length=1, max_length=200)
    sector: PatSector
    baseline_year: int = Field(..., ge=1990, le=2100)
    standards_applicable: str | None = Field(default=None, max_length=100)
    country_code: str = Field(default="IN", max_length=10)
    category_id: int | None = None
    remarks: str | None = None


class ManufacturingUnitCreate(ManufacturingUnitBase):
    pass


class ManufacturingUnitUpdate(BaseModel):
    building_id: int | None = None
    unit_code: str | None = Field(default=None, min_length=1, max_length=30)
    unit_name: str | None = Field(default=None, min_length=1, max_length=200)
    sector: PatSector | None = None
    baseline_year: int | None = Field(default=None, ge=1990, le=2100)
    standards_applicable: str | None = Field(default=None, max_length=100)
    country_code: str | None = Field(default=None, max_length=10)
    category_id: int | None = None
    remarks: str | None = None
    is_active: bool | None = None


class ManufacturingUnitResponse(ManufacturingUnitBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: int
    is_active: bool
