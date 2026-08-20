from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.water_record import WaterRecord
from app.models.waste_record import WasteRecord
from app.repositories.water_record_repository import WaterRecordRepository
from app.repositories.waste_record_repository import WasteRecordRepository

WATER_WITHDRAWAL_FIELDS = [
    "withdrawal_surface_water",
    "withdrawal_groundwater",
    "withdrawal_third_party",
    "withdrawal_seawater_desalinated",
    "withdrawal_others",
]

WATER_DISCHARGE_FIELDS = [
    "discharge_surface_water",
    "discharge_groundwater",
    "discharge_seawater",
    "discharge_third_party",
    "discharge_others",
]

WASTE_GENERATED_FIELDS = [
    "plastic_waste",
    "e_waste",
    "bio_medical_waste",
    "construction_demolition_waste",
    "battery_waste",
    "radioactive_waste",
    "other_hazardous_waste",
    "other_non_hazardous_waste",
]

# SEBI's narrative question asks specifically about hazardous and toxic
# waste, so this subset is surfaced separately rather than recomputed by
# hand each time a report is written.
WASTE_HAZARDOUS_FIELDS = [
    "bio_medical_waste",
    "battery_waste",
    "radioactive_waste",
    "other_hazardous_waste",
]

WASTE_RECOVERED_FIELDS = ["recycled", "reused", "other_recovery"]
WASTE_DISPOSED_FIELDS = ["incineration", "landfilling", "other_disposal"]


def _sum_fields(obj: Any, fields: List[str]) -> Optional[Decimal]:
    """
    Sum the given fields, keeping unfilled distinct from zero.

    Returns None when every field is unset - a record with nothing entered
    must not report a total of 0, or the platform starts asserting figures
    nobody disclosed. A single 0 among Nones is a real disclosure and does
    produce a total.
    """
    values = [getattr(obj, f, None) for f in fields]
    present = [v for v in values if v is not None]
    if not present:
        return None
    return sum(present, Decimal("0"))


class WaterWasteService:
    """BRSR Section C, Principle 6 - water (Q3) and waste (Q9)."""

    def __init__(self, db: Session, organization_id: int):
        self.db = db
        self.organization_id = organization_id
        self.water_repo = WaterRecordRepository(db, organization_id)
        self.waste_repo = WasteRecordRepository(db, organization_id)

    # --- water ---

    def enrich_water(self, record: WaterRecord) -> Dict[str, Any]:
        """Record plus the three derived figures SEBI defines rather than asks for."""
        withdrawal = _sum_fields(record, WATER_WITHDRAWAL_FIELDS)
        discharge = _sum_fields(record, WATER_DISCHARGE_FIELDS)

        # Consumption = withdrawal - discharge, per SEBI. Left negative when
        # the inputs say so: a negative here means the data is wrong, and
        # hiding it would hide the error.
        consumption: Optional[Decimal] = None
        if withdrawal is not None or discharge is not None:
            consumption = (withdrawal or Decimal("0")) - (discharge or Decimal("0"))

        data = {
            c.name: getattr(record, c.name) for c in record.__table__.columns
        }
        data["total_withdrawal"] = withdrawal
        data["total_discharge"] = discharge
        data["total_consumption"] = consumption
        return data

    def get_water_records(self, year: int | None = None) -> List[Dict[str, Any]]:
        return [self.enrich_water(r) for r in self.water_repo.get_all(year)]

    # --- waste ---

    def enrich_waste(self, record: WasteRecord) -> Dict[str, Any]:
        data = {
            c.name: getattr(record, c.name) for c in record.__table__.columns
        }
        data["total_generated"] = _sum_fields(record, WASTE_GENERATED_FIELDS)
        data["total_recovered"] = _sum_fields(record, WASTE_RECOVERED_FIELDS)
        data["total_disposed"] = _sum_fields(record, WASTE_DISPOSED_FIELDS)
        data["hazardous_generated"] = _sum_fields(record, WASTE_HAZARDOUS_FIELDS)
        return data

    def get_waste_records(self, year: int | None = None) -> List[Dict[str, Any]]:
        return [self.enrich_waste(r) for r in self.waste_repo.get_all(year)]

    # --- org-level summary, for the P6 report ---

    def get_summary(self, year: int | None = None) -> Dict[str, Any]:
        """
        Organisation totals for the period, for BRSR P6 reporting.

        Every figure stays None when nothing underlying was disclosed, so a
        report can distinguish "not tracked" from "zero" - the same rule the
        emission factor appendix follows.
        """
        water = self.water_repo.get_all(year)
        waste = self.waste_repo.get_all(year)

        def _total(records, fields):
            per_record = [_sum_fields(r, fields) for r in records]
            present = [v for v in per_record if v is not None]
            return sum(present, Decimal("0")) if present else None

        water_withdrawal = _total(water, WATER_WITHDRAWAL_FIELDS)
        water_discharge = _total(water, WATER_DISCHARGE_FIELDS)
        water_consumption: Optional[Decimal] = None
        if water_withdrawal is not None or water_discharge is not None:
            water_consumption = (water_withdrawal or Decimal("0")) - (
                water_discharge or Decimal("0")
            )

        return {
            "organization_id": self.organization_id,
            "year": year,
            "water": {
                "record_count": len(water),
                "total_withdrawal_kl": water_withdrawal,
                "total_discharge_kl": water_discharge,
                "total_consumption_kl": water_consumption,
                "water_stressed_records": sum(
                    1 for r in water if r.is_water_stressed_area
                ),
            },
            "waste": {
                "record_count": len(waste),
                "total_generated_mt": _total(waste, WASTE_GENERATED_FIELDS),
                "hazardous_generated_mt": _total(waste, WASTE_HAZARDOUS_FIELDS),
                "total_recovered_mt": _total(waste, WASTE_RECOVERED_FIELDS),
                "total_disposed_mt": _total(waste, WASTE_DISPOSED_FIELDS),
            },
        }
