"""
PAT Cycle Target model (Manufacturing / Energy module)
Stores BEE PAT-notified baseline and mandated reduction target for a
manufacturing unit in a given PAT cycle. Target SEC is deliberately
NOT stored -- it is always derived (baseline_sec * (1 - reduction%))
so there is never a second version of the truth that can disagree
with its own inputs (same principle as water/waste totals).
"""
from __future__ import annotations
from datetime import datetime
from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class PatCycleTarget(Base):
    __tablename__ = "pat_cycle_targets"
    __table_args__ = (
        UniqueConstraint(
            "manufacturing_unit_id",
            "cycle_number",
            name="uq_pat_target_unit_cycle",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    manufacturing_unit_id: Mapped[int] = mapped_column(
        ForeignKey("manufacturing_units.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    cycle_number: Mapped[int] = mapped_column(Integer, nullable=False)
    cycle_start_year: Mapped[int] = mapped_column(Integer, nullable=False)
    cycle_end_year: Mapped[int] = mapped_column(Integer, nullable=False)

    # Baseline year's MEASURED values -- real data, not a policy figure.
    baseline_production_qty: Mapped[float] = mapped_column(Float, nullable=False)
    production_unit: Mapped[str] = mapped_column(String(50), nullable=False)
    baseline_energy_gj: Mapped[float] = mapped_column(Float, nullable=False)

    # BEE-notified mandated reduction -- a policy figure, stored as-is.
    mandated_reduction_percent: Mapped[float] = mapped_column(Float, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    organization = relationship("Organization")
    manufacturing_unit = relationship("ManufacturingUnit")
