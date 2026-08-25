"""Pydantic schemas for StakeholderEngagementRecord and StakeholderGroup."""
from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class StakeholderGroupBase(BaseModel):
    group_name: str = Field(..., min_length=1, max_length=255)
    is_vulnerable_marginalized: bool | None = None
    communication_channels: str | None = None
    frequency_of_engagement: str | None = Field(None, max_length=100)
    purpose_and_scope: str | None = None
    remarks: str | None = None


class StakeholderGroupCreate(StakeholderGroupBase):
    pass


class StakeholderGroupUpdate(BaseModel):
    group_name: str | None = Field(None, min_length=1, max_length=255)
    is_vulnerable_marginalized: bool | None = None
    communication_channels: str | None = None
    frequency_of_engagement: str | None = Field(None, max_length=100)
    purpose_and_scope: str | None = None
    remarks: str | None = None


class StakeholderGroupResponse(StakeholderGroupBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    engagement_record_id: int
    created_at: datetime
    updated_at: datetime | None = None


class StakeholderEngagementRecordBase(BaseModel):
    reporting_year: int = Field(..., ge=2000, le=2100)
    has_consultation_process: bool | None = None
    consultation_process_details: str | None = None
    resulted_in_policy_change: bool | None = None
    policy_change_details: str | None = None
    remarks: str | None = None


class StakeholderEngagementRecordCreate(StakeholderEngagementRecordBase):
    pass


class StakeholderEngagementRecordUpdate(BaseModel):
    reporting_year: int | None = Field(None, ge=2000, le=2100)
    has_consultation_process: bool | None = None
    consultation_process_details: str | None = None
    resulted_in_policy_change: bool | None = None
    policy_change_details: str | None = None
    remarks: str | None = None


class StakeholderEngagementRecordResponse(StakeholderEngagementRecordBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    organization_id: int
    stakeholder_groups: list[StakeholderGroupResponse] = []
    created_at: datetime
    updated_at: datetime | None = None
