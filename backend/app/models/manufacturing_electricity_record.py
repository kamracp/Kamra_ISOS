"""
Manufacturing Electricity Record model.
Persists purchased/grid electricity consumption for a ManufacturingUnit
+ period -- the Scope 2 counterpart to ManufacturingEmissionRecord
(Scope 1 process emissions). Unlike Scope 1, which stores a computed
co2_tonnes result, Scope 2 CO2e is NEVER stored here: it is derived
at read time in ManufacturingCarbonService by looking up the unit's
country_code in app.services.country_config and multiplying the grid
factor against (electricity_consumed_kwh - renewable_kwh). This keeps
Scope 2 always in step with the latest verified grid factor for that
country, rather than freezing a value computed against a factor that
may later be corrected/updated.
"""
from __future__ import annotations
from datetime import date, datetime
from sqlalchemy import (
    Date,
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


class ManufacturingElectricityRecord(Base):
    __tablename__ = "manufacturing_electricity_records"

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
    period_start: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    period_end: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    electricity_consumed_kwh: Mapped[float] = mapped_column(Float, nullable=False)
    # Portion of electricity_consumed_kwh sourced from on-site or
    # contracted renewables (solar, WHRS-generated power, REC-backed
    # purchase) -- excluded from the grid-factor Scope 2 calculation,
    # same convention as CarbonService's renewable-meter handling.
    renewable_kwh: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    # Free-text traceability note (e.g. "utility bill #4521", "smart
    # meter reading") -- not an enum, sources vary too widely.
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    organization = relationship("Organization")
    manufacturing_unit = relationship("ManufacturingUnit")
