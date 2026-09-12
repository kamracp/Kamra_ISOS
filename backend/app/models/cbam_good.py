"""
CBAM models (EU Carbon Border Adjustment Mechanism, definitive period 2026+).

CbamGood : one CBAM good produced at an installation (ManufacturingUnit) for
           one reporting year (calendar year, per the Methodology Act). It is
           linked to an LcaProduct whose functional unit is one tonne (or kg)
           of the good; the CBAM engine re-uses the LCA inventory and re-cuts it
           along CBAM boundaries:
             fuel        -> direct emissions (combustion + process)
             electricity -> indirect emissions (only where Annex II does not
                            restrict the good to direct emissions)
             factor      -> outside the CBAM boundary UNLESS the material is a
                            precursor CBAM good (precursor linking: session 2)
           Specific embedded emissions (SEE) = tCO2e per tonne of good, direct
           and indirect reported separately, as the operator template requires.

Nothing computed is persisted. Factor values come from the same libraries as
the LCA engine (IPCC / CEA / DEFRA) -- never typed.

This module prepares the operator's data; it does not replace verification by
an accredited verifier, which the definitive period requires for actual values.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

# Annex I goods categories. Annex II (Regulation (EU) 2023/956) lists the goods
# for which ONLY direct emissions count: iron & steel, aluminium, hydrogen.
CBAM_CATEGORIES = ("cement", "iron_steel", "aluminium", "fertilisers", "hydrogen", "electricity")
INDIRECT_REQUIRED = {"cement": True, "fertilisers": True, "electricity": True,
                     "iron_steel": False, "aluminium": False, "hydrogen": False}


class CbamGood(Base):
    __tablename__ = "cbam_goods"
    __table_args__ = (
        CheckConstraint(
            "goods_category IN ('cement', 'iron_steel', 'aluminium', 'fertilisers', 'hydrogen', 'electricity')",
            name="ck_cbam_goods_category",
        ),
        CheckConstraint("production_qty_tonne >= 0", name="ck_cbam_goods_production_non_negative"),
        CheckConstraint("reporting_year >= 2026 AND reporting_year <= 2100", name="ck_cbam_goods_year"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # The CBAM "installation". Nullable so a good can be drafted before the
    # unit is set up, but the operator template cannot be exported without it.
    manufacturing_unit_id: Mapped[int | None] = mapped_column(
        ForeignKey("manufacturing_units.id", ondelete="SET NULL"), nullable=True, index=True
    )
    # Source of the inventory. SET NULL keeps the CBAM record if the LCA product
    # is deleted; the engine then reports status no_lca.
    lca_product_id: Mapped[int | None] = mapped_column(
        ForeignKey("lca_products.id", ondelete="SET NULL"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    cn_code: Mapped[str] = mapped_column(String(12), nullable=False)      # e.g. "2523 29 00"
    goods_category: Mapped[str] = mapped_column(String(20), nullable=False)
    production_route: Mapped[str | None] = mapped_column(String(120), nullable=True)  # e.g. "BF-BOF", "dry kiln"
    reporting_year: Mapped[int] = mapped_column(Integer, nullable=False)
    production_qty_tonne: Mapped[float] = mapped_column(Float, nullable=False)
    # Carbon price effectively paid in the country of origin, if any (Art. 9).
    carbon_price_paid_per_tco2e: Mapped[float | None] = mapped_column(Float, nullable=True)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    organization = relationship("Organization")
    manufacturing_unit = relationship("ManufacturingUnit")
    lca_product = relationship("LcaProduct")
