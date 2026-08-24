"""
BRSR Section C, Principle 8 (Transparent & Inclusive Growth) - CSR spend
and project details for one reporting year.

Applicability (csr_applicable, turnover/net-worth thresholds) already
lives in BrsrOrganizationProfile (Section A, Q22) -- this table is
deliberately NOT re-asking that. It only holds what Section A doesn't:
the actual amount spent and the projects it went to.

% spent vs budgeted is NOT stored -- always derived
(actual/budgeted * 100) in the service, same never-store-a-derived-
total discipline as water/waste and PAT SEC.
"""
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Numeric,
    ForeignKey,
    DateTime,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base


class CsrRecord(Base):
    __tablename__ = "csr_records"
    __table_args__ = (
        CheckConstraint(
            "reporting_year >= 2000 AND reporting_year <= 2100",
            name="ck_csr_record_year_range",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(
        Integer,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    reporting_year = Column(Integer, nullable=False, index=True)

    # 2% mandate under Companies Act 2013, s.135 -- what SHOULD be spent.
    csr_budget_inr = Column(Numeric(18, 2), nullable=True)
    # What actually went out the door this year.
    csr_amount_spent_inr = Column(Numeric(18, 2), nullable=True)
    # Admin overhead is capped at 5% of total CSR spend under the Act --
    # tracked separately so that cap is checkable, not folded into total spend.
    csr_admin_overhead_inr = Column(Numeric(18, 2), nullable=True)

    remarks = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    organization = relationship("Organization")
    projects = relationship(
        "CsrProject", back_populates="csr_record", cascade="all, delete-orphan"
    )


class CsrProject(Base):
    """One CSR project/activity funded within a CsrRecord's year -- a
    one-to-many child, since a company typically runs several CSR
    initiatives (education, health, environment...) per year."""
    __tablename__ = "csr_projects"

    id = Column(Integer, primary_key=True, index=True)
    csr_record_id = Column(
        Integer,
        ForeignKey("csr_records.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    project_name = Column(String(255), nullable=False)
    # Schedule VII of the Companies Act names permitted CSR categories
    # (education, health, environment, rural development...) -- free text
    # since entities phrase these differently, not a rigid enum here.
    activity_category = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    # SEBI distinguishes local-area vs other-area CSR spend.
    is_local_area = Column(String(10), nullable=True)  # "yes" / "no" / "partial"
    amount_spent_inr = Column(Numeric(18, 2), nullable=True)
    direct_beneficiaries_count = Column(Integer, nullable=True)
    remarks = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    csr_record = relationship("CsrRecord", back_populates="projects")
