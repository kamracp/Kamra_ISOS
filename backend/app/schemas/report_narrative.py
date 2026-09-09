import re
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, field_validator

HEX_COLOUR = re.compile(r"^#[0-9A-Fa-f]{6}$")

# UN SDG short names, served at GET /report-narratives/sdgs so the
# frontend never keeps a second copy.
SDG_LABELS = {
    1: "No Poverty", 2: "Zero Hunger", 3: "Good Health and Well-being",
    4: "Quality Education", 5: "Gender Equality",
    6: "Clean Water and Sanitation", 7: "Affordable and Clean Energy",
    8: "Decent Work and Economic Growth",
    9: "Industry, Innovation and Infrastructure",
    10: "Reduced Inequalities", 11: "Sustainable Cities and Communities",
    12: "Responsible Consumption and Production", 13: "Climate Action",
    14: "Life Below Water", 15: "Life on Land",
    16: "Peace, Justice and Strong Institutions",
    17: "Partnerships for the Goals",
}


class Milestone(BaseModel):
    year: int = Field(..., ge=1900, le=2100)
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None


class PrincipleNarrative(BaseModel):
    principle: int = Field(..., ge=1, le=9)
    highlight: Optional[str] = None
    intro: Optional[str] = None
    sdgs: List[int] = Field(default_factory=list)

    @field_validator("sdgs")
    @classmethod
    def _sdgs_in_range(cls, v: List[int]) -> List[int]:
        bad = [s for s in v if s not in SDG_LABELS]
        if bad:
            raise ValueError(f"unknown SDG number(s): {bad} (valid: 1-17)")
        return sorted(set(v))


class ReportNarrativeBase(BaseModel):
    cover_title: Optional[str] = Field(None, max_length=255)
    cover_subtitle: Optional[str] = Field(None, max_length=255)
    theme_colour: Optional[str] = Field(None, max_length=7)
    about_company: Optional[str] = None
    leadership_message: Optional[str] = None
    leadership_name: Optional[str] = Field(None, max_length=150)
    leadership_designation: Optional[str] = Field(None, max_length=150)
    milestones: Optional[List[Milestone]] = None
    principle_narratives: Optional[List[PrincipleNarrative]] = None

    @field_validator("theme_colour")
    @classmethod
    def _hex_colour(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v == "":
            return None
        if not HEX_COLOUR.match(v):
            raise ValueError("theme_colour must be #RRGGBB")
        return v.upper()

    @field_validator("principle_narratives")
    @classmethod
    def _unique_principles(cls, v):
        if v is None:
            return v
        seen = [p.principle for p in v]
        dupes = sorted({p for p in seen if seen.count(p) > 1})
        if dupes:
            raise ValueError(f"principle listed more than once: {dupes}")
        return sorted(v, key=lambda p: p.principle)


class ReportNarrativeUpdate(ReportNarrativeBase):
    """PUT payload - every field optional; exclude_unset gives partial update."""
    pass


class ReportNarrativeResponse(ReportNarrativeBase):
    id: int
    organization_id: int
    reporting_year: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
