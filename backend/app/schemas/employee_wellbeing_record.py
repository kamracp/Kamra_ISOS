"""Pydantic schemas for EmployeeWellbeingRecord and its four child tables (BRSR Principle 3)."""
from __future__ import annotations
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict

GenderCategory = Literal[
    "permanent_employees_male", "permanent_employees_female", "other_employees_male", "other_employees_female",
    "permanent_workers_male", "permanent_workers_female", "other_workers_male", "other_workers_female",
]
ParentalCategory = Literal["employees_male", "employees_female", "workers_male", "workers_female"]
TrainingCategory = Literal["permanent_employees_male", "permanent_employees_female", "permanent_workers_male", "permanent_workers_female"]
WellbeingComplaintCategory = Literal["working_conditions_employees", "health_safety_employees", "working_conditions_workers", "health_safety_workers"]
DepositStatus = Literal["yes", "no", "na"]

Pct = Field(None, ge=0, le=100)
Count = Field(None, ge=0)
Rate = Field(None, ge=0)


class _ChildMeta(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    employee_wellbeing_record_id: int
    created_at: datetime
    updated_at: datetime | None = None


# ---- EI 1 well-being measures ----
class MeasureBase(BaseModel):
    category: GenderCategory
    total_count: int | None = Count
    health_insurance: int | None = Count
    accident_insurance: int | None = Count
    maternity_benefits: int | None = Count
    paternity_benefits: int | None = Count
    day_care_facilities: int | None = Count
    remarks: str | None = None

class MeasureCreate(MeasureBase): pass

class MeasureUpdate(BaseModel):
    category: GenderCategory | None = None
    total_count: int | None = Count
    health_insurance: int | None = Count
    accident_insurance: int | None = Count
    maternity_benefits: int | None = Count
    paternity_benefits: int | None = Count
    day_care_facilities: int | None = Count
    remarks: str | None = None

class MeasureResponse(MeasureBase, _ChildMeta):
    # Derived coverage % per benefit (None unless both counts present, total > 0).
    health_insurance_percent: float | None = None
    accident_insurance_percent: float | None = None
    maternity_benefits_percent: float | None = None
    paternity_benefits_percent: float | None = None
    day_care_facilities_percent: float | None = None


# ---- EI 6 parental leave ----
class ParentalLeaveBase(BaseModel):
    category: ParentalCategory
    return_to_work_rate_percent: float | None = Pct
    retention_rate_percent: float | None = Pct
    remarks: str | None = None

class ParentalLeaveCreate(ParentalLeaveBase): pass

class ParentalLeaveUpdate(BaseModel):
    category: ParentalCategory | None = None
    return_to_work_rate_percent: float | None = Pct
    retention_rate_percent: float | None = Pct
    remarks: str | None = None

class ParentalLeaveResponse(ParentalLeaveBase, _ChildMeta): pass


# ---- EI 8/9 training ----
class TrainingBase(BaseModel):
    category: TrainingCategory
    total_count: int | None = Count
    health_safety_trained: int | None = Count
    skill_upgraded: int | None = Count
    performance_reviewed: int | None = Count
    remarks: str | None = None

class TrainingCreate(TrainingBase): pass

class TrainingUpdate(BaseModel):
    category: TrainingCategory | None = None
    total_count: int | None = Count
    health_safety_trained: int | None = Count
    skill_upgraded: int | None = Count
    performance_reviewed: int | None = Count
    remarks: str | None = None

class TrainingResponse(TrainingBase, _ChildMeta):
    health_safety_trained_percent: float | None = None
    skill_upgraded_percent: float | None = None
    performance_reviewed_percent: float | None = None


# ---- EI 13 complaints ----
class WellbeingComplaintBase(BaseModel):
    category: WellbeingComplaintCategory
    filed_count: int | None = Count
    pending_count: int | None = Count
    remarks: str | None = None

class WellbeingComplaintCreate(WellbeingComplaintBase): pass

class WellbeingComplaintUpdate(BaseModel):
    category: WellbeingComplaintCategory | None = None
    filed_count: int | None = Count
    pending_count: int | None = Count
    remarks: str | None = None

class WellbeingComplaintResponse(WellbeingComplaintBase, _ChildMeta): pass


# ---- Parent ----
class EmployeeWellbeingFields(BaseModel):
    wellbeing_spend_percent_revenue: float | None = Pct
    pf_employees_percent: float | None = Pct
    pf_workers_percent: float | None = Pct
    pf_deposited: DepositStatus | None = None
    gratuity_employees_percent: float | None = Pct
    gratuity_workers_percent: float | None = Pct
    gratuity_deposited: DepositStatus | None = None
    esi_employees_percent: float | None = Pct
    esi_workers_percent: float | None = Pct
    esi_deposited: DepositStatus | None = None
    other_benefit_name: str | None = Field(None, max_length=255)
    other_benefit_employees_percent: float | None = Pct
    other_benefit_workers_percent: float | None = Pct
    other_benefit_deposited: DepositStatus | None = None
    premises_accessible_to_differently_abled: bool | None = None
    accessibility_details: str | None = None
    has_equal_opportunity_policy: bool | None = None
    equal_opportunity_policy_link: str | None = Field(None, max_length=500)
    permanent_employees_total: int | None = Count
    permanent_employees_union_members: int | None = Count
    permanent_workers_total: int | None = Count
    permanent_workers_union_members: int | None = Count
    has_ohs_management_system: bool | None = None
    ohs_system_coverage: str | None = None
    hazard_identification_process: str | None = None
    non_routine_risk_reporting_process: str | None = None
    has_medical_facilities: bool | None = None
    safety_assessments_details: str | None = None
    ltifr_employees: float | None = Rate
    ltifr_workers: float | None = Rate
    recordable_injuries_employees: int | None = Count
    recordable_injuries_workers: int | None = Count
    fatalities_employees: int | None = Count
    fatalities_workers: int | None = Count
    high_consequence_injuries_employees: int | None = Count
    high_consequence_injuries_workers: int | None = Count
    safe_workplace_measures: str | None = None
    complainant_protection_details: str | None = None
    assessed_health_safety_percent: float | None = Pct
    assessed_working_conditions_percent: float | None = Pct
    corrective_actions_from_assessments: str | None = None
    life_insurance_employees: bool | None = None
    life_insurance_workers: bool | None = None
    value_chain_statutory_dues_details: str | None = None
    rehabilitated_employees_count: int | None = Count
    rehabilitated_workers_count: int | None = Count
    has_transition_assistance: bool | None = None
    value_chain_assessed_health_safety_percent: float | None = Pct
    value_chain_assessed_working_conditions_percent: float | None = Pct
    value_chain_corrective_actions: str | None = None
    remarks: str | None = None


class EmployeeWellbeingRecordCreate(EmployeeWellbeingFields):
    reporting_year: int = Field(..., ge=2000, le=2100)


class EmployeeWellbeingRecordUpdate(EmployeeWellbeingFields):
    reporting_year: int | None = Field(None, ge=2000, le=2100)


class EmployeeWellbeingRecordResponse(EmployeeWellbeingFields):
    model_config = ConfigDict(from_attributes=True)
    id: int
    organization_id: int
    reporting_year: int
    wellbeing_measures: list[MeasureResponse] = []
    parental_leave: list[ParentalLeaveResponse] = []
    training: list[TrainingResponse] = []
    complaints: list[WellbeingComplaintResponse] = []
    # Derived on read.
    permanent_employees_union_percent: float | None = None
    permanent_workers_union_percent: float | None = None
    total_complaints_filed: int | None = None
    total_complaints_pending: int | None = None
    created_at: datetime
    updated_at: datetime | None = None
