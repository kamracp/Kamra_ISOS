"""
Product LCA models (LCA/PCF Studio).

LcaProduct   : one product + functional unit + system boundary (cradle-to-gate
               by default) for an organization, optionally tied to a
               ManufacturingUnit.
LcaInventoryItem : one life-cycle inventory input for that product -- a
               material, fuel, electricity or transport flow with its quantity
               and a *reference* to the emission factor that converts it to
               kgCO2e. Factor values are never stored; they are resolved at
               read time from one of three sources:
                 fuel        -> cross_sector_ef_library.FUEL_LIBRARY[fuel_key]
                 electricity -> country_config grid factor for country_code
                 factor      -> emission_factors row (DEFRA/IPCC materials,
                                transport, packaging, with citation)
               So a factor revision re-computes every product automatically.

GWP per functional unit = sum(quantity_per_fu x factor). Annual-total items
are divided by the product's annual_output_qty x functional_unit_qty in the
engine -- the simplest auditable allocation. Totals are never persisted
(same rule as water/waste and fuel records).

Scope: ISO 14067-style carbon footprint using GWP100 factors. This is NOT a
verified ISO 14040/44 LCA; the export (session 2) is for consultant review.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

SYSTEM_BOUNDARIES = ("cradle_to_gate", "gate_to_gate", "cradle_to_grave")
LCA_STAGES = ("raw_materials", "inbound_transport", "manufacturing", "packaging", "outbound_transport")
FACTOR_SOURCES = ("fuel", "electricity", "factor")
QUANTITY_BASES = ("per_functional_unit", "annual_total")


class LcaProduct(Base):
    __tablename__ = "lca_products"
    __table_args__ = (
        CheckConstraint("functional_unit_qty > 0", name="ck_lca_product_fu_qty_positive"),
        CheckConstraint("annual_output_qty IS NULL OR annual_output_qty > 0", name="ck_lca_product_output_positive"),
        CheckConstraint(
            "system_boundary IN ('cradle_to_gate', 'gate_to_gate', 'cradle_to_grave')",
            name="ck_lca_product_boundary",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    manufacturing_unit_id: Mapped[int | None] = mapped_column(
        ForeignKey("manufacturing_units.id", ondelete="SET NULL"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    product_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Declared unit of analysis, e.g. 1 tonne clinker, 1 m2 vitrified tile.
    functional_unit_qty: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    functional_unit: Mapped[str] = mapped_column(String(30), nullable=False)
    system_boundary: Mapped[str] = mapped_column(String(20), nullable=False, default="cradle_to_gate")
    reference_year: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    # Annual production in functional units (e.g. tonnes/year). Required only
    # when any inventory item uses basis = annual_total.
    annual_output_qty: Mapped[float | None] = mapped_column(Float, nullable=True)
    # Default country for electricity items; ISO 3166-1 alpha-2, key into country_config.
    production_country_code: Mapped[str] = mapped_column(String(2), nullable=False, default="IN")
    # LCA session 4: plausibility benchmark key (see lca_benchmarks.py) and Material Circularity
    # Indicator inputs (Ellen MacArthur MCI). All nullable: an unknown input keeps MCI/benchmark
    # at not_computed rather than assuming a value.
    benchmark_key: Mapped[str | None] = mapped_column(String(40), nullable=True)
    eol_recycling_fraction: Mapped[float | None] = mapped_column(Float, nullable=True)       # Cr
    eol_reuse_fraction: Mapped[float | None] = mapped_column(Float, nullable=True)           # Cu
    recycling_efficiency_input: Mapped[float | None] = mapped_column(Float, nullable=True)   # Ef
    recycling_efficiency_eol: Mapped[float | None] = mapped_column(Float, nullable=True)     # Ec
    lifetime_years: Mapped[float | None] = mapped_column(Float, nullable=True)               # L
    industry_avg_lifetime_years: Mapped[float | None] = mapped_column(Float, nullable=True)  # Lav
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    organization = relationship("Organization")
    manufacturing_unit = relationship("ManufacturingUnit")
    items = relationship(
        "LcaInventoryItem",
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="LcaInventoryItem.id",
    )


class LcaInventoryItem(Base):
    __tablename__ = "lca_inventory_items"
    __table_args__ = (
        CheckConstraint("quantity >= 0", name="ck_lca_item_quantity_non_negative"),
        CheckConstraint(
            "stage IN ('raw_materials', 'inbound_transport', 'manufacturing', 'packaging', 'outbound_transport')",
            name="ck_lca_item_stage",
        ),
        CheckConstraint(
            "factor_source IN ('fuel', 'electricity', 'factor')",
            name="ck_lca_item_factor_source",
        ),
        CheckConstraint(
            "basis IN ('per_functional_unit', 'annual_total')",
            name="ck_lca_item_basis",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # Denormalised tenant key so the repository's _base_query() can filter
    # items without a join -- no method can read across tenants.
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("lca_products.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    stage: Mapped[str] = mapped_column(String(30), nullable=False)
    # Which of the three factor references below applies (exactly one must be
    # set; enforced in the Pydantic schema, not here).
    factor_source: Mapped[str] = mapped_column(String(20), nullable=False)
    fuel_key: Mapped[str | None] = mapped_column(String(50), nullable=True)
    country_code: Mapped[str | None] = mapped_column(String(2), nullable=True)
    emission_factor_id: Mapped[int | None] = mapped_column(
        ForeignKey("emission_factors.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    # Must match the factor's unit: fuel -> tonne, electricity -> kWh,
    # factor -> emission_factors.unit (kg, tonne, tkm, litre ...). Checked by the service.
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    basis: Mapped[str] = mapped_column(String(25), nullable=False, default="per_functional_unit")
    # CBAM (session 2): optional bucket override and precursor link.
    # NULL bucket = engine default rule (fuel/process=direct, grid=indirect, else excluded).
    cbam_bucket: Mapped[str | None] = mapped_column(String(12), nullable=True)
    precursor_cbam_good_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("cbam_goods.id", ondelete="SET NULL"), nullable=True, index=True
    )
    # LCA session 4 (MCI): share of this material input that is recycled / reused feedstock (0-1).
    recycled_content_fraction: Mapped[float | None] = mapped_column(Float, nullable=True)    # Fr
    reused_content_fraction: Mapped[float | None] = mapped_column(Float, nullable=True)      # Fu
    # Traceability: invoice, weighbridge, ERP report, supplier EPD.
    data_source: Mapped[str | None] = mapped_column(String(200), nullable=True)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    product = relationship("LcaProduct", back_populates="items")
    emission_factor = relationship("EmissionFactor")
