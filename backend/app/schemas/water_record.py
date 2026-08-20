from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class WaterRecordBase(BaseModel):
    manufacturing_unit_id: Optional[int] = None
    building_id: Optional[int] = None
    period_start: date
    period_end: date
    is_water_stressed_area: bool = False

    # Withdrawal by source (KL)
    withdrawal_surface_water: Optional[Decimal] = Field(default=None, ge=0)
    withdrawal_groundwater: Optional[Decimal] = Field(default=None, ge=0)
    withdrawal_third_party: Optional[Decimal] = Field(default=None, ge=0)
    withdrawal_seawater_desalinated: Optional[Decimal] = Field(default=None, ge=0)
    withdrawal_others: Optional[Decimal] = Field(default=None, ge=0)

    # Discharge by destination (KL)
    discharge_surface_water: Optional[Decimal] = Field(default=None, ge=0)
    discharge_groundwater: Optional[Decimal] = Field(default=None, ge=0)
    discharge_seawater: Optional[Decimal] = Field(default=None, ge=0)
    discharge_third_party: Optional[Decimal] = Field(default=None, ge=0)
    discharge_others: Optional[Decimal] = Field(default=None, ge=0)

    discharge_treatment_level: Optional[str] = None
    has_zero_liquid_discharge: Optional[bool] = None
    remarks: Optional[str] = None

    @model_validator(mode="after")
    def check_period_order(self):
        if self.period_end < self.period_start:
            raise ValueError("period_end cannot be earlier than period_start")
        return self


class WaterRecordCreate(WaterRecordBase):
    pass


class WaterRecordUpdate(BaseModel):
    """All optional: an existing record is edited field by field."""
    manufacturing_unit_id: Optional[int] = None
    building_id: Optional[int] = None
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    is_water_stressed_area: Optional[bool] = None

    withdrawal_surface_water: Optional[Decimal] = Field(default=None, ge=0)
    withdrawal_groundwater: Optional[Decimal] = Field(default=None, ge=0)
    withdrawal_third_party: Optional[Decimal] = Field(default=None, ge=0)
    withdrawal_seawater_desalinated: Optional[Decimal] = Field(default=None, ge=0)
    withdrawal_others: Optional[Decimal] = Field(default=None, ge=0)

    discharge_surface_water: Optional[Decimal] = Field(default=None, ge=0)
    discharge_groundwater: Optional[Decimal] = Field(default=None, ge=0)
    discharge_seawater: Optional[Decimal] = Field(default=None, ge=0)
    discharge_third_party: Optional[Decimal] = Field(default=None, ge=0)
    discharge_others: Optional[Decimal] = Field(default=None, ge=0)

    discharge_treatment_level: Optional[str] = None
    has_zero_liquid_discharge: Optional[bool] = None
    remarks: Optional[str] = None


class WaterRecordRead(WaterRecordBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Derived, never stored - SEBI defines consumption as withdrawal minus
    # discharge, so it is computed on read.
    total_withdrawal: Optional[Decimal] = None
    total_discharge: Optional[Decimal] = None
    total_consumption: Optional[Decimal] = None
