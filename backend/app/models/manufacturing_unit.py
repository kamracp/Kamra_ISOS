"""
Manufacturing Unit model (Phase 6 -- Manufacturing module)

Modeled on BEE PAT Scheme's "Designated Consumer" concept: an
energy-intensive plant tracked per sector, with a baseline year
against which future Specific Energy Consumption (SEC) is compared.

Kept fully separate from BENAS (Building/Real-Estate vertical) --
this is a distinct module, linked to Building only for physical
location/address reuse, not for BENAS feature sharing.
"""
from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class PatSector(str, enum.Enum):
    """Sectors covered under BEE PAT Scheme (grown across cycles)."""
    ALUMINIUM = "aluminium"
    CEMENT = "cement"
    CHLOR_ALKALI = "chlor_alkali"
    FERTILIZER = "fertilizer"
    IRON_STEEL = "iron_steel"
    PULP_PAPER = "pulp_paper"
    TEXTILE = "textile"
    THERMAL_POWER = "thermal_power"
    REFINERIES = "refineries"
    RAILWAYS = "railways"
    DISCOMS = "discoms"
    PETROCHEMICALS = "petrochemicals"
    OTHER = "other"


class ManufacturingUnit(Base):
    __tablename__ = "manufacturing_units"

    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "unit_code",
            name="uq_manufacturing_unit_org_code",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Optional link to Building for address/location reuse only --
    # NOT a BENAS feature-sharing relationship.
    building_id: Mapped[int | None] = mapped_column(
        ForeignKey("buildings.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    unit_code: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    unit_name: Mapped[str] = mapped_column(String(200), nullable=False)
    sector: Mapped[PatSector] = mapped_column(nullable=False, index=True)

    baseline_year: Mapped[int] = mapped_column(Integer, nullable=False)
# Which standard(s) this unit's SEC/EnPI tracking follows,
    # e.g. "BEE PAT", "ISO 50001", or "BEE PAT + ISO 50001".
    # SEC (BEE PAT terminology) and EnPI (ISO 50001 terminology) are
    # the same Energy/Production ratio concept -- this field just
    # records which compliance framing the org needs reported.
    standards_applicable: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    # ISO country code (e.g. "IN", "GB", "AE") -- selects this unit's
    # location-based Scope 2 grid factor + applicable regulatory
    # standards via app.services.country_config. Defaults to India.
    country_code: Mapped[str] = mapped_column(
        String(10), nullable=False, default="IN", index=True
    )
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    organization = relationship("Organization")
    building = relationship("Building")
