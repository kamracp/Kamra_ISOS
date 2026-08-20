from sqlalchemy import (
    Column,
    Integer,
    Text,
    Numeric,
    Date,
    ForeignKey,
    DateTime,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class WasteRecord(Base):
    """
    BRSR Section C, Principle 6, Question 9 - waste generated, recovered and
    disposed for one reporting period.

    The eight generation categories are SEBI's own A-H list. Totals are NOT
    stored: total generated is the sum of the categories, and storing it
    would let a filed total drift away from its own parts.

    Recovery and disposal are asked separately by SEBI and are separate KPIs
    under BRSR Core - waste generated, and waste diverted from disposal.

    All quantities are in metric tonnes (MT).
    """

    __tablename__ = "waste_records"
    __table_args__ = (
        CheckConstraint(
            "period_end >= period_start", name="ck_waste_record_period_order"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(
        Integer,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    manufacturing_unit_id = Column(
        Integer,
        ForeignKey("manufacturing_units.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    building_id = Column(
        Integer,
        ForeignKey("buildings.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)

    # --- Waste generated, SEBI categories A-H (MT) ---
    plastic_waste = Column(Numeric(18, 3), nullable=True)              # A
    e_waste = Column(Numeric(18, 3), nullable=True)                    # B
    bio_medical_waste = Column(Numeric(18, 3), nullable=True)          # C
    construction_demolition_waste = Column(Numeric(18, 3), nullable=True)  # D
    battery_waste = Column(Numeric(18, 3), nullable=True)              # E
    radioactive_waste = Column(Numeric(18, 3), nullable=True)          # F
    other_hazardous_waste = Column(Numeric(18, 3), nullable=True)      # G
    other_non_hazardous_waste = Column(Numeric(18, 3), nullable=True)  # H

    # --- Recovered / diverted from disposal (MT) ---
    recycled = Column(Numeric(18, 3), nullable=True)
    reused = Column(Numeric(18, 3), nullable=True)
    other_recovery = Column(Numeric(18, 3), nullable=True)

    # --- Disposed (MT) ---
    incineration = Column(Numeric(18, 3), nullable=True)
    landfilling = Column(Numeric(18, 3), nullable=True)
    other_disposal = Column(Numeric(18, 3), nullable=True)

    # SEBI also asks for a narrative on waste management practices.
    waste_management_practices = Column(Text, nullable=True)
    remarks = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    organization = relationship("Organization")
