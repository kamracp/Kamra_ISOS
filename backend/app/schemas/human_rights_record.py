"""Pydantic schemas for HumanRightsRecord and its three child tables
(BRSR Section C, Principle 5)."""
from __future__ import annotations
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict

WorkforceCategory = Literal["permanent_employees", "other_employees", "permanent_workers", "other_workers"]
RemunerationCategory = Literal["bod", "kmp", "employees", "workers"]
ComplaintCategory = Literal["sexual_harassment", "discrimination", "child_labour", "forced_labour", "wages", "other"]

Pct = Field(None, ge=0, le=100)
Count = Field(None, ge=0)
Money = Field(None, ge=0)


# ---- Workforce coverage (EI 1 + EI 2) ----
class WorkforceCoverageBase(BaseModel):
    category: WorkforceCategory
    total_count: int | None = Count
    hr_training_covered: int | None = Count
    equal_min_wage_male: int | None = Count
    equal_min_wage_female: int | None = Count
    more_than_min_wage_male: int | None = Count
    more_than_min_wage_female: int | None = Count
    remarks: str | None = None


class WorkforceCoverageCreate(WorkforceCoverageBase):
    pass


class WorkforceCoverageUpdate(BaseModel):
    category: WorkforceCategory | None = None
    total_count: int | None = Count
    hr_training_covered: int | None = Count
    equal_min_wage_male: int | None = Count
    equal_min_wage_female: int | None = Count
    more_than_min_wage_male: int | None = Count
    more_than_min_wage_female: int | None = Count
    remarks: str | None = None


class WorkforceCoverageResponse(WorkforceCoverageBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    human_rights_record_id: int
    # Derived: covered / total * 100, None unless both counts present and total > 0.
    hr_training_coverage_percent: float | None = None
    created_at: datetime
    updated_at: datetime | None = None


# ---- Remuneration (EI 3) ----
class RemunerationBase(BaseModel):
    category: RemunerationCategory
    male_count: int | None = Count
    male_median_inr: float | None = Money
    female_count: int | None = Count
    female_median_inr: float | None = Money
    remarks: str | None = None


class RemunerationCreate(RemunerationBase):
    pass


class RemunerationUpdate(BaseModel):
    category: RemunerationCategory | None = None
    male_count: int | None = Count
    male_median_inr: float | None = Money
    female_count: int | None = Count
    female_median_inr: float | None = Money
    remarks: str | None = None


class RemunerationResponse(RemunerationBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    human_rights_record_id: int
    created_at: datetime
    updated_at: datetime | None = None


# ---- Complaints (EI 6) ----
class ComplaintBase(BaseModel):
    category: ComplaintCategory
    filed_count: int | None = Count
    pending_count: int | None = Count
    remarks: str | None = None


class ComplaintCreate(ComplaintBase):
    pass


class ComplaintUpdate(BaseModel):
    category: ComplaintCategory | None = None
    filed_count: int | None = Count
    pending_count: int | None = Count
    remarks: str | None = None


class ComplaintResponse(ComplaintBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    human_rights_record_id: int
    created_at: datetime
    updated_at: datetime | None = None


# ---- Parent ----
class HumanRightsFields(BaseModel):
    # EI 4, 5, 7, 8
    has_human_rights_focal_point: bool | None = None
    focal_point_details: str | None = None
    grievance_mechanism_details: str | None = None
    complainant_protection_details: str | None = None
    hr_requirements_in_contracts: bool | None = None
    hr_requirements_details: str | None = None
    # EI 9, 10
    assessed_child_labour_percent: float | None = Pct
    assessed_forced_labour_percent: float | None = Pct
    assessed_sexual_harassment_percent: float | None = Pct
    assessed_discrimination_percent: float | None = Pct
    assessed_wages_percent: float | None = Pct
    assessed_other_percent: float | None = Pct
    assessed_other_description: str | None = None
    corrective_actions_from_assessments: str | None = None
    # Leadership
    process_modifications_from_grievances: str | None = None
    human_rights_due_diligence_details: str | None = None
    premises_accessible_to_differently_abled: bool | None = None
    accessibility_details: str | None = None
    value_chain_partners_assessed_percent: float | None = Pct
    value_chain_assessment_details: str | None = None
    value_chain_corrective_actions: str | None = None
    remarks: str | None = None


class HumanRightsRecordCreate(HumanRightsFields):
    reporting_year: int = Field(..., ge=2000, le=2100)


class HumanRightsRecordUpdate(HumanRightsFields):
    reporting_year: int | None = Field(None, ge=2000, le=2100)


class HumanRightsRecordResponse(HumanRightsFields):
    model_config = ConfigDict(from_attributes=True)
    id: int
    organization_id: int
    reporting_year: int
    workforce_coverage: list[WorkforceCoverageResponse] = []
    remuneration: list[RemunerationResponse] = []
    complaints: list[ComplaintResponse] = []
    # Derived from complaint rows -- never stored.
    total_complaints_filed: int | None = None
    total_complaints_pending: int | None = None
    created_at: datetime
    updated_at: datetime | None = None
