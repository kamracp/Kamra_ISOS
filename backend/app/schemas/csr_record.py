"""Pydantic schemas for CsrRecord and CsrProject."""
from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict


class CsrProjectBase(BaseModel):
    project_name: str = Field(..., min_length=1, max_length=255)
    activity_category: str | None = Field(None, max_length=255)
    location: str | None = Field(None, max_length=255)
    is_local_area: str | None = Field(None, max_length=10)
    amount_spent_inr: Decimal | None = Field(None, ge=0)
    direct_beneficiaries_count: int | None = Field(None, ge=0)
    remarks: str | None = None


class CsrProjectCreate(CsrProjectBase):
    pass


class CsrProjectUpdate(BaseModel):
    project_name: str | None = Field(None, min_length=1, max_length=255)
    activity_category: str | None = Field(None, max_length=255)
    location: str | None = Field(None, max_length=255)
    is_local_area: str | None = Field(None, max_length=10)
    amount_spent_inr: Decimal | None = Field(None, ge=0)
    direct_beneficiaries_count: int | None = Field(None, ge=0)
    remarks: str | None = None


class CsrProjectResponse(CsrProjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    csr_record_id: int
    created_at: datetime
    updated_at: datetime | None = None


class CsrRecordBase(BaseModel):
    reporting_year: int = Field(..., ge=2000, le=2100)
    csr_budget_inr: Decimal | None = Field(None, ge=0)
    csr_amount_spent_inr: Decimal | None = Field(None, ge=0)
    csr_admin_overhead_inr: Decimal | None = Field(None, ge=0)
    remarks: str | None = None


class CsrRecordCreate(CsrRecordBase):
    pass


class CsrRecordUpdate(BaseModel):
    reporting_year: int | None = Field(None, ge=2000, le=2100)
    csr_budget_inr: Decimal | None = Field(None, ge=0)
    csr_amount_spent_inr: Decimal | None = Field(None, ge=0)
    csr_admin_overhead_inr: Decimal | None = Field(None, ge=0)
    remarks: str | None = None


class CsrRecordResponse(CsrRecordBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: int
    # Derived, never stored -- attached by the service.
    percent_spent_vs_budget: float | None = None
    total_project_spend_inr: Decimal | None = None
    projects: list[CsrProjectResponse] = []
    created_at: datetime
    updated_at: datetime | None = None
