"""
Manufacturing Fuel Service -- fuel combustion records for ManufactureOS.

Derives, on read and never stored:
  energy_gj      = tonnes x LHV (TJ/Gg == GJ/t)
  energy_toe     = energy_gj / 41.868           (1 toe = 10^7 kcal, BEE/PAT unit)
  scope1_co2e_kg = tonnes x co2e_kg_per_tonne   (biogenic CO2 excluded)
  biogenic_co2_kg= tonnes x (co2e incl. biogenic - co2e excl. biogenic)
These are the same numbers the energy layer, PAT SEC, Scope 1 and P6 EI 1
will read, so a fuel entered here is never entered anywhere else.
"""
from __future__ import annotations
from app.repositories.manufacturing_fuel_record_repository import ManufacturingFuelRecordRepository
from app.models.manufacturing_fuel_record import ManufacturingFuelRecord
from app.services.cross_sector_ef_library import get_fuel, co2e_per_tonne, is_biogenic, list_fuels

GJ_PER_TOE = 41.868


def fuel_energy_and_emissions(fuel_key: str, tonnes: float) -> dict:
    """Pure function shared with energy_service; None when the library
    lacks an LHV for the fuel (never a guessed number)."""
    f = get_fuel(fuel_key)
    if f is None:
        return {"lhv_gj_per_tonne": None, "energy_gj": None, "energy_toe": None,
                "scope1_co2e_kg": None, "biogenic_co2_kg": None}
    lhv = f["lhv_tj_per_gg"]
    energy_gj = round(tonnes * lhv, 4) if lhv is not None else None
    fossil = co2e_per_tonne(fuel_key, include_biogenic_co2=False)
    total = co2e_per_tonne(fuel_key, include_biogenic_co2=True)
    return {
        "lhv_gj_per_tonne": lhv,
        "energy_gj": energy_gj,
        "energy_toe": round(energy_gj / GJ_PER_TOE, 4) if energy_gj is not None else None,
        "scope1_co2e_kg": round(tonnes * fossil, 3) if fossil is not None else None,
        "biogenic_co2_kg": round(tonnes * (total - fossil), 3) if (total is not None and fossil is not None and is_biogenic(fuel_key)) else 0.0,
    }


class ManufacturingFuelService:
    def __init__(self, fuel_repository: ManufacturingFuelRecordRepository):
        self.fuel_repository = fuel_repository

    @staticmethod
    def library() -> list[dict]:
        return list_fuels()

    def create_record(self, data) -> dict:
        return self._serialize(self.fuel_repository.create(data))

    def list_records(self, year: int | None = None) -> list[dict]:
        return [self._serialize(r) for r in self.fuel_repository.get_all(year=year)]

    def list_by_unit(self, manufacturing_unit_id: int, year: int | None = None) -> list[dict]:
        return [self._serialize(r) for r in self.fuel_repository.get_by_unit(manufacturing_unit_id, year=year)]

    def get_record(self, record_id: int) -> dict | None:
        r = self.fuel_repository.get_by_id(record_id)
        return self._serialize(r) if r else None

    def update_record(self, record_id: int, data) -> dict | None:
        r = self.fuel_repository.get_by_id(record_id)
        if r is None:
            return None
        return self._serialize(self.fuel_repository.update(r, data))

    def delete_record(self, record_id: int) -> bool:
        r = self.fuel_repository.get_by_id(record_id)
        if r is None:
            return False
        self.fuel_repository.delete(r)
        return True

    def _serialize(self, r: ManufacturingFuelRecord) -> dict:
        f = get_fuel(r.fuel_key) or {}
        out = {
            "id": r.id, "organization_id": r.organization_id,
            "manufacturing_unit_id": r.manufacturing_unit_id,
            "period_start": r.period_start, "period_end": r.period_end,
            "fuel_key": r.fuel_key, "quantity_tonnes": r.quantity_tonnes, "purpose": r.purpose,
            "source": r.source, "remarks": r.remarks,
            "fuel_name": f.get("name"), "fuel_category": f.get("category"), "is_biogenic": f.get("is_biogenic"),
            "created_at": r.created_at, "updated_at": r.updated_at,
        }
        out.update(fuel_energy_and_emissions(r.fuel_key, r.quantity_tonnes))
        return out
