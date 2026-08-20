from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Numeric,
    Boolean,
    ForeignKey,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class BrsrOrganizationProfile(Base):
    """
    BRSR Section A - General Disclosures.

    Kept as a separate 1:1 table rather than extra columns on Organization,
    so that regulatory reporting fields never bloat the core org model.

    Scalar regulatory fields are real columns.
    Repeating disclosure blocks (products, locations, employees, holdings)
    are JSONB: they are write-once / read-for-report only, never filtered
    or aggregated in SQL, so child tables would add cost without benefit.
    """

    __tablename__ = "brsr_organization_profile"
    __table_args__ = (
        UniqueConstraint("organization_id", name="uq_brsr_profile_organization"),
    )

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(
        Integer,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # --- A.I Details of the listed entity (Q1-Q13) ---
    cin = Column(String(50), nullable=True)                      # Q1
    year_of_incorporation = Column(Integer, nullable=True)       # Q3
    registered_office_address = Column(Text, nullable=True)      # Q4
    corporate_address = Column(Text, nullable=True)              # Q5
    contact_email = Column(String(255), nullable=True)           # Q6
    contact_telephone = Column(String(50), nullable=True)        # Q7
    website = Column(String(255), nullable=True)                 # Q8
    financial_year_reported = Column(String(20), nullable=True)  # Q9 e.g. "2025-26"
    stock_exchanges_listed = Column(JSONB, nullable=True)        # Q10 list[str]
    paid_up_capital_inr = Column(Numeric(20, 2), nullable=True)  # Q11
    brsr_contact_name = Column(String(255), nullable=True)       # Q12
    brsr_contact_phone = Column(String(50), nullable=True)       # Q12
    brsr_contact_email = Column(String(255), nullable=True)      # Q12

    # Q13 reporting boundary: "standalone" | "consolidated"
    reporting_boundary = Column(String(20), nullable=True)

    # --- A.II Products and services (Q14-Q15) ---
    # Q14 -> [{"description": str, "nic_code": str, "turnover_percent": float}]
    business_activities = Column(JSONB, nullable=True)
    # Q15 -> [{"product_service": str, "nic_code": str, "turnover_percent": float}]
    products_sold = Column(JSONB, nullable=True)

    # --- A.III Operations (Q16-Q17) ---
    # Q16 -> {"plants": {"national": int, "international": int},
    #         "offices": {"national": int, "international": int}}
    location_counts = Column(JSONB, nullable=True)
    # Q17 -> {"national_states": int, "international_countries": int,
    #         "exports_percent": float, "customer_types": str}
    markets_served = Column(JSONB, nullable=True)

    # --- A.IV Employees (Q18-Q20) ---
    # Q18 -> {"employees": {"permanent": {...}, "other": {...}},
    #         "workers":   {"permanent": {...}, "other": {...}}}
    # each inner block: {"total": int, "male": int, "female": int}
    employee_worker_counts = Column(JSONB, nullable=True)
    # Q18b differently abled, same shape as above
    differently_abled_counts = Column(JSONB, nullable=True)
    # Q19 -> {"board_total": int, "board_female": int,
    #         "kmp_total": int, "kmp_female": int}
    women_participation = Column(JSONB, nullable=True)
    # Q20 -> [{"year": "2025-26", "category": "permanent_employees",
    #          "male_turnover_percent": float, "female_turnover_percent": float,
    #          "total_turnover_percent": float}]
    turnover_rates = Column(JSONB, nullable=True)

    # --- A.V Holding / subsidiary / associate (Q21) ---
    # -> [{"name": str, "relationship": str, "shareholding_percent": float,
    #      "participates_in_brsr": bool}]
    group_companies = Column(JSONB, nullable=True)

    # --- A.VI CSR details (Q22) ---
    csr_applicable = Column(Boolean, nullable=True)
    csr_turnover_inr = Column(Numeric(20, 2), nullable=True)
    csr_net_worth_inr = Column(Numeric(20, 2), nullable=True)

    # --- A.VII Transparency and disclosures (Q23) ---
    # -> [{"stakeholder_group": str, "grievance_mechanism": str,
    #      "filed_current_year": int, "pending_current_year": int,
    #      "filed_previous_year": int, "pending_previous_year": int}]
    grievance_redressal = Column(JSONB, nullable=True)

    # --- A.VIII Assurance (Q25-Q26) ---
    assurance_provider_name = Column(String(255), nullable=True)
    assurance_type = Column(String(100), nullable=True)

    # --- Section B, entity-level questions (Q10-Q12) ---
    # These three are asked once for the whole entity, not per principle, so
    # they live here rather than in brsr_policy_disclosures. They are counted
    # in Section B's completeness, NOT in SECTION_A_QUESTIONS.
    has_sustainability_committee = Column(Boolean, nullable=True)
    policy_review_frequency = Column(String(50), nullable=True)
    independent_assessment_agency = Column(String(255), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    organization = relationship("Organization")
