"""
Energy Production Record model (Manufacturing / Energy module)
Period-wise MEASURED energy consumption and production quantity for
a manufacturing unit -- the raw data actual SEC is computed from.
toe (tonne of oil equivalent, BEE's official reporting unit) is
deliberately NOT stored -- always derived from energy_consumed_gj at
read time via the standard conversion (1 toe = 41.868 GJ), same
never-store-a-derived-total discipline as water/waste and PAT targets.
"""
from __future__ import annotations
from datetime import date, datetime
from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class EnergyProductionRecord(Base):
    __tablename__ = "energy_production_records"
    __table_args__ = (
        CheckConstraint(
            "period_end >= period_start", name="ck_epr_period_order"
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
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)

    # Sum of ALL energy forms (grid electricity + fuels + steam etc.)
    # converted to GJ -- the platform's canonical energy unit.
    energy_consumed_gj: Mapped[float] = mapped_column(Float, nullable=False)

    production_quantity: Mapped[float] = mapped_column(Float, nullable=False)
    # Must match the unit's PatCycleTarget.production_unit for a valid
    # SEC comparison -- checked in the service, not the DB.
    production_unit: Mapped[str] = mapped_column(String(50), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    organization = relationship("Organization")
    manufacturing_unit = relationship("ManufacturingUnit")
