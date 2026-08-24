"""
BRSR Section C, Principle 1 (Ethics, Transparency & Accountability) --
anti-corruption training, disciplinary actions, and complaints for one
reporting year.

Training percentages are NOT stored -- always derived
(trained_count / total_count * 100) in the service, same
never-store-a-derived-total discipline as PAT SEC, water/waste, CSR.
"""
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Numeric,
    ForeignKey,
    DateTime,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base


class EthicsRecord(Base):
    __tablename__ = "ethics_records"
    __table_args__ = (
        CheckConstraint(
            "reporting_year >= 2000 AND reporting_year <= 2100",
            name="ck_ethics_record_year_range",
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

    # --- Anti-corruption/anti-bribery training coverage ---
    # SEBI asks board-of-directors and KMP (key managerial personnel)
    # separately from the rest of the workforce -- different governance
    # weight, so kept as distinct counts rather than one pooled figure.
    board_kmp_total_count = Column(Integer, nullable=True)
    board_kmp_trained_count = Column(Integer, nullable=True)
    employees_total_count = Column(Integer, nullable=True)
    employees_trained_count = Column(Integer, nullable=True)
    workers_total_count = Column(Integer, nullable=True)
    workers_trained_count = Column(Integer, nullable=True)

    # --- Disciplinary actions & fines (corruption/conflict-of-interest) ---
    disciplinary_actions_directors = Column(Integer, nullable=True)
    disciplinary_actions_kmp = Column(Integer, nullable=True)
    disciplinary_actions_employees = Column(Integer, nullable=True)
    disciplinary_actions_workers = Column(Integer, nullable=True)
    fines_penalties_amount_inr = Column(Numeric(18, 2), nullable=True)

    # --- Conflict of interest ---
    # SEBI wants a yes/no on whether a defined process exists, plus
    # count of directors/KMP with a disclosed conflict this year.
    has_conflict_of_interest_process = Column(String(10), nullable=True)  # yes/no
    conflict_of_interest_disclosures_count = Column(Integer, nullable=True)

    # --- Anti-corruption complaints ---
    corruption_complaints_received = Column(Integer, nullable=True)
    corruption_complaints_pending = Column(Integer, nullable=True)

    remarks = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    organization = relationship("Organization")
