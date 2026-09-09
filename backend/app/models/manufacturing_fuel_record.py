"""
Manufacturing Fuel Record model.

One fuel consumption entry for a ManufacturingUnit + period: a fuel from
cross_sector_ef_library (54 IPCC fuels) and the tonnes consumed. This is
the missing input the platform never had -- process emissions live in
ManufacturingEmissionRecord and electricity in ManufacturingElectricityRecord,
but fuel *combustion* had no home outside BENAS utility bills.

One entry feeds every pillar without re-entry:
  Energy Efficiency : tonnes x LHV (TJ/Gg = GJ/t) -> GJ, toe, thermal SEC
  Carbon Accounting : tonnes x co2e_kg_per_tonne -> Scope 1 combustion
                      (biogenic CO2 reported separately per the library flag)
  ESG (P6 EI 1)     : energy consumption by fuel
  Product LCA       : energy per functional unit

Quantities are in tonnes only. Volumetric fuels (Nm3 gas, litres oil)
must be converted with a stated density before entry -- the density and
source go in `remarks`. A native-unit column would invite silent
unit errors in the GJ/CO2e chain.
"""
from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

FUEL_PURPOSES = ("process_heat", "captive_power", "steam_boiler", "transport", "other")


class ManufacturingFuelRecord(Base):
    __tablename__ = "manufacturing_fuel_records"
    __table_args__ = (
        CheckConstraint("quantity_tonnes >= 0", name="ck_mfg_fuel_quantity_non_negative"),
        CheckConstraint("period_end >= period_start", name="ck_mfg_fuel_period_order"),
        CheckConstraint(
            "purpose IN ('process_heat', 'captive_power', 'steam_boiler', 'transport', 'other')",
            name="ck_mfg_fuel_purpose",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    manufacturing_unit_id: Mapped[int] = mapped_column(
        ForeignKey("manufacturing_units.id", ondelete="CASCADE"), nullable=False, index=True
    )
    period_start: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    period_end: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    # Key into cross_sector_ef_library.FUEL_LIBRARY (e.g. "bituminous_coal",
    # "natural_gas", "diesel"). Validated against the library in the schema;
    # LHV and emission factors are looked up at read time, never stored.
    fuel_key: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    quantity_tonnes: Mapped[float] = mapped_column(Float, nullable=False)
    purpose: Mapped[str] = mapped_column(String(30), nullable=False, default="process_heat")
    # Traceability note (invoice, weighbridge, density used for conversion).
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
