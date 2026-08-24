"""Pydantic schemas for EthicsRecord (BRSR Section C, Principle 1)."""
from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict


class EthicsRecordBase(BaseModel):
    reporting_year: int = Field(..., ge=2000, le=2100)

    board_kmp_total_count: int | None = Field(None, ge=0)
    board_kmp_trained_count: int | None = Field(None, ge=0)
    employees_total_count: int | None = Field(None, ge=0)
    employees_trained_count: int | None = Field(None, ge=0)
    workers_total_count: int | None = Field(None, ge=0)
    workers_trained_count: int | None = Field(None, ge=0)

    disciplinary_actions_directors: int | None = Field(None, ge=0)
    disciplinary_actions_kmp: int | None = Field(None, ge=0)
    disciplinary_actions_employees: int | None = Field(None, ge=0)
    disciplinary_actions_workers: int | None = Field(None, ge=0)
    fines_penalties_amount_inr: Decimal | None = Field(None, ge=0)

    has_conflict_of_interest_process: str | None = Field(None, max_length=10)
    conflict_of_interest_disclosures_count: int | None = Field(None, ge=0)

    corruption_complaints_received: int | None = Field(None, ge=0)
    corruption_complaints_pending: int | None = Field(None, ge=0)

    remarks: str | None = None


class EthicsRecordCreate(EthicsRecordBase):
    pass


class EthicsRecordUpdate(BaseModel):
    reporting_year: int | None = Field(None, ge=2000, le=2100)

    board_kmp_total_count: int | None = Field(None, ge=0)
    board_kmp_trained_count: int | None = Field(None, ge=0)
    employees_total_count: int | None = Field(None, ge=0)
    employees_trained_count: int | None = Field(None, ge=0)
    workers_total_count: int | None = Field(None, ge=0)
    workers_trained_count: int | None = Field(None, ge=0)

    disciplinary_actions_directors: int | None = Field(None, ge=0)
    disciplinary_actions_kmp: int | None = Field(None, ge=0)
    disciplinary_actions_employees: int | None = Field(None, ge=0)
    disciplinary_actions_workers: int | None = Field(None, ge=0)
    fines_penalties_amount_inr: Decimal | None = Field(None, ge=0)

    has_conflict_of_interest_process: str | None = Field(None, max_length=10)
    conflict_of_interest_disclosures_count: int | None = Field(None, ge=0)

    corruption_complaints_received: int | None = Field(None, ge=0)
    corruption_complaints_pending: int | None = Field(None, ge=0)

    remarks: str | None = None


class EthicsRecordResponse(EthicsRecordBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: int
    # Derived, never stored -- attached by the service.
    board_kmp_trained_percent: float | None = None
    employees_trained_percent: float | None = None
    workers_trained_percent: float | None = None
    created_at: datetime
    updated_at: datetime | None = None
