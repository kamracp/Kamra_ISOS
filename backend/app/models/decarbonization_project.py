"""
Decarbonization Project model.

A candidate or in-progress project that reduces emissions (Solar PV,
Waste Heat Recovery, Fuel Switching, Energy Efficiency, Electrification,
CCUS, etc.). Feeds the MACC (Marginal Abatement Cost Curve) engine:
MAC ($/tCO2e) = (Annualized CAPEX + Annual delta-OPEX) / Annual tCO2e abated.
"""
from __future__ import annotations

import enum
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


class ProjectCategory(str, enum.Enum):
    ENERGY_EFFICIENCY = "energy_efficiency"
    RENEWABLE_GENERATION = "renewable_generation"
    FUEL_SWITCHING = "fuel_switching"
    WASTE_HEAT_RECOVERY = "waste_heat_recovery"
    ELECTRIFICATION = "electrification"
    CCUS = "ccus"
    OTHER = "other"


class ProjectStatus(str, enum.Enum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class DecarbonizationProject(Base):
    __tablename__ = "decarbonization_projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    building_id: Mapped[int | None] = mapped_column(
        ForeignKey("buildings.id", ondelete="SET NULL"), nullable=True
    )
    manufacturing_unit_id: Mapped[int | None] = mapped_column(
        ForeignKey("manufacturing_units.id", ondelete="SET NULL"), nullable=True
    )

    project_name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[ProjectCategory] = mapped_column(nullable=False)
    status: Mapped[ProjectStatus] = mapped_column(nullable=False, default=ProjectStatus.PROPOSED)

    capex: Mapped[float] = mapped_column(Float, nullable=False)
    annual_opex_delta: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0
    )  # positive = costs more to run, negative = saves running cost
    lifespan_years: Mapped[int] = mapped_column(Integer, nullable=False)

    annual_co2e_abated_tonnes: Mapped[float] = mapped_column(Float, nullable=False)

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
