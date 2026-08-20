from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


# The nine NGRBC principles, as named by SEBI. Kept server-side so the
# frontend and any report renderer share one wording rather than each
# hard-coding its own.
PRINCIPLE_LABELS: Dict[int, str] = {
    1: "Ethics, transparency and accountability",
    2: "Sustainable and safe goods and services",
    3: "Well-being of employees",
    4: "Stakeholder engagement",
    5: "Human rights",
    6: "Environment protection and restoration",
    7: "Responsible public policy advocacy",
    8: "Inclusive growth and equitable development",
    9: "Value to consumers in a responsible manner",
}


class BrsrPolicyDisclosureBase(BaseModel):
    has_policy: Optional[bool] = None
    policy_board_approved: Optional[bool] = None
    policy_web_link: Optional[str] = None
    translated_to_procedures: Optional[bool] = None
    extends_to_value_chain: Optional[bool] = None
    certifications: Optional[str] = None
    commitments_and_targets: Optional[str] = None
    performance_against_targets: Optional[str] = None
    reason_no_policy: Optional[str] = None


class BrsrPolicyDisclosureUpdate(BrsrPolicyDisclosureBase):
    """One principle's disclosure. `principle` identifies which row to upsert."""
    principle: int = Field(ge=1, le=9)


class BrsrPolicyBulkUpdate(BaseModel):
    """
    Save several principles in one request.

    The Section B form is filled as one screen with nine tabs, so the client
    submits whatever it has rather than issuing nine separate calls.
    """
    disclosures: List[BrsrPolicyDisclosureUpdate] = Field(min_length=1)


class BrsrPolicyDisclosureRead(BrsrPolicyDisclosureBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: int
    principle: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
