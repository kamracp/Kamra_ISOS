"""
BRSR Section C, Principle 7 (Public and Regulatory Policy Advocacy) --
trade/industry association memberships and anti-competitive conduct
disclosures for one reporting year.

SEBI's two Essential Indicators: (1) affiliations with trade and
industry chambers/associations, listed with their reach; (2) details
of any corrective action taken on issues related to anti-competitive
conduct. Parent/child shape mirrors CsrRecord/CsrProject -- one
organization can belong to several associations in a given year.
"""
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    ForeignKey,
    DateTime,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base


class PolicyAdvocacyRecord(Base):
    __tablename__ = "policy_advocacy_records"
    __table_args__ = (
        CheckConstraint(
            "reporting_year >= 2000 AND reporting_year <= 2100",
            name="ck_policy_advocacy_record_year_range",
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

    # SEBI EI 2: was any corrective action required on anti-competitive
    # conduct this year? Nullable -- not-yet-answered stays distinct
    # from an explicit "no issues".
    has_anti_competitive_conduct_issue = Column(Boolean, nullable=True)
    anti_competitive_conduct_details = Column(Text, nullable=True)
    corrective_action_taken = Column(Text, nullable=True)

    remarks = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    organization = relationship("Organization")
    associations = relationship(
        "TradeAssociation", back_populates="policy_advocacy_record",
        cascade="all, delete-orphan",
    )


class TradeAssociation(Base):
    """One trade/industry chamber or association membership within a
    PolicyAdvocacyRecord's year -- a one-to-many child, since an
    organization typically belongs to several (CII, FICCI, ASSOCHAM,
    sector-specific bodies...) at once."""
    __tablename__ = "trade_associations"

    id = Column(Integer, primary_key=True, index=True)
    policy_advocacy_record_id = Column(
        Integer,
        ForeignKey("policy_advocacy_records.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    association_name = Column(String(255), nullable=False)
    # SEBI asks reach as National / State / District -- free text since
    # some entities describe it differently (e.g. "Regional").
    reach = Column(String(50), nullable=True)
    remarks = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    policy_advocacy_record = relationship("PolicyAdvocacyRecord", back_populates="associations")
