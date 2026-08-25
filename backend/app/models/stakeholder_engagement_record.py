"""
BRSR Section C, Principle 4 (Stakeholder Responsiveness) -- stakeholder
group identification and consultation process for one reporting year.

SEBI's Essential Indicators: (1) a list of stakeholder groups identified,
whether each is vulnerable/marginalized, the communication channels used,
and engagement frequency; (2) whether consultation with stakeholders on
economic/environmental/social topics occurred, and whether it led to
policy or activity changes. Parent/child shape mirrors CsrRecord/CsrProject
and PolicyAdvocacyRecord/TradeAssociation -- several stakeholder groups
per reporting year.
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


class StakeholderEngagementRecord(Base):
    __tablename__ = "stakeholder_engagement_records"
    __table_args__ = (
        CheckConstraint(
            "reporting_year >= 2000 AND reporting_year <= 2100",
            name="ck_stakeholder_engagement_record_year_range",
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

    # SEBI EI 2: was there consultation with stakeholders on economic,
    # environmental, and social topics this year?
    has_consultation_process = Column(Boolean, nullable=True)
    consultation_process_details = Column(Text, nullable=True)
    # SEBI asks specifically whether consultation resulted in changes to
    # policy or activities -- distinct from whether consultation happened.
    resulted_in_policy_change = Column(Boolean, nullable=True)
    policy_change_details = Column(Text, nullable=True)

    remarks = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    organization = relationship("Organization")
    stakeholder_groups = relationship(
        "StakeholderGroup", back_populates="engagement_record",
        cascade="all, delete-orphan",
    )


class StakeholderGroup(Base):
    """One stakeholder group identified within a
    StakeholderEngagementRecord's year -- a one-to-many child, since an
    organization typically identifies several (employees, communities,
    investors, suppliers...) at once."""
    __tablename__ = "stakeholder_groups"

    id = Column(Integer, primary_key=True, index=True)
    engagement_record_id = Column(
        Integer,
        ForeignKey("stakeholder_engagement_records.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    group_name = Column(String(255), nullable=False)
    is_vulnerable_marginalized = Column(Boolean, nullable=True)
    # SEBI lists channels (e.g. sustainability report, website, meetings,
    # notice board) -- free text since entities describe combinations.
    communication_channels = Column(Text, nullable=True)
    # SEBI names discrete bands (annually/half-yearly/quarterly/others) --
    # free text here since entities phrase these differently.
    frequency_of_engagement = Column(String(100), nullable=True)
    purpose_and_scope = Column(Text, nullable=True)
    remarks = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    engagement_record = relationship("StakeholderEngagementRecord", back_populates="stakeholder_groups")
