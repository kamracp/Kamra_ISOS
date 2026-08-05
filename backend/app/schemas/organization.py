from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class OrganizationBase(BaseModel):
    organization_code: str = Field(
        ...,
        min_length=1,
        max_length=30,
    )

    organization_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
    )

    legal_name: str | None = Field(
        default=None,
        max_length=250,
    )

    industry: str | None = Field(
        default=None,
        max_length=120,
    )

    email: EmailStr | None = None

    phone: str | None = Field(
        default=None,
        max_length=50,
    )

    website: str | None = Field(
        default=None,
        max_length=250,
    )

    country: str | None = Field(
        default=None,
        max_length=120,
    )

    state: str | None = Field(
        default=None,
        max_length=120,
    )

    city: str | None = Field(
        default=None,
        max_length=120,
    )

    timezone: str | None = Field(
        default=None,
        max_length=80,
    )

    currency: str | None = Field(
        default=None,
        max_length=20,
    )

    employee_count: int | None = None
    annual_revenue_inr: float | None = None
    is_active: bool = True


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    @field_validator("email", mode="before")
    @classmethod
    def empty_email_to_none(cls, v):
        return None if v == "" else v

    organization_code: str | None = Field(
        default=None,
        max_length=30,
    )

    organization_name: str | None = Field(
        default=None,
        max_length=200,
    )

    legal_name: str | None = Field(
        default=None,
        max_length=250,
    )

    industry: str | None = Field(
        default=None,
        max_length=120,
    )

    email: EmailStr | None = None

    phone: str | None = Field(
        default=None,
        max_length=50,
    )

    website: str | None = Field(
        default=None,
        max_length=250,
    )

    country: str | None = Field(
        default=None,
        max_length=120,
    )

    state: str | None = Field(
        default=None,
        max_length=120,
    )

    city: str | None = Field(
        default=None,
        max_length=120,
    )

    timezone: str | None = Field(
        default=None,
        max_length=80,
    )

    currency: str | None = Field(
        default=None,
        max_length=20,
    )

    employee_count: int | None = None
    annual_revenue_inr: float | None = None
    is_active: bool | None = None


class OrganizationResponse(OrganizationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )