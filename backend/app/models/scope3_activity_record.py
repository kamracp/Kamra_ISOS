"""
Scope 3 activity records (GHG Protocol Corporate Value Chain Standard).

One row = one activity line for one Scope 3 category in one reporting year, with
an explicit emission_factor_id (DEFRA / other cited source). Emissions are never
stored: the Scope 3 engine multiplies quantity x factor at read time, so a factor
revision recomputes every record.

Only ENTERED categories live here (today: 4 upstream transport; later 1, 6, 7, 9).
Categories 3 (WTT + T&D) and 5 (waste) are DERIVED by the engine from the existing
fuel / electricity / waste records and are not written to this table.
"""
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Scope3ActivityRecord(Base):
    __tablename__ = "scope3_activity_records"
    __table_args__ = (
        CheckConstraint("category >= 1 AND category <= 15", name="ck_scope3_category"),
        CheckConstraint("quantity >= 0", name="ck_scope3_quantity_non_negative"),
        CheckConstraint("year >= 2000 AND year <= 2100", name="ck_scope3_year"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    manufacturing_unit_id: Mapped[int | None] = mapped_column(
        ForeignKey("manufacturing_units.id", ondelete="SET NULL"), nullable=True, index=True
    )
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    category: Mapped[int] = mapped_column(Integer, nullable=False, index=True)   # GHG Protocol 1..15
    description: Mapped[str] = mapped_column(String(200), nullable=False)        # e.g. "Clay from Bikaner, road"
    quantity: Mapped[float] = mapped_column(Float, nullable=False)                # in `unit` (tonne.km, tonne, km, ...)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)                 # must equal the factor's unit
    # RESTRICT: a factor in use cannot be deleted; revise it instead (audit trail).
    emission_factor_id: Mapped[int] = mapped_column(
        ForeignKey("emission_factors.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    data_source: Mapped[str | None] = mapped_column(String(200), nullable=True)  # LR copies, ERP, invoices
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    organization = relationship("Organization")
    manufacturing_unit = relationship("ManufacturingUnit")
    emission_factor = relationship("EmissionFactor")
