from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Numeric,
    Boolean,
    Date,
    ForeignKey,
    DateTime,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class WaterRecord(Base):
    """
    BRSR Section C, Principle 6, Question 3 - water withdrawal and discharge
    for one reporting period.

    Withdrawal is split by source and discharge by destination, each as its
    own column rather than JSONB: unlike Section A's disclosure blocks these
    figures are aggregated, trended and used for intensity ratios, so they
    have to be queryable in SQL.

    Consumption is deliberately NOT stored. SEBI defines it as
    withdrawal minus discharge, so persisting it would create a second
    version of the truth that can disagree with its own inputs - exactly
    what an assurance provider looks for. It is computed in the service.

    Volumes are in kilolitres (KL) throughout.
    """

    __tablename__ = "water_records"
    __table_args__ = (
        CheckConstraint(
            "period_end >= period_start", name="ck_water_record_period_order"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(
        Integer,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Optional: a record can be org-wide or tied to one plant. SEBI asks for
    # unit-wise water data specifically for units in water-stressed areas.
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

    # Flags this record as falling under the additional unit-wise disclosure
    # SEBI requires only for water-stressed locations.
    is_water_stressed_area = Column(Boolean, nullable=False, default=False)

    # --- Withdrawal by source (KL) ---
    withdrawal_surface_water = Column(Numeric(18, 3), nullable=True)
    withdrawal_groundwater = Column(Numeric(18, 3), nullable=True)
    withdrawal_third_party = Column(Numeric(18, 3), nullable=True)
    withdrawal_seawater_desalinated = Column(Numeric(18, 3), nullable=True)
    withdrawal_others = Column(Numeric(18, 3), nullable=True)

    # --- Discharge by destination (KL) ---
    discharge_surface_water = Column(Numeric(18, 3), nullable=True)
    discharge_groundwater = Column(Numeric(18, 3), nullable=True)
    discharge_seawater = Column(Numeric(18, 3), nullable=True)
    discharge_third_party = Column(Numeric(18, 3), nullable=True)
    discharge_others = Column(Numeric(18, 3), nullable=True)

    # Treatment level applied before discharge, where relevant.
    # Free text: SEBI names primary/secondary/tertiary but entities commonly
    # describe combined or plant-specific treatment trains.
    discharge_treatment_level = Column(String(255), nullable=True)

    # Zero Liquid Discharge - a specific BRSR disclosure, not just "no
    # discharge": it means treated water is fully recycled back into use.
    has_zero_liquid_discharge = Column(Boolean, nullable=True)

    remarks = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    organization = relationship("Organization")
