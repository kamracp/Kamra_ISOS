"""
SEC (BEE PAT) / EnPI (ISO 50001) Calculation Service (Phase 6)

Core idea: for a ManufacturingUnit's production period, sum all
energy consumed (converted to GJ via emission_factors.energy_content_gj_per_unit)
by meters at the unit's linked Building, divide by production quantity
for that same period = SEC / EnPI.

Baseline SEC = average SEC across whichever production periods fall
in the unit's baseline_year. All other periods are compared against it.
"""
from sqlalchemy.orm import Session

from app.models.emission_factor import EmissionFactor
from app.models.energy_meter import EnergyMeter
from app.models.manufacturing_unit import ManufacturingUnit
from app.models.production_record import ProductionRecord
from app.models.utility_bill import UtilityBill


def _find_factor(db: Session, meter_type: str, unit: str, on_date, region: str = "IN"):
    return (
        db.query(EmissionFactor)
        .filter(
            EmissionFactor.meter_type == meter_type,
            EmissionFactor.unit == unit,
            EmissionFactor.region == region,
            EmissionFactor.is_active.is_(True),
            EmissionFactor.valid_from <= on_date,
            (EmissionFactor.valid_to.is_(None)) | (EmissionFactor.valid_to >= on_date),
        )
        .order_by(EmissionFactor.valid_from.desc())
        .first()
    )


def calculate_period_sec(
    db: Session,
    organization_id: int,
    manufacturing_unit_id: int,
    production_record: ProductionRecord,
) -> dict:
    """SEC for one production period, on the shared energy balance
    (energy_service.unit_period_energy): electricity + fuel records, with
    BENAS utility bills only as a fallback. Reports the PAT split --
    thermal SEC (Gcal/t), electrical SEC (kWh/t), overall (GJ/t, toe/t) --
    the same shape as BEE's PAT cycle tables."""
    from app.services.energy_service import unit_period_energy, GJ_PER_TOE, GCAL_PER_GJ

    unit = (
        db.query(ManufacturingUnit)
        .filter(
            ManufacturingUnit.id == manufacturing_unit_id,
            ManufacturingUnit.organization_id == organization_id,
        )
        .first()
    )
    if unit is None:
        return {"status": "unit_not_found", "manufacturing_unit_id": manufacturing_unit_id}

    energy = unit_period_energy(
        db, organization_id, unit, production_record.period_start, production_record.period_end
    )
    if energy["source_basis"] == "none":
        return {
            "status": "no_energy_data",
            "manufacturing_unit_id": manufacturing_unit_id,
            "period_start": production_record.period_start,
            "period_end": production_record.period_end,
            "production_quantity": production_record.production_quantity,
            "production_unit": production_record.production_unit,
            "hint": "Add electricity and fuel records for this unit and period (or link a building with bills).",
            "excluded_overlapping": energy["excluded_overlapping"],
        }

    qty = production_record.production_quantity
    total_gj = energy["total_energy_gj"]
    sec = round(total_gj / qty, 6) if qty > 0 else None

    return {
        "status": "calculated",
        "manufacturing_unit_id": manufacturing_unit_id,
        "period_start": production_record.period_start,
        "period_end": production_record.period_end,
        "total_energy_gj": total_gj,
        "total_energy_toe": energy["total_energy_toe"],
        "production_quantity": qty,
        "production_unit": production_record.production_unit,
        "sec_gj_per_unit": sec,
        # PAT / ISO 50001 EnPI split
        "sec_toe_per_unit": round(total_gj / GJ_PER_TOE / qty, 6) if qty > 0 else None,
        "thermal_sec_gcal_per_unit": round(energy["thermal_gj"] * GCAL_PER_GJ / qty, 6) if qty > 0 else None,
        "electrical_sec_kwh_per_unit": round(energy["electricity_kwh"] / qty, 4) if qty > 0 else None,
        "renewable_share_percent": energy["renewable_share_percent"],
        "source_basis": energy["source_basis"],
        "by_fuel": energy["by_fuel"],
        "scope1_combustion_co2e_kg": energy["scope1_combustion_co2e_kg"],
        "bills_pending_energy_content": energy["bills_pending_energy_content"],
        "fuels_missing_lhv": energy["fuels_missing_lhv"],
        "excluded_overlapping": energy["excluded_overlapping"],
        "pat_dc_threshold_toe": energy["pat_dc_threshold_toe"],
        "annualised_toe": energy["annualised_toe"],
        "is_designated_consumer_scale": energy["is_designated_consumer_scale"],
    }


def get_sec_summary(db: Session, organization_id: int, manufacturing_unit_id: int) -> dict:
    """BEE PAT-style / ISO 50001-style summary: baseline SEC vs every period's SEC."""
    unit = (
        db.query(ManufacturingUnit)
        .filter(
            ManufacturingUnit.id == manufacturing_unit_id,
            ManufacturingUnit.organization_id == organization_id,
        )
        .first()
    )

    if unit is None:
        return {"status": "unit_not_found"}

    records = (
        db.query(ProductionRecord)
        .filter(
            ProductionRecord.organization_id == organization_id,
            ProductionRecord.manufacturing_unit_id == manufacturing_unit_id,
        )
        .order_by(ProductionRecord.period_start)
        .all()
    )

    period_results = [
        calculate_period_sec(db, organization_id, manufacturing_unit_id, r) for r in records
    ]

    baseline_secs = [
        r["sec_gj_per_unit"]
        for r, rec in zip(period_results, records)
        if r.get("sec_gj_per_unit") is not None and rec.period_start.year == unit.baseline_year
    ]
    baseline_sec = round(sum(baseline_secs) / len(baseline_secs), 6) if baseline_secs else None

    for r in period_results:
        if baseline_sec and r.get("sec_gj_per_unit") is not None:
            r["pct_change_vs_baseline"] = round(
                ((r["sec_gj_per_unit"] - baseline_sec) / baseline_sec) * 100, 2
            )
        else:
            r["pct_change_vs_baseline"] = None

    return {
        "status": "ok",
        "manufacturing_unit_id": manufacturing_unit_id,
        "sector": unit.sector,
        "baseline_year": unit.baseline_year,
        "baseline_sec_gj_per_unit": baseline_sec,
        "standards_applicable": unit.standards_applicable,
        "periods": period_results,
    }
