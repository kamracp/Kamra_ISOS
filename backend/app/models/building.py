from __future__ import annotations

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


class Building(Base):
    __tablename__ = "buildings"

    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "building_code",
            name="uq_building_org_code",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    building_code: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )

    building_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    address_line_1: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    address_line_2: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    city: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )

    state: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )

    country: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )

    pincode: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    building_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    total_floor_area: Mapped[float | None] = mapped_column(
        nullable=True,
    )

    number_of_floors: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    year_constructed: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("facility_categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
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

    organization = relationship(
        "Organization",
        back_populates="buildings",
    )

    floors = relationship(
        "Floor",
        back_populates="building",
        cascade="all, delete-orphan",
    )
    energy_meters = relationship(
        "EnergyMeter",
        back_populates="building",
        cascade="all, delete-orphan",
    )
