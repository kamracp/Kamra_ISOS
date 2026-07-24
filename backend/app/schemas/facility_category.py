from pydantic import BaseModel, ConfigDict, Field


class FacilityCategoryBase(BaseModel):
    segment: str = Field(..., pattern="^(benas|manufacturing)$")
    name: str = Field(..., min_length=1, max_length=150)
    display_order: int = 0


class FacilityCategoryCreate(FacilityCategoryBase):
    pass


class FacilityCategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    display_order: int | None = None


class FacilityCategoryResponse(FacilityCategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: int
