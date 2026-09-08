"""Pydantic schemas for ConsumerResponsibilityRecord + ConsumerComplaint (BRSR Principle 9)."""
from __future__ import annotations
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict

ConsumerComplaintCategory = Literal[
    "data_privacy", "advertising", "cyber_security", "delivery_of_essential_services",
    "restrictive_trade_practices", "unfair_trade_practices", "other",
]
Pct = Field(None, ge=0, le=100)
Count = Field(None, ge=0)


class ConsumerComplaintBase(BaseModel):
    category: ConsumerComplaintCategory
    received_count: int | None = Count
    pending_count: int | None = Count
    remarks: str | None = None


class ConsumerComplaintCreate(ConsumerComplaintBase):
    pass


class ConsumerComplaintUpdate(BaseModel):
    category: ConsumerComplaintCategory | None = None
    received_count: int | None = Count
    pending_count: int | None = Count
    remarks: str | None = None


class ConsumerComplaintResponse(ConsumerComplaintBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    consumer_responsibility_record_id: int
    created_at: datetime
    updated_at: datetime | None = None


class ConsumerResponsibilityFields(BaseModel):
    complaint_mechanism_details: str | None = None
    turnover_percent_env_social_info: float | None = Pct
    turnover_percent_safe_usage_info: float | None = Pct
    turnover_percent_recycling_info: float | None = Pct
    voluntary_recalls_count: int | None = Count
    voluntary_recalls_reasons: str | None = None
    forced_recalls_count: int | None = Count
    forced_recalls_reasons: str | None = None
    has_cyber_security_policy: bool | None = None
    cyber_security_policy_link: str | None = Field(None, max_length=500)
    corrective_actions_details: str | None = None
    product_information_channels: str | None = None
    consumer_education_details: str | None = None
    service_disruption_disclosure_details: str | None = None
    displays_product_info_beyond_mandate: bool | None = None
    consumer_survey_conducted: bool | None = None
    consumer_survey_details: str | None = None
    data_breaches_count: int | None = Count
    data_breach_pii_percent: float | None = Pct
    data_breach_impact_details: str | None = None
    remarks: str | None = None


class ConsumerResponsibilityRecordCreate(ConsumerResponsibilityFields):
    reporting_year: int = Field(..., ge=2000, le=2100)


class ConsumerResponsibilityRecordUpdate(ConsumerResponsibilityFields):
    reporting_year: int | None = Field(None, ge=2000, le=2100)


class ConsumerResponsibilityRecordResponse(ConsumerResponsibilityFields):
    model_config = ConfigDict(from_attributes=True)
    id: int
    organization_id: int
    reporting_year: int
    complaints: list[ConsumerComplaintResponse] = []
    total_complaints_received: int | None = None  # derived
    total_complaints_pending: int | None = None   # derived
    created_at: datetime
    updated_at: datetime | None = None
