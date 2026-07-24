from pydantic import BaseModel, ConfigDict, Field, model_validator


class NetZeroTargetBase(BaseModel):
    building_id: int | None = None
    manufacturing_unit_id: int | None = None
    target_name: str = Field(..., min_length=1, max_length=150)
    baseline_year: int = Field(..., ge=1990, le=2100)
    baseline_co2e_tonnes: float = Field(..., ge=0)
    target_year: int = Field(..., ge=1990, le=2100)
    reduction_percentage: float = Field(..., ge=0, le=100)
    target_type: str = Field(default="near_term", pattern="^(near_term|long_term)$")
    scope_coverage: str = Field(default="scope_1_2")
    remarks: str | None = None

    @model_validator(mode="after")
    def check_years(self) -> "NetZeroTargetBase":
        if self.target_year <= self.baseline_year:
            raise ValueError("target_year must be after baseline_year.")
        return self


class NetZeroTargetCreate(NetZeroTargetBase):
    pass


class NetZeroTargetUpdate(BaseModel):
    target_name: str | None = Field(default=None, min_length=1, max_length=150)
    baseline_year: int | None = Field(default=None, ge=1990, le=2100)
    baseline_co2e_tonnes: float | None = Field(default=None, ge=0)
    target_year: int | None = Field(default=None, ge=1990, le=2100)
    reduction_percentage: float | None = Field(default=None, ge=0, le=100)
    target_type: str | None = Field(default=None, pattern="^(near_term|long_term)$")
    scope_coverage: str | None = None
    remarks: str | None = None


class NetZeroTargetResponse(NetZeroTargetBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: int
