"""
Net Zero Target model.

An organization's decarbonization commitment: reduce emissions by
X% from a baseline year, by a target year. Modeled loosely on
SBTi (Science Based Targets initiative) near-term/long-term target
structure. Optionally scoped to one Building or ManufacturingUnit
(facility-specific target) -- org-wide if both are null.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class NetZeroTarget(Base):
    __tablename__ = "net_zero_targets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Optional facility scoping -- null on both = org-wide target.
    building_id: Mapped[int | None] = mapped_column(
        ForeignKey("buildings.id", ondelete="SET NULL"), nullable=True
    )
    manufacturing_unit_id: Mapped[int | None] = mapped_column(
        ForeignKey("manufacturing_units.id", ondelete="SET NULL"), nullable=True
    )

    target_name: Mapped[str] = mapped_column(String(150), nullable=False)

    baseline_year: Mapped[int] = mapped_column(Integer, nullable=False)
    baseline_co2e_tonnes: Mapped[float] = mapped_column(Float, nullable=False)

    target_year: Mapped[int] = mapped_column(Integer, nullable=False)
    reduction_percentage: Mapped[float] = mapped_column(Float, nullable=False)

    # "near_term" (SBTi 5-10yr) or "long_term" (net zero, typically 2050)
    target_type: Mapped[str] = mapped_column(String(20), nullable=False, default="near_term")

    scope_coverage: Mapped[str] = mapped_column(
        String(50), nullable=False, default="scope_1_2"
    )  # "scope_1_2", "scope_1_2_3"

    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    organization = relationship("Organization")
    building = relationship("Building")
    manufacturing_unit = relationship("ManufacturingUnit")
