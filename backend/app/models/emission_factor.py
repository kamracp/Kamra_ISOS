from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class EmissionFactor(Base):
    """Official emission factor reference data.

    GLOBAL table — intentionally NO organization_id. Emission factors
    are published facts (CEA / DEFRA / IPCC), identical for every
    tenant, so all organizations read from this shared table.

    BENAS permanent rule: every row MUST carry its official source,
    publication year and validity window. Values come ONLY from
    official publications — never invented, never LLM-generated.
    """

    __tablename__ = "emission_factors"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    # Matches EnergyMeter.meter_type values:
    # electricity, diesel, natural_gas, lpg, water, solar_generation, other
    meter_type: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
        index=True,
    )

    # Consumption unit this factor applies to (kWh, litres, SCM, kg ...).
    # Must match the meter's unit for a valid calculation.
    unit: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    # kg CO2e emitted per one unit of consumption.
    factor_kgco2e_per_unit: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
# Energy content of one unit, in Gigajoules -- used for SEC (BEE PAT)
    # / EnPI (ISO 50001) calculations: Total Energy (GJ) / Production.
    # Nullable because not every factor row needs it (e.g. water).
    energy_content_gj_per_unit: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    # ISO country code the factor applies to (grid factors are national).
    region: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="IN",
        index=True,
    )

    # Official publication, e.g. "CEA CO2 Baseline Database v19".
    source: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    source_year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # Exact document / table / page reference for audit traceability.
    document_reference: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # Validity window: the engine picks the factor whose window
    # contains the bill's billing period.
    valid_from: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    # NULL = still valid (open-ended, current factor).
    valid_to: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
        index=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
