"""
Energy Service -- the single energy balance every pillar reads.

unit_period_energy() assembles, for one ManufacturingUnit and one period:
  electrical  : ManufacturingElectricityRecord kWh -> GJ (x 0.0036)
  thermal     : ManufacturingFuelRecord tonnes x LHV -> GJ (per fuel, biogenic flagged)
  fallback    : BENAS UtilityBill energy content, ONLY when the unit is
                linked to a building AND has no electricity/fuel records
                in the period (prevents double counting)
and returns GJ, toe (1 toe = 41.868 GJ, the BEE/PAT unit), thermal /
electrical split, renewable share, Scope 1 combustion CO2e, and the PAT
Designated-Consumer threshold check for the unit's sector.

Consumers: PAT SEC (sec_calculation_service), BRSR P6 EI 1, GRI 302,
ISO 50001 energy review, Energy dashboard, Report Studio, Product LCA.
A quantity entered once is read here by all of them.

Period rule: a record counts when it lies fully inside the requested
period (same rule the bill path already used). Overlapping records are
listed under `excluded_overlapping` so the user can see why a number is
missing instead of silently pro-rating it.
"""
from __future__ import annotations
from datetime import date
from sqlalchemy.orm import Session

from app.models.manufacturing_unit import ManufacturingUnit
from app.models.manufacturing_electricity_record import ManufacturingElectricityRecord
from app.models.manufacturing_fuel_record import ManufacturingFuelRecord
from app.models.energy_meter import EnergyMeter
from app.models.utility_bill import UtilityBill
from app.services.manufacturing_fuel_service import fuel_energy_and_emissions, GJ_PER_TOE
from app.services.cross_sector_ef_library import get_fuel

GJ_PER_KWH = 0.0036
GCAL_PER_GJ = 0.238846  # 1 GJ = 0.238846 Gcal (10^6 kcal per Gcal, 4.1868 MJ per kcal x 1000)

# BEE PAT Designated Consumer thresholds, toe per year (EC Act 2001 notifications,
# PAT cycle-I/II booklets). None = sector notified on a non-toe basis or not covered.
PAT_DC_THRESHOLD_TOE = {
    "aluminium": 7500, "cement": 30000, "chlor_alkali": 12000, "fertilizer": 30000,
    "iron_steel": 30000, "pulp_paper": 30000, "textile": 3000, "thermal_power": 30000,
    "refineries": 90000, "petrochemicals": 30000, "railways": None, "discoms": None, "other": None,
}


def _inside(rec_start: date, rec_end: date, start: date, end: date) -> bool:
    return rec_start >= start and rec_end <= end


def _overlaps(rec_start: date, rec_end: date, start: date, end: date) -> bool:
    return rec_start <= end and rec_end >= start


def unit_period_energy(db: Session, organization_id: int, unit: ManufacturingUnit,
                       period_start: date, period_end: date) -> dict:
    # ---- electricity ----
    elec_q = db.query(ManufacturingElectricityRecord).filter(
        ManufacturingElectricityRecord.organization_id == organization_id,
        ManufacturingElectricityRecord.manufacturing_unit_id == unit.id,
        ManufacturingElectricityRecord.period_start <= period_end,
        ManufacturingElectricityRecord.period_end >= period_start,
    ).all()
    elec_in = [r for r in elec_q if _inside(r.period_start, r.period_end, period_start, period_end)]
    elec_out = [r for r in elec_q if r not in elec_in]
    kwh = sum(r.electricity_consumed_kwh for r in elec_in)
    renewable_kwh = sum(r.renewable_kwh for r in elec_in)
    electrical_gj = kwh * GJ_PER_KWH

    # ---- fuels ----
    fuel_q = db.query(ManufacturingFuelRecord).filter(
        ManufacturingFuelRecord.organization_id == organization_id,
        ManufacturingFuelRecord.manufacturing_unit_id == unit.id,
        ManufacturingFuelRecord.period_start <= period_end,
        ManufacturingFuelRecord.period_end >= period_start,
    ).all()
    fuel_in = [r for r in fuel_q if _inside(r.period_start, r.period_end, period_start, period_end)]
    fuel_out = [r for r in fuel_q if r not in fuel_in]

    by_fuel: dict[str, dict] = {}
    thermal_gj = 0.0
    biomass_gj = 0.0
    scope1_kg = 0.0
    biogenic_kg = 0.0
    fuels_missing_lhv = []
    for r in fuel_in:
        d = fuel_energy_and_emissions(r.fuel_key, r.quantity_tonnes)
        if d["energy_gj"] is None:
            fuels_missing_lhv.append(r.fuel_key)
            continue
        f = get_fuel(r.fuel_key) or {}
        row = by_fuel.setdefault(r.fuel_key, {
            "fuel_key": r.fuel_key, "fuel_name": f.get("name"), "is_biogenic": bool(f.get("is_biogenic")),
            "tonnes": 0.0, "energy_gj": 0.0, "scope1_co2e_kg": 0.0, "biogenic_co2_kg": 0.0,
        })
        row["tonnes"] += r.quantity_tonnes
        row["energy_gj"] += d["energy_gj"]
        row["scope1_co2e_kg"] += d["scope1_co2e_kg"] or 0.0
        row["biogenic_co2_kg"] += d["biogenic_co2_kg"] or 0.0
        thermal_gj += d["energy_gj"]
        if row["is_biogenic"]:
            biomass_gj += d["energy_gj"]
        scope1_kg += d["scope1_co2e_kg"] or 0.0
        biogenic_kg += d["biogenic_co2_kg"] or 0.0

    # ---- BENAS bills: fallback only, never in addition ----
    bills_gj = 0.0
    bills_used = False
    bills_pending = []
    if not elec_in and not fuel_in and unit.building_id is not None:
        from app.services.sec_calculation_service import _find_factor  # local import: avoids a cycle
        meters = db.query(EnergyMeter).filter(EnergyMeter.building_id == unit.building_id).all()
        meters_by_id = {m.id: m for m in meters}
        if meters_by_id:
            bills = db.query(UtilityBill).filter(
                UtilityBill.meter_id.in_(list(meters_by_id)),
                UtilityBill.billing_period_start >= period_start,
                UtilityBill.billing_period_end <= period_end,
            ).all()
            for b in bills:
                m = meters_by_id[b.meter_id]
                factor = _find_factor(db, m.meter_type, m.unit, b.billing_period_start)
                if factor is None or factor.energy_content_gj_per_unit is None:
                    bills_pending.append({"bill_id": b.id, "meter_code": m.meter_code, "meter_type": m.meter_type})
                    continue
                bills_gj += b.consumption * factor.energy_content_gj_per_unit
                bills_used = True

    total_gj = electrical_gj + thermal_gj + bills_gj
    total_toe = total_gj / GJ_PER_TOE
    threshold = PAT_DC_THRESHOLD_TOE.get(unit.sector.value if hasattr(unit.sector, "value") else str(unit.sector))
    days = (period_end - period_start).days + 1
    annualised_toe = total_toe * (365 / days) if days > 0 else None

    return {
        "manufacturing_unit_id": unit.id,
        "period_start": period_start,
        "period_end": period_end,
        "total_energy_gj": round(total_gj, 4),
        "total_energy_toe": round(total_toe, 4),
        "electrical_gj": round(electrical_gj, 4),
        "electricity_kwh": round(kwh, 3),
        "renewable_kwh": round(renewable_kwh, 3),
        "thermal_gj": round(thermal_gj, 4),
        "thermal_gcal": round(thermal_gj * GCAL_PER_GJ, 4),
        "biomass_gj": round(biomass_gj, 4),
        "renewable_share_percent": round(((renewable_kwh * GJ_PER_KWH + biomass_gj) / total_gj) * 100, 2) if total_gj > 0 else None,
        "by_fuel": [{**v, "tonnes": round(v["tonnes"], 4), "energy_gj": round(v["energy_gj"], 4),
                     "scope1_co2e_kg": round(v["scope1_co2e_kg"], 3), "biogenic_co2_kg": round(v["biogenic_co2_kg"], 3)}
                    for v in by_fuel.values()],
        "scope1_combustion_co2e_kg": round(scope1_kg, 3),
        "biogenic_co2_kg": round(biogenic_kg, 3),
        "source_basis": "records" if (elec_in or fuel_in) else ("utility_bills" if bills_used else "none"),
        "bills_energy_gj": round(bills_gj, 4),
        "bills_pending_energy_content": bills_pending,
        "fuels_missing_lhv": fuels_missing_lhv,
        "excluded_overlapping": [
            {"kind": "electricity", "id": r.id, "period_start": r.period_start, "period_end": r.period_end} for r in elec_out
        ] + [
            {"kind": "fuel", "id": r.id, "period_start": r.period_start, "period_end": r.period_end} for r in fuel_out
        ],
        "pat_dc_threshold_toe": threshold,
        "annualised_toe": round(annualised_toe, 2) if annualised_toe is not None else None,
        "is_designated_consumer_scale": (annualised_toe >= threshold) if (threshold and annualised_toe is not None) else None,
    }
