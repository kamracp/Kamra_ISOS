"""Pydantic schemas for PolicyAdvocacyRecord and TradeAssociation."""
from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class TradeAssociationBase(BaseModel):
    association_name: str = Field(..., min_length=1, max_length=255)
    reach: str | None = Field(None, max_length=50)
    remarks: str | None = None


class TradeAssociationCreate(TradeAssociationBase):
    pass


class TradeAssociationUpdate(BaseModel):
    association_name: str | None = Field(None, min_length=1, max_length=255)
    reach: str | None = Field(None, max_length=50)
    remarks: str | None = None


class TradeAssociationResponse(TradeAssociationBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    policy_advocacy_record_id: int
    created_at: datetime
    updated_at: datetime | None = None


class PolicyAdvocacyRecordBase(BaseModel):
    reporting_year: int = Field(..., ge=2000, le=2100)
    has_anti_competitive_conduct_issue: bool | None = None
    anti_competitive_conduct_details: str | None = None
    corrective_action_taken: str | None = None
    remarks: str | None = None


class PolicyAdvocacyRecordCreate(PolicyAdvocacyRecordBase):
    pass


class PolicyAdvocacyRecordUpdate(BaseModel):
    reporting_year: int | None = Field(None, ge=2000, le=2100)
    has_anti_competitive_conduct_issue: bool | None = None
    anti_competitive_conduct_details: str | None = None
    corrective_action_taken: str | None = None
    remarks: str | None = None


class PolicyAdvocacyRecordResponse(PolicyAdvocacyRecordBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    organization_id: int
    associations: list[TradeAssociationResponse] = []
    created_at: datetime
    updated_at: datetime | None = None
