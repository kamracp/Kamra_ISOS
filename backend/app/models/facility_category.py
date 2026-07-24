"""
Facility Category model.

A simple, user-editable list of facility/block names shown on the
Dashboard's portfolio widget (e.g. "Admin Block", "Workshop",
"Engineering Wing" for Manufacturing; "Commercial Buildings",
"Hospitals" for BENAS). No energy/data linkage -- display only,
by design (user's explicit scope choice).
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class FacilityCategory(Base):
    __tablename__ = "facility_categories"

    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "segment",
            "name",
            name="uq_facility_category_org_segment_name",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # "benas" or "manufacturing" -- which segment's portfolio this belongs to.
    segment: Mapped[str] = mapped_column(String(20), nullable=False, index=True)

    name: Mapped[str] = mapped_column(String(150), nullable=False)

    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    organization = relationship("Organization")
