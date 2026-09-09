from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class ReportNarrative(Base):
    """
    Report Studio - editorial content for one organization's report in one
    reporting year: cover, about-us, leadership message, milestones and the
    per-principle highlight/intro/SDG mapping.

    One row per (organization, year). Kept off Organization on purpose:
    narrative text changes every year while the entity does not.

    Scalars are real columns. `milestones` and `principle_narratives` are
    JSONB because they are read only when a report is rendered - never
    filtered or aggregated in SQL - so child tables would cost without
    benefit. Their shape is enforced by nested Pydantic models at the API
    boundary (loose storage, strict validation - the Section A pattern).

    JSONB shapes:
      milestones: [{"year": 2019, "title": "...", "description": "..."}]
      principle_narratives: [{"principle": 6, "highlight": "...",
                               "intro": "...", "sdgs": [7, 13]}]
    """

    __tablename__ = "report_narratives"
    __table_args__ = (
        UniqueConstraint(
            "organization_id", "reporting_year",
            name="uq_report_narratives_org_year",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(
        Integer,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    reporting_year = Column(Integer, nullable=False)

    # Cover page
    cover_title = Column(String(255), nullable=True)
    cover_subtitle = Column(String(255), nullable=True)
    theme_colour = Column(String(7), nullable=True)  # "#RRGGBB"

    # About the company / leadership message
    about_company = Column(Text, nullable=True)
    leadership_message = Column(Text, nullable=True)
    leadership_name = Column(String(150), nullable=True)
    leadership_designation = Column(String(150), nullable=True)

    # Repeating blocks (see class docstring for shapes)
    milestones = Column(JSONB, nullable=True)
    principle_narratives = Column(JSONB, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    organization = relationship("Organization")
