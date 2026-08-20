from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class WasteRecordBase(BaseModel):
    manufacturing_unit_id: Optional[int] = None
    building_id: Optional[int] = None
    period_start: date
    period_end: date

    # Generated, SEBI categories A-H (MT)
    plastic_waste: Optional[Decimal] = Field(default=None, ge=0)
    e_waste: Optional[Decimal] = Field(default=None, ge=0)
    bio_medical_waste: Optional[Decimal] = Field(default=None, ge=0)
    construction_demolition_waste: Optional[Decimal] = Field(default=None, ge=0)
    battery_waste: Optional[Decimal] = Field(default=None, ge=0)
    radioactive_waste: Optional[Decimal] = Field(default=None, ge=0)
    other_hazardous_waste: Optional[Decimal] = Field(default=None, ge=0)
    other_non_hazardous_waste: Optional[Decimal] = Field(default=None, ge=0)

    # Recovered / diverted from disposal (MT)
    recycled: Optional[Decimal] = Field(default=None, ge=0)
    reused: Optional[Decimal] = Field(default=None, ge=0)
    other_recovery: Optional[Decimal] = Field(default=None, ge=0)

    # Disposed (MT)
    incineration: Optional[Decimal] = Field(default=None, ge=0)
    landfilling: Optional[Decimal] = Field(default=None, ge=0)
    other_disposal: Optional[Decimal] = Field(default=None, ge=0)

    waste_management_practices: Optional[str] = None
    remarks: Optional[str] = None

    @model_validator(mode="after")
    def check_period_order(self):
        if self.period_end < self.period_start:
            raise ValueError("period_end cannot be earlier than period_start")
        return self


class WasteRecordCreate(WasteRecordBase):
    pass


class WasteRecordUpdate(BaseModel):
    """All optional: an existing record is edited field by field."""
    manufacturing_unit_id: Optional[int] = None
    building_id: Optional[int] = None
    period_start: Optional[date] = None
    period_end: Optional[date] = None

    plastic_waste: Optional[Decimal] = Field(default=None, ge=0)
    e_waste: Optional[Decimal] = Field(default=None, ge=0)
    bio_medical_waste: Optional[Decimal] = Field(default=None, ge=0)
    construction_demolition_waste: Optional[Decimal] = Field(default=None, ge=0)
    battery_waste: Optional[Decimal] = Field(default=None, ge=0)
    radioactive_waste: Optional[Decimal] = Field(default=None, ge=0)
    other_hazardous_waste: Optional[Decimal] = Field(default=None, ge=0)
    other_non_hazardous_waste: Optional[Decimal] = Field(default=None, ge=0)

    recycled: Optional[Decimal] = Field(default=None, ge=0)
    reused: Optional[Decimal] = Field(default=None, ge=0)
    other_recovery: Optional[Decimal] = Field(default=None, ge=0)

    incineration: Optional[Decimal] = Field(default=None, ge=0)
    landfilling: Optional[Decimal] = Field(default=None, ge=0)
    other_disposal: Optional[Decimal] = Field(default=None, ge=0)

    waste_management_practices: Optional[str] = None
    remarks: Optional[str] = None


class WasteRecordRead(WasteRecordBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Derived, never stored.
    total_generated: Optional[Decimal] = None
    total_recovered: Optional[Decimal] = None
    total_disposed: Optional[Decimal] = None
    hazardous_generated: Optional[Decimal] = None
