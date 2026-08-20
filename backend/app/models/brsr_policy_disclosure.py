from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    ForeignKey,
    DateTime,
    CheckConstraint,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class BrsrPolicyDisclosure(Base):
    """
    BRSR Section B - Management and Process Disclosures.

    One row per NGRBC principle (1-9) per organization. The SEBI form asks
    the SAME questions for every principle, so this is one shape repeated
    nine times rather than nine different shapes - hence a child table with
    nine rows, not nine sets of columns and not a JSONB blob.

    A child table is the right call here (unlike Section A's JSONB blocks)
    because these rows ARE queried: completeness counts them, and reports
    read them principle by principle.

    Booleans are nullable on purpose: "not answered yet" must stay
    distinguishable from an explicit "no", or the completeness figure starts
    claiming disclosures that were never made.
    """

    __tablename__ = "brsr_policy_disclosures"
    __table_args__ = (
        UniqueConstraint(
            "organization_id", "principle", name="uq_brsr_policy_org_principle"
        ),
        CheckConstraint(
            "principle >= 1 AND principle <= 9", name="ck_brsr_policy_principle_range"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(
        Integer,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # NGRBC principle number, 1-9. Kept as an integer rather than an enum:
    # SEBI identifies these by number, and a future tenth principle would
    # need no schema change.
    principle = Column(Integer, nullable=False)

    # --- Q1 Policy and management processes ---
    has_policy = Column(Boolean, nullable=True)              # Q1a
    policy_board_approved = Column(Boolean, nullable=True)   # Q1b
    policy_web_link = Column(String(500), nullable=True)     # Q1c

    # --- Q2 Translated into procedures ---
    translated_to_procedures = Column(Boolean, nullable=True)

    # --- Q3 Extends to value chain partners ---
    extends_to_value_chain = Column(Boolean, nullable=True)

    # --- Q4 Certifications / standards adopted for this principle ---
    certifications = Column(Text, nullable=True)

    # --- Q5 Specific commitments, goals and targets ---
    commitments_and_targets = Column(Text, nullable=True)

    # --- Q6 Performance against those targets ---
    performance_against_targets = Column(Text, nullable=True)

    # --- Q12 Reason if the entity does not have a policy ---
    # Free text: SEBI lists fixed reason codes, but entities routinely add
    # their own wording, so a constrained enum would force bad fits.
    reason_no_policy = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    organization = relationship("Organization")
