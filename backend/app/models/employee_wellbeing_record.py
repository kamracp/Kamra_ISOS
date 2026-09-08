"""
BRSR Section C, Principle 3 (Employee Well-being) -- one organization's P3
disclosures for one reporting year. SEBI's largest principle; mapping:

  EI 1  well-being measures by workforce category x gender -> EmployeeWellbeingMeasure
  EI 2  spend on well-being (% of revenue)                 -> parent
  EI 3  retirement benefits (PF/gratuity/ESI/other)        -> parent (12 columns)
  EI 4  accessibility, EI 5 equal opportunity policy       -> parent
  EI 6  parental leave return / retention rates            -> EmployeeWellbeingParentalLeave
  EI 7  union membership                                   -> parent (counts; % derived)
  EI 8/9 training and performance reviews                  -> EmployeeWellbeingTraining
  EI 10 OHS management system, EI 11 safety incidents,
  EI 12 safe workplace, EI 14 complainant protection,
  EI 15 assessments                                        -> parent
  EI 13 complaints (working conditions / health & safety)  -> EmployeeWellbeingComplaint
  Leadership indicators                                    -> parent

Percentages against a total (well-being coverage, union %, training %)
are derived in the service from counts and never stored.
"""
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Numeric,
    ForeignKey, DateTime, CheckConstraint, UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base

GENDER_CATEGORIES = (
    "permanent_employees_male", "permanent_employees_female",
    "other_employees_male", "other_employees_female",
    "permanent_workers_male", "permanent_workers_female",
    "other_workers_male", "other_workers_female",
)
PARENTAL_CATEGORIES = ("employees_male", "employees_female", "workers_male", "workers_female")
TRAINING_CATEGORIES = (
    "permanent_employees_male", "permanent_employees_female",
    "permanent_workers_male", "permanent_workers_female",
)
COMPLAINT_CATEGORIES = (
    "working_conditions_employees", "health_safety_employees",
    "working_conditions_workers", "health_safety_workers",
)
DEPOSIT_STATUS = ("yes", "no", "na")


def _pct_check(col, name):
    return CheckConstraint(f"{col} IS NULL OR ({col} >= 0 AND {col} <= 100)", name=name)


def _nonneg(cols, name):
    return CheckConstraint(" AND ".join(f"({c} IS NULL OR {c} >= 0)" for c in cols), name=name)


def _in(col, values, name):
    return CheckConstraint(f"{col} IN ({', '.join(repr(v) for v in values)})", name=name)


_PCT_COLS = (
    "wellbeing_spend_percent_revenue",
    "pf_employees_percent", "pf_workers_percent",
    "gratuity_employees_percent", "gratuity_workers_percent",
    "esi_employees_percent", "esi_workers_percent",
    "other_benefit_employees_percent", "other_benefit_workers_percent",
    "assessed_health_safety_percent", "assessed_working_conditions_percent",
    "value_chain_assessed_health_safety_percent", "value_chain_assessed_working_conditions_percent",
)
_COUNT_COLS = (
    "permanent_employees_total", "permanent_employees_union_members",
    "permanent_workers_total", "permanent_workers_union_members",
    "recordable_injuries_employees", "recordable_injuries_workers",
    "fatalities_employees", "fatalities_workers",
    "high_consequence_injuries_employees", "high_consequence_injuries_workers",
    "rehabilitated_employees_count", "rehabilitated_workers_count",
    "ltifr_employees", "ltifr_workers",
)


class EmployeeWellbeingRecord(Base):
    __tablename__ = "employee_wellbeing_records"
    __table_args__ = (
        UniqueConstraint("organization_id", "reporting_year", name="uq_employee_wellbeing_org_year"),
        CheckConstraint("reporting_year >= 2000 AND reporting_year <= 2100", name="ck_employee_wellbeing_year_range"),
        *[_pct_check(c, f"ck_ewb_{c}_pct") for c in _PCT_COLS],
        _nonneg(_COUNT_COLS, "ck_employee_wellbeing_non_negative"),
        *[_in(f"{b}_deposited", DEPOSIT_STATUS, f"ck_ewb_{b}_deposited") for b in ("pf", "gratuity", "esi", "other_benefit")],
    )

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    reporting_year = Column(Integer, nullable=False, index=True)

    # EI 2
    wellbeing_spend_percent_revenue = Column(Numeric(6, 2), nullable=True)

    # EI 3 -- retirement benefits: % of employees / % of workers covered,
    # and whether deductions are deposited with the authority (yes/no/na).
    pf_employees_percent = Column(Numeric(6, 2), nullable=True)
    pf_workers_percent = Column(Numeric(6, 2), nullable=True)
    pf_deposited = Column(String(3), nullable=True)
    gratuity_employees_percent = Column(Numeric(6, 2), nullable=True)
    gratuity_workers_percent = Column(Numeric(6, 2), nullable=True)
    gratuity_deposited = Column(String(3), nullable=True)
    esi_employees_percent = Column(Numeric(6, 2), nullable=True)
    esi_workers_percent = Column(Numeric(6, 2), nullable=True)
    esi_deposited = Column(String(3), nullable=True)
    other_benefit_name = Column(String(255), nullable=True)
    other_benefit_employees_percent = Column(Numeric(6, 2), nullable=True)
    other_benefit_workers_percent = Column(Numeric(6, 2), nullable=True)
    other_benefit_deposited = Column(String(3), nullable=True)

    # EI 4, 5
    premises_accessible_to_differently_abled = Column(Boolean, nullable=True)
    accessibility_details = Column(Text, nullable=True)
    has_equal_opportunity_policy = Column(Boolean, nullable=True)
    equal_opportunity_policy_link = Column(String(500), nullable=True)

    # EI 7 -- union membership (counts; % derived).
    permanent_employees_total = Column(Integer, nullable=True)
    permanent_employees_union_members = Column(Integer, nullable=True)
    permanent_workers_total = Column(Integer, nullable=True)
    permanent_workers_union_members = Column(Integer, nullable=True)

    # EI 10 -- occupational health and safety.
    has_ohs_management_system = Column(Boolean, nullable=True)
    ohs_system_coverage = Column(Text, nullable=True)
    hazard_identification_process = Column(Text, nullable=True)
    non_routine_risk_reporting_process = Column(Text, nullable=True)
    has_medical_facilities = Column(Boolean, nullable=True)
    safety_assessments_details = Column(Text, nullable=True)

    # EI 11 -- safety incidents. LTIFR per one million person-hours.
    ltifr_employees = Column(Numeric(8, 3), nullable=True)
    ltifr_workers = Column(Numeric(8, 3), nullable=True)
    recordable_injuries_employees = Column(Integer, nullable=True)
    recordable_injuries_workers = Column(Integer, nullable=True)
    fatalities_employees = Column(Integer, nullable=True)
    fatalities_workers = Column(Integer, nullable=True)
    high_consequence_injuries_employees = Column(Integer, nullable=True)
    high_consequence_injuries_workers = Column(Integer, nullable=True)

    # EI 12, 14, 15
    safe_workplace_measures = Column(Text, nullable=True)
    complainant_protection_details = Column(Text, nullable=True)
    assessed_health_safety_percent = Column(Numeric(6, 2), nullable=True)
    assessed_working_conditions_percent = Column(Numeric(6, 2), nullable=True)
    corrective_actions_from_assessments = Column(Text, nullable=True)

    # Leadership Indicators.
    life_insurance_employees = Column(Boolean, nullable=True)
    life_insurance_workers = Column(Boolean, nullable=True)
    value_chain_statutory_dues_details = Column(Text, nullable=True)
    rehabilitated_employees_count = Column(Integer, nullable=True)
    rehabilitated_workers_count = Column(Integer, nullable=True)
    has_transition_assistance = Column(Boolean, nullable=True)
    value_chain_assessed_health_safety_percent = Column(Numeric(6, 2), nullable=True)
    value_chain_assessed_working_conditions_percent = Column(Numeric(6, 2), nullable=True)
    value_chain_corrective_actions = Column(Text, nullable=True)

    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    organization = relationship("Organization")
    wellbeing_measures = relationship("EmployeeWellbeingMeasure", back_populates="record", cascade="all, delete-orphan")
    parental_leave = relationship("EmployeeWellbeingParentalLeave", back_populates="record", cascade="all, delete-orphan")
    training = relationship("EmployeeWellbeingTraining", back_populates="record", cascade="all, delete-orphan")
    complaints = relationship("EmployeeWellbeingComplaint", back_populates="record", cascade="all, delete-orphan")


def _fk():
    return Column(Integer, ForeignKey("employee_wellbeing_records.id", ondelete="CASCADE"), nullable=False, index=True)


class EmployeeWellbeingMeasure(Base):
    """EI 1 -- well-being measures, one row per workforce category x gender.
    Counts of those covered; coverage % derived in the service."""
    __tablename__ = "employee_wellbeing_measures"
    __table_args__ = (
        _in("category", GENDER_CATEGORIES, "ck_ewb_measure_category"),
        _nonneg(("total_count", "health_insurance", "accident_insurance", "maternity_benefits",
                 "paternity_benefits", "day_care_facilities"), "ck_ewb_measure_non_negative"),
    )
    id = Column(Integer, primary_key=True, index=True)
    employee_wellbeing_record_id = _fk()
    category = Column(String(50), nullable=False)
    total_count = Column(Integer, nullable=True)
    health_insurance = Column(Integer, nullable=True)
    accident_insurance = Column(Integer, nullable=True)
    maternity_benefits = Column(Integer, nullable=True)
    paternity_benefits = Column(Integer, nullable=True)
    day_care_facilities = Column(Integer, nullable=True)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    record = relationship("EmployeeWellbeingRecord", back_populates="wellbeing_measures")


class EmployeeWellbeingParentalLeave(Base):
    """EI 6 -- return-to-work and retention rates after parental leave."""
    __tablename__ = "employee_wellbeing_parental_leave"
    __table_args__ = (
        _in("category", PARENTAL_CATEGORIES, "ck_ewb_parental_category"),
        _pct_check("return_to_work_rate_percent", "ck_ewb_parental_return_pct"),
        _pct_check("retention_rate_percent", "ck_ewb_parental_retention_pct"),
    )
    id = Column(Integer, primary_key=True, index=True)
    employee_wellbeing_record_id = _fk()
    category = Column(String(50), nullable=False)
    return_to_work_rate_percent = Column(Numeric(6, 2), nullable=True)
    retention_rate_percent = Column(Numeric(6, 2), nullable=True)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    record = relationship("EmployeeWellbeingRecord", back_populates="parental_leave")


class EmployeeWellbeingTraining(Base):
    """EI 8 (health & safety and skill upgradation training) and EI 9
    (performance and career development reviews), permanent workforce x gender."""
    __tablename__ = "employee_wellbeing_training"
    __table_args__ = (
        _in("category", TRAINING_CATEGORIES, "ck_ewb_training_category"),
        _nonneg(("total_count", "health_safety_trained", "skill_upgraded", "performance_reviewed"),
                "ck_ewb_training_non_negative"),
    )
    id = Column(Integer, primary_key=True, index=True)
    employee_wellbeing_record_id = _fk()
    category = Column(String(50), nullable=False)
    total_count = Column(Integer, nullable=True)
    health_safety_trained = Column(Integer, nullable=True)
    skill_upgraded = Column(Integer, nullable=True)
    performance_reviewed = Column(Integer, nullable=True)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    record = relationship("EmployeeWellbeingRecord", back_populates="training")


class EmployeeWellbeingComplaint(Base):
    """EI 13 -- complaints on working conditions and health & safety."""
    __tablename__ = "employee_wellbeing_complaints"
    __table_args__ = (
        _in("category", COMPLAINT_CATEGORIES, "ck_ewb_complaint_category"),
        _nonneg(("filed_count", "pending_count"), "ck_ewb_complaint_non_negative"),
    )
    id = Column(Integer, primary_key=True, index=True)
    employee_wellbeing_record_id = _fk()
    category = Column(String(50), nullable=False)
    filed_count = Column(Integer, nullable=True)
    pending_count = Column(Integer, nullable=True)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    record = relationship("EmployeeWellbeingRecord", back_populates="complaints")
