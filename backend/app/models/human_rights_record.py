"""
BRSR Section C, Principle 5 (Human Rights) -- one organization's P5
disclosures for one reporting year.

SEBI Essential Indicators map as follows:
  Q1 training coverage, Q2 minimum wages -> HumanRightsWorkforceCoverage
     (one row per workforce category)
  Q3 remuneration medians                -> HumanRightsRemuneration
     (one row per SEBI remuneration category)
  Q4 focal point, Q5 grievance mechanism, Q7 complainant protection,
  Q8 HR clauses in contracts, Q9 assessment coverage %, Q10 corrective
  actions                                -> scalar columns on the parent
  Q6 complaints                          -> HumanRightsComplaint
     (one row per complaint category)
Leadership Indicators are scalar columns on the parent.

Percentages (training coverage %, wage-band %) are derived in the
service from counts and never stored -- same rule as water/waste and P2.
"""
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    Numeric,
    ForeignKey,
    DateTime,
    CheckConstraint,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base

WORKFORCE_CATEGORIES = ("permanent_employees", "other_employees", "permanent_workers", "other_workers")
REMUNERATION_CATEGORIES = ("bod", "kmp", "employees", "workers")
COMPLAINT_CATEGORIES = ("sexual_harassment", "discrimination", "child_labour", "forced_labour", "wages", "other")


def _pct_check(col: str, name: str) -> CheckConstraint:
    return CheckConstraint(f"{col} IS NULL OR ({col} >= 0 AND {col} <= 100)", name=name)


class HumanRightsRecord(Base):
    __tablename__ = "human_rights_records"
    __table_args__ = (
        UniqueConstraint("organization_id", "reporting_year", name="uq_human_rights_record_org_year"),
        CheckConstraint("reporting_year >= 2000 AND reporting_year <= 2100", name="ck_human_rights_record_year_range"),
        _pct_check("assessed_child_labour_percent", "ck_hr_assessed_child_labour_pct"),
        _pct_check("assessed_forced_labour_percent", "ck_hr_assessed_forced_labour_pct"),
        _pct_check("assessed_sexual_harassment_percent", "ck_hr_assessed_sexual_harassment_pct"),
        _pct_check("assessed_discrimination_percent", "ck_hr_assessed_discrimination_pct"),
        _pct_check("assessed_wages_percent", "ck_hr_assessed_wages_pct"),
        _pct_check("assessed_other_percent", "ck_hr_assessed_other_pct"),
        _pct_check("value_chain_partners_assessed_percent", "ck_hr_value_chain_assessed_pct"),
    )

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    reporting_year = Column(Integer, nullable=False, index=True)

    # EI 4, 5, 7, 8 -- nullable booleans keep "not answered" distinct from "No".
    has_human_rights_focal_point = Column(Boolean, nullable=True)
    focal_point_details = Column(Text, nullable=True)
    grievance_mechanism_details = Column(Text, nullable=True)
    complainant_protection_details = Column(Text, nullable=True)
    hr_requirements_in_contracts = Column(Boolean, nullable=True)
    hr_requirements_details = Column(Text, nullable=True)

    # EI 9 -- % of plants/offices assessed by the entity or statutory
    # authorities / third parties, per topic.
    assessed_child_labour_percent = Column(Numeric(6, 2), nullable=True)
    assessed_forced_labour_percent = Column(Numeric(6, 2), nullable=True)
    assessed_sexual_harassment_percent = Column(Numeric(6, 2), nullable=True)
    assessed_discrimination_percent = Column(Numeric(6, 2), nullable=True)
    assessed_wages_percent = Column(Numeric(6, 2), nullable=True)
    assessed_other_percent = Column(Numeric(6, 2), nullable=True)
    assessed_other_description = Column(Text, nullable=True)
    # EI 10
    corrective_actions_from_assessments = Column(Text, nullable=True)

    # Leadership Indicators.
    process_modifications_from_grievances = Column(Text, nullable=True)
    human_rights_due_diligence_details = Column(Text, nullable=True)
    premises_accessible_to_differently_abled = Column(Boolean, nullable=True)
    accessibility_details = Column(Text, nullable=True)
    value_chain_partners_assessed_percent = Column(Numeric(6, 2), nullable=True)
    value_chain_assessment_details = Column(Text, nullable=True)
    value_chain_corrective_actions = Column(Text, nullable=True)

    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    organization = relationship("Organization")
    workforce_coverage = relationship(
        "HumanRightsWorkforceCoverage", back_populates="record", cascade="all, delete-orphan"
    )
    remuneration = relationship(
        "HumanRightsRemuneration", back_populates="record", cascade="all, delete-orphan"
    )
    complaints = relationship(
        "HumanRightsComplaint", back_populates="record", cascade="all, delete-orphan"
    )


class HumanRightsWorkforceCoverage(Base):
    """EI 1 (training) and EI 2 (minimum wages), one row per SEBI workforce
    category. Only counts are stored; coverage % and wage-band % are
    derived in the service."""
    __tablename__ = "human_rights_workforce_coverage"
    __table_args__ = (
        CheckConstraint(
            "category IN ('permanent_employees', 'other_employees', 'permanent_workers', 'other_workers')",
            name="ck_hr_workforce_category",
        ),
        CheckConstraint(
            "(total_count IS NULL OR total_count >= 0) AND "
            "(hr_training_covered IS NULL OR hr_training_covered >= 0) AND "
            "(equal_min_wage_male IS NULL OR equal_min_wage_male >= 0) AND "
            "(equal_min_wage_female IS NULL OR equal_min_wage_female >= 0) AND "
            "(more_than_min_wage_male IS NULL OR more_than_min_wage_male >= 0) AND "
            "(more_than_min_wage_female IS NULL OR more_than_min_wage_female >= 0)",
            name="ck_hr_workforce_non_negative",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    human_rights_record_id = Column(
        Integer, ForeignKey("human_rights_records.id", ondelete="CASCADE"), nullable=False, index=True
    )
    category = Column(String(50), nullable=False)
    total_count = Column(Integer, nullable=True)
    hr_training_covered = Column(Integer, nullable=True)
    equal_min_wage_male = Column(Integer, nullable=True)
    equal_min_wage_female = Column(Integer, nullable=True)
    more_than_min_wage_male = Column(Integer, nullable=True)
    more_than_min_wage_female = Column(Integer, nullable=True)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    record = relationship("HumanRightsRecord", back_populates="workforce_coverage")


class HumanRightsRemuneration(Base):
    """EI 3 -- median remuneration by gender, one row per SEBI category
    (Board of Directors, KMP, employees other than BoD/KMP, workers).
    Medians are in INR per annum as disclosed; no aggregation is derived
    across categories (a median of medians is meaningless)."""
    __tablename__ = "human_rights_remuneration"
    __table_args__ = (
        CheckConstraint("category IN ('bod', 'kmp', 'employees', 'workers')", name="ck_hr_remuneration_category"),
        CheckConstraint(
            "(male_count IS NULL OR male_count >= 0) AND (female_count IS NULL OR female_count >= 0) AND "
            "(male_median_inr IS NULL OR male_median_inr >= 0) AND (female_median_inr IS NULL OR female_median_inr >= 0)",
            name="ck_hr_remuneration_non_negative",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    human_rights_record_id = Column(
        Integer, ForeignKey("human_rights_records.id", ondelete="CASCADE"), nullable=False, index=True
    )
    category = Column(String(50), nullable=False)
    male_count = Column(Integer, nullable=True)
    male_median_inr = Column(Numeric(14, 2), nullable=True)
    female_count = Column(Integer, nullable=True)
    female_median_inr = Column(Numeric(14, 2), nullable=True)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    record = relationship("HumanRightsRecord", back_populates="remuneration")


class HumanRightsComplaint(Base):
    """EI 6 -- complaints on human rights issues, one row per SEBI
    category: filed during the year and pending at year end."""
    __tablename__ = "human_rights_complaints"
    __table_args__ = (
        CheckConstraint(
            "category IN ('sexual_harassment', 'discrimination', 'child_labour', 'forced_labour', 'wages', 'other')",
            name="ck_hr_complaint_category",
        ),
        CheckConstraint(
            "(filed_count IS NULL OR filed_count >= 0) AND (pending_count IS NULL OR pending_count >= 0)",
            name="ck_hr_complaint_non_negative",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    human_rights_record_id = Column(
        Integer, ForeignKey("human_rights_records.id", ondelete="CASCADE"), nullable=False, index=True
    )
    category = Column(String(50), nullable=False)
    filed_count = Column(Integer, nullable=True)
    pending_count = Column(Integer, nullable=True)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    record = relationship("HumanRightsRecord", back_populates="complaints")
