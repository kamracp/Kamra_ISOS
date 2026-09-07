"""
BRSR Section C, Principle 2 (Sustainable and Safe Goods and Services) --
one organization's P2 disclosures for one reporting year.

SEBI Essential Indicators: (1) % of R&D and capex on technologies
improving environmental/social impact, current vs previous FY;
(2) sustainable sourcing procedures and % of inputs sourced sustainably;
(3) processes to reclaim products for reuse/recycling/disposal, per
material category; (4) whether Extended Producer Responsibility applies
and whether the waste collection plan is in line with it.
Leadership Indicators: LCA conducted, recycled input %, reclaimed
products/packaging as % of products sold.

Parent/child shape mirrors PolicyAdvocacyRecord/TradeAssociation: the
reclaimed-quantity table (LI Q4) is one row per material category.
Totals across categories are never stored -- derived in the service,
same rule as water/waste (a persisted total is a second version of the
truth that can disagree with its own inputs).
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

RECLAIM_CATEGORIES = ("plastics", "e_waste", "hazardous", "other")


class SustainableProductRecord(Base):
    __tablename__ = "sustainable_product_records"
    __table_args__ = (
        UniqueConstraint(
            "organization_id", "reporting_year",
            name="uq_sustainable_product_record_org_year",
        ),
        CheckConstraint(
            "reporting_year >= 2000 AND reporting_year <= 2100",
            name="ck_sustainable_product_record_year_range",
        ),
        CheckConstraint(
            "rnd_sustainable_percent_current IS NULL OR "
            "(rnd_sustainable_percent_current >= 0 AND rnd_sustainable_percent_current <= 100)",
            name="ck_sustainable_product_rnd_current_pct",
        ),
        CheckConstraint(
            "rnd_sustainable_percent_previous IS NULL OR "
            "(rnd_sustainable_percent_previous >= 0 AND rnd_sustainable_percent_previous <= 100)",
            name="ck_sustainable_product_rnd_previous_pct",
        ),
        CheckConstraint(
            "capex_sustainable_percent_current IS NULL OR "
            "(capex_sustainable_percent_current >= 0 AND capex_sustainable_percent_current <= 100)",
            name="ck_sustainable_product_capex_current_pct",
        ),
        CheckConstraint(
            "capex_sustainable_percent_previous IS NULL OR "
            "(capex_sustainable_percent_previous >= 0 AND capex_sustainable_percent_previous <= 100)",
            name="ck_sustainable_product_capex_previous_pct",
        ),
        CheckConstraint(
            "sustainable_sourcing_percent IS NULL OR "
            "(sustainable_sourcing_percent >= 0 AND sustainable_sourcing_percent <= 100)",
            name="ck_sustainable_product_sourcing_pct",
        ),
        CheckConstraint(
            "recycled_input_percent IS NULL OR "
            "(recycled_input_percent >= 0 AND recycled_input_percent <= 100)",
            name="ck_sustainable_product_recycled_input_pct",
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

    # EI 1 -- R&D and capex on sustainable technologies (% of total).
    rnd_sustainable_percent_current = Column(Numeric(6, 2), nullable=True)
    rnd_sustainable_percent_previous = Column(Numeric(6, 2), nullable=True)
    capex_sustainable_percent_current = Column(Numeric(6, 2), nullable=True)
    capex_sustainable_percent_previous = Column(Numeric(6, 2), nullable=True)
    rnd_capex_details = Column(Text, nullable=True)

    # EI 2 -- sustainable sourcing. Nullable booleans throughout: an
    # unanswered question must stay distinct from an explicit "no".
    has_sustainable_sourcing_procedure = Column(Boolean, nullable=True)
    sustainable_sourcing_percent = Column(Numeric(6, 2), nullable=True)
    sustainable_sourcing_details = Column(Text, nullable=True)

    # EI 3 -- processes in place to reclaim products at end of life.
    reclaim_process_plastics = Column(Text, nullable=True)
    reclaim_process_e_waste = Column(Text, nullable=True)
    reclaim_process_hazardous = Column(Text, nullable=True)
    reclaim_process_other = Column(Text, nullable=True)

    # EI 4 -- Extended Producer Responsibility.
    epr_applicable = Column(Boolean, nullable=True)
    epr_plan_in_line = Column(Boolean, nullable=True)
    epr_details = Column(Text, nullable=True)

    # Leadership Indicators.
    has_conducted_lca = Column(Boolean, nullable=True)
    lca_details = Column(Text, nullable=True)
    recycled_input_percent = Column(Numeric(6, 2), nullable=True)
    reclaimed_products_percent_details = Column(Text, nullable=True)

    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    organization = relationship("Organization")
    reclaimed_materials = relationship(
        "ReclaimedMaterialRecord", back_populates="sustainable_product_record",
        cascade="all, delete-orphan",
    )


class ReclaimedMaterialRecord(Base):
    """Leadership Indicator Q4: quantity of reclaimed product/packaging
    material reused, recycled or safely disposed in the year, one row per
    SEBI material category (plastics, e-waste, hazardous, other)."""
    __tablename__ = "reclaimed_material_records"
    __table_args__ = (
        CheckConstraint(
            "material_category IN ('plastics', 'e_waste', 'hazardous', 'other')",
            name="ck_reclaimed_material_category",
        ),
        CheckConstraint(
            "(reused_mt IS NULL OR reused_mt >= 0) AND "
            "(recycled_mt IS NULL OR recycled_mt >= 0) AND "
            "(disposed_mt IS NULL OR disposed_mt >= 0)",
            name="ck_reclaimed_material_non_negative",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    sustainable_product_record_id = Column(
        Integer,
        ForeignKey("sustainable_product_records.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    material_category = Column(String(50), nullable=False)
    reused_mt = Column(Numeric(14, 3), nullable=True)
    recycled_mt = Column(Numeric(14, 3), nullable=True)
    disposed_mt = Column(Numeric(14, 3), nullable=True)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    sustainable_product_record = relationship(
        "SustainableProductRecord", back_populates="reclaimed_materials"
    )
