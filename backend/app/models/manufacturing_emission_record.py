"""
Manufacturing Emission Record model.

Persists the result (and full input traceability) of one sector-specific
GHG Protocol calculator run for a ManufacturingUnit + period -- e.g. one
Cement CSI clinker-calcination calculation, one Aluminium Tier-1 run.

Why this exists: the sector calculators (aluminium/cement/iron_steel/
pulp_paper/refrigerant/chp) are on-demand functions needing detailed
process inputs (e.g. CaO%/MgO% for cement) that ProductionRecord does
not carry. This table is where a calculation, once run, is saved --
so ManufacturingCarbonService can later sum results across all units
of an organization without recomputing, exactly mirroring how
CarbonService sums bills. calculator_inputs is stored as JSON so each
sector's distinct input shape doesn't need its own set of columns.
"""
from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.manufacturing_unit import PatSector


class ManufacturingEmissionRecord(Base):
    __tablename__ = "manufacturing_emission_records"

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

    sector: Mapped[PatSector] = mapped_column(nullable=False, index=True)

    period_start: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    period_end: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # Which calculator produced this result -- e.g. "cement_csi_stoichiometric",
    # "aluminium_tier1_default", "iron_steel_mass_balance", "pulp_paper_biomass",
    # "refrigerant_lifecycle", "chp_efficiency_allocation". Free text, not an
    # enum, since new sector calculators get added over time.
    calculation_source: Mapped[str] = mapped_column(String(60), nullable=False)

    # Full inputs the calculator was run with (e.g. {"clinker_produced_tonnes":
    # 1000, "cao_content_percent": 0.65, "mgo_content_percent": 0.01}) --
    # audit traceability, mirrors why BillEmission keeps factor_id/factor_value.
    calculator_inputs: Mapped[dict] = mapped_column(JSONB, nullable=False)

    co2_tonnes: Mapped[float] = mapped_column(Float, nullable=False)

    # True for biogenic CO2 (e.g. Pulp & Paper biomass combustion) -- per
    # GHG Protocol convention, reported separately, never summed into the
    # fossil Scope 1 total. Mirrors CarbonService's renewable-meter handling.
    is_biogenic: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    organization = relationship("Organization")
    manufacturing_unit = relationship("ManufacturingUnit")
