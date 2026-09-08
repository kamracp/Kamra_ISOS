"""
BRSR Section C, Principle 9 (Responsible Engagement with Consumers) --
one organization's P9 disclosures for one reporting year.

SEBI Essential Indicators: (1) consumer complaint/feedback mechanism;
(2) turnover % of products carrying information on environmental/social
parameters, safe usage and recycling; (3) product recalls, voluntary
and forced; (4) cyber security / data privacy policy; (5) corrective
actions. Leadership: product information channels, consumer education,
risk-of-disruption disclosure, product recall/withdrawal disclosure,
consumer survey, data breaches.

EI 6 complaints (seven SEBI categories) live in the child table, one row
per category; totals are derived in the service, never stored.
"""
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Numeric,
    ForeignKey, DateTime, CheckConstraint, UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base

COMPLAINT_CATEGORIES = (
    "data_privacy", "advertising", "cyber_security", "delivery_of_essential_services",
    "restrictive_trade_practices", "unfair_trade_practices", "other",
)


def _pct_check(col: str, name: str) -> CheckConstraint:
    return CheckConstraint(f"{col} IS NULL OR ({col} >= 0 AND {col} <= 100)", name=name)


class ConsumerResponsibilityRecord(Base):
    __tablename__ = "consumer_responsibility_records"
    __table_args__ = (
        UniqueConstraint("organization_id", "reporting_year", name="uq_consumer_responsibility_org_year"),
        CheckConstraint("reporting_year >= 2000 AND reporting_year <= 2100", name="ck_consumer_responsibility_year_range"),
        _pct_check("turnover_percent_env_social_info", "ck_cr_turnover_env_social_pct"),
        _pct_check("turnover_percent_safe_usage_info", "ck_cr_turnover_safe_usage_pct"),
        _pct_check("turnover_percent_recycling_info", "ck_cr_turnover_recycling_pct"),
        _pct_check("data_breach_pii_percent", "ck_cr_data_breach_pii_pct"),
        CheckConstraint(
            "(voluntary_recalls_count IS NULL OR voluntary_recalls_count >= 0) AND "
            "(forced_recalls_count IS NULL OR forced_recalls_count >= 0) AND "
            "(data_breaches_count IS NULL OR data_breaches_count >= 0)",
            name="ck_consumer_responsibility_non_negative",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    reporting_year = Column(Integer, nullable=False, index=True)

    # EI 1
    complaint_mechanism_details = Column(Text, nullable=True)
    # EI 2 -- turnover share of products/services carrying the information.
    turnover_percent_env_social_info = Column(Numeric(6, 2), nullable=True)
    turnover_percent_safe_usage_info = Column(Numeric(6, 2), nullable=True)
    turnover_percent_recycling_info = Column(Numeric(6, 2), nullable=True)
    # EI 3 -- product recalls.
    voluntary_recalls_count = Column(Integer, nullable=True)
    voluntary_recalls_reasons = Column(Text, nullable=True)
    forced_recalls_count = Column(Integer, nullable=True)
    forced_recalls_reasons = Column(Text, nullable=True)
    # EI 4
    has_cyber_security_policy = Column(Boolean, nullable=True)
    cyber_security_policy_link = Column(String(500), nullable=True)
    # EI 5
    corrective_actions_details = Column(Text, nullable=True)

    # Leadership Indicators.
    product_information_channels = Column(Text, nullable=True)
    consumer_education_details = Column(Text, nullable=True)
    service_disruption_disclosure_details = Column(Text, nullable=True)
    displays_product_info_beyond_mandate = Column(Boolean, nullable=True)
    consumer_survey_conducted = Column(Boolean, nullable=True)
    consumer_survey_details = Column(Text, nullable=True)
    data_breaches_count = Column(Integer, nullable=True)
    data_breach_pii_percent = Column(Numeric(6, 2), nullable=True)
    data_breach_impact_details = Column(Text, nullable=True)

    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    organization = relationship("Organization")
    complaints = relationship(
        "ConsumerComplaint", back_populates="record", cascade="all, delete-orphan"
    )


class ConsumerComplaint(Base):
    """EI 6 -- consumer complaints by SEBI category: received during the
    year and pending at year end."""
    __tablename__ = "consumer_complaints"
    __table_args__ = (
        CheckConstraint(
            "category IN ('data_privacy', 'advertising', 'cyber_security', 'delivery_of_essential_services', "
            "'restrictive_trade_practices', 'unfair_trade_practices', 'other')",
            name="ck_consumer_complaint_category",
        ),
        CheckConstraint(
            "(received_count IS NULL OR received_count >= 0) AND (pending_count IS NULL OR pending_count >= 0)",
            name="ck_consumer_complaint_non_negative",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    consumer_responsibility_record_id = Column(
        Integer, ForeignKey("consumer_responsibility_records.id", ondelete="CASCADE"), nullable=False, index=True
    )
    category = Column(String(50), nullable=False)
    received_count = Column(Integer, nullable=True)
    pending_count = Column(Integer, nullable=True)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    record = relationship("ConsumerResponsibilityRecord", back_populates="complaints")
