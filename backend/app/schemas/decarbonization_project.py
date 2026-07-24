from pydantic import BaseModel, ConfigDict, Field

from app.models.decarbonization_project import ProjectCategory, ProjectStatus


class DecarbonizationProjectBase(BaseModel):
    building_id: int | None = None
    manufacturing_unit_id: int | None = None
    project_name: str = Field(..., min_length=1, max_length=200)
    category: ProjectCategory
    status: ProjectStatus = ProjectStatus.PROPOSED
    capex: float = Field(..., ge=0)
    annual_opex_delta: float = 0.0
    lifespan_years: int = Field(..., ge=1, le=100)
    annual_co2e_abated_tonnes: float = Field(..., ge=0)
    remarks: str | None = None


class DecarbonizationProjectCreate(DecarbonizationProjectBase):
    pass


class DecarbonizationProjectUpdate(BaseModel):
    building_id: int | None = None
    manufacturing_unit_id: int | None = None
    project_name: str | None = Field(default=None, min_length=1, max_length=200)
    category: ProjectCategory | None = None
    status: ProjectStatus | None = None
    capex: float | None = Field(default=None, ge=0)
    annual_opex_delta: float | None = None
    lifespan_years: int | None = Field(default=None, ge=1, le=100)
    annual_co2e_abated_tonnes: float | None = Field(default=None, ge=0)
    remarks: str | None = None


class DecarbonizationProjectResponse(DecarbonizationProjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: int
