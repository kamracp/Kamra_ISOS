"""
Climate Risk model (TCFD-aligned).
A physical or transition climate risk the organization faces, with
financial quantification following the TCFD (Task Force on
Climate-related Financial Disclosures) recommendations:
Net Risk Exposure (Rs) = Estimated Financial Impact - Mitigation Benefit
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


class RiskCategory(str, enum.Enum):
    PHYSICAL_ACUTE = "physical_acute"
    PHYSICAL_CHRONIC = "physical_chronic"
    TRANSITION_POLICY_LEGAL = "transition_policy_legal"
    TRANSITION_TECHNOLOGY = "transition_technology"
    TRANSITION_MARKET = "transition_market"
    TRANSITION_REPUTATION = "transition_reputation"


class RiskTimeHorizon(str, enum.Enum):
    SHORT_TERM = "short_term"      # 0-3 years
    MEDIUM_TERM = "medium_term"    # 3-10 years
    LONG_TERM = "long_term"        # 10+ years


class RiskLikelihood(str, enum.Enum):
    UNLIKELY = "unlikely"
    POSSIBLE = "possible"
    LIKELY = "likely"
    ALMOST_CERTAIN = "almost_certain"


class ClimateRisk(Base):
    __tablename__ = "climate_risks"

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

    risk_name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[RiskCategory] = mapped_column(nullable=False)
    time_horizon: Mapped[RiskTimeHorizon] = mapped_column(nullable=False)
    likelihood: Mapped[RiskLikelihood] = mapped_column(nullable=False)

    estimated_financial_impact_inr: Mapped[float] = mapped_column(
        Float, nullable=False
    )  # potential loss/cost if the risk materializes (Rs)
    mitigation_cost_inr: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0
    )  # cost of the mitigation action (Rs)
    mitigation_benefit_inr: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0
    )  # risk reduction value from mitigation (Rs)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    mitigation_action: Mapped[str | None] = mapped_column(Text, nullable=True)
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
