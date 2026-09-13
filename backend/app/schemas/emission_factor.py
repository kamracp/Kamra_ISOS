from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class EmissionFactorBase(BaseModel):
    """Official emission factor — shared reference data (no organization_id).

    BENAS permanent rule: values come ONLY from official publications
    (India CEA / DEFRA / IPCC). Source, year and validity window are
    mandatory for audit traceability.
    """

    # Must match EnergyMeter.meter_type values.
    meter_type: str = Field(..., min_length=1, max_length=50)
    # Must match the meter's consumption unit (kWh, litres, SCM, kg ...).
    unit: str = Field(..., min_length=1, max_length=20)
    factor_kgco2e_per_unit: float = Field(..., ge=0)
    energy_content_gj_per_unit: float | None = Field(default=None, ge=0)
    region: str = Field(default="IN", min_length=2, max_length=10)
    source: str = Field(..., min_length=3, max_length=200)
    source_year: int = Field(..., ge=1990, le=2100)
    document_reference: str | None = Field(default=None, max_length=500)
    reference_id: str | None = Field(default=None, max_length=60)   # lca_references.py id
    valid_from: date
    # None = open-ended (currently valid factor).
    valid_to: date | None = None
    is_active: bool = True
    notes: str | None = Field(default=None, max_length=2000)

    @model_validator(mode="after")
    def check_validity_window(self) -> "EmissionFactorBase":
        if self.valid_to is not None and self.valid_to < self.valid_from:
            raise ValueError(
                "valid_to cannot be before valid_from.",
            )
        return self


class EmissionFactorCreate(EmissionFactorBase):
    pass


class EmissionFactorUpdate(BaseModel):
    meter_type: str | None = Field(default=None, min_length=1, max_length=50)
    unit: str | None = Field(default=None, min_length=1, max_length=20)
    factor_kgco2e_per_unit: float | None = Field(default=None, ge=0)
    energy_content_gj_per_unit: float | None = Field(default=None, ge=0)
    region: str | None = Field(default=None, min_length=2, max_length=10)
    source: str | None = Field(default=None, min_length=3, max_length=200)
    source_year: int | None = Field(default=None, ge=1990, le=2100)
    document_reference: str | None = Field(default=None, max_length=500)
    reference_id: str | None = Field(default=None, max_length=60)   # lca_references.py id
    valid_from: date | None = None
    valid_to: date | None = None
    is_active: bool | None = None
    notes: str | None = Field(default=None, max_length=2000)

    @model_validator(mode="after")
    def check_validity_window(self) -> "EmissionFactorUpdate":
        if (
            self.valid_from is not None
            and self.valid_to is not None
            and self.valid_to < self.valid_from
        ):
            raise ValueError(
                "valid_to cannot be before valid_from.",
            )
        return self


class EmissionFactorResponse(EmissionFactorBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
