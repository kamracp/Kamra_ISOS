"""
PAT Cycle Target endpoints (Manufacturing / Energy module). Prefix
/pat-energy. Actual energy/production data lives in the existing
/production-records + utility-bills stack; this module only manages
BEE-notified targets and the PAT-aware summary on top of them.
organization_id always from JWT.
"""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.api.deps import get_current_user
from app.services.pat_sec_service import PatSecService
from app.schemas.pat_cycle_target import (
    PatCycleTargetCreate,
    PatCycleTargetUpdate,
    PatCycleTargetResponse,
)

router = APIRouter(prefix="/pat-energy", tags=["pat-energy"])


def get_service(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> PatSecService:
    return PatSecService(db, current_user.organization_id)


@router.post("/targets/{manufacturing_unit_id}", response_model=PatCycleTargetResponse, status_code=201)
def create_target(
    manufacturing_unit_id: int,
    payload: PatCycleTargetCreate,
    service: PatSecService = Depends(get_service),
):
    data = payload.model_dump()
    return service.create_target(manufacturing_unit_id, data)


@router.get("/targets/{manufacturing_unit_id}", response_model=list[PatCycleTargetResponse])
def list_targets(manufacturing_unit_id: int, service: PatSecService = Depends(get_service)):
    return service.list_targets(manufacturing_unit_id)


@router.put("/targets/{target_id}", response_model=PatCycleTargetResponse)
def update_target(
    target_id: int,
    payload: PatCycleTargetUpdate,
    service: PatSecService = Depends(get_service),
):
    data = payload.model_dump(exclude_unset=True)
    result = service.update_target(target_id, data)
    if result is None:
        raise HTTPException(status_code=404, detail="PAT cycle target not found")
    return result


@router.delete("/targets/{target_id}", status_code=204)
def delete_target(target_id: int, service: PatSecService = Depends(get_service)):
    if not service.delete_target(target_id):
        raise HTTPException(status_code=404, detail="PAT cycle target not found")


@router.get("/pat-summary/{manufacturing_unit_id}")
def get_pat_summary(
    manufacturing_unit_id: int,
    year: int,
    service: PatSecService = Depends(get_service),
):
    return service.get_pat_summary(manufacturing_unit_id, year)


@router.get("/energy-balance/{manufacturing_unit_id}")
def energy_balance(
    manufacturing_unit_id: int,
    year: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """ISO 50001-style energy review for one unit and year: per production
    period, the shared energy balance (electricity + fuels, bills fallback)
    with PAT split -- thermal SEC (Gcal/t), electrical SEC (kWh/t), overall
    (GJ/t, toe/t), by-fuel table, Scope 1 combustion, renewable share and
    the Designated-Consumer threshold check. Year matches period_start."""
    from app.models.production_record import ProductionRecord
    from app.services.sec_calculation_service import calculate_period_sec
    from app.services.energy_service import GJ_PER_TOE, GCAL_PER_GJ

    records = (
        db.query(ProductionRecord)
        .filter(
            ProductionRecord.organization_id == current_user.organization_id,
            ProductionRecord.manufacturing_unit_id == manufacturing_unit_id,
            ProductionRecord.period_start >= f"{year}-01-01",
            ProductionRecord.period_start <= f"{year}-12-31",
        )
        .order_by(ProductionRecord.period_start.asc())
        .all()
    )
    periods = [calculate_period_sec(db, current_user.organization_id, manufacturing_unit_id, r) for r in records]
    calc = [p for p in periods if p.get("status") == "calculated"]
    total_gj = sum(p["total_energy_gj"] for p in calc)
    thermal_gj = sum(p["thermal_sec_gcal_per_unit"] / GCAL_PER_GJ * p["production_quantity"] for p in calc if p["thermal_sec_gcal_per_unit"] is not None)
    kwh = sum(p["electrical_sec_kwh_per_unit"] * p["production_quantity"] for p in calc if p["electrical_sec_kwh_per_unit"] is not None)
    qty = sum(p["production_quantity"] for p in calc)
    return {
        "manufacturing_unit_id": manufacturing_unit_id,
        "year": year,
        "periods": periods,
        "year_totals": {
            "production_quantity": qty,
            "total_energy_gj": round(total_gj, 4),
            "total_energy_toe": round(total_gj / GJ_PER_TOE, 4),
            "thermal_gj": round(thermal_gj, 4),
            "electricity_kwh": round(kwh, 3),
            "sec_gj_per_unit": round(total_gj / qty, 6) if qty else None,
            "sec_toe_per_unit": round(total_gj / GJ_PER_TOE / qty, 6) if qty else None,
            "thermal_sec_gcal_per_unit": round(thermal_gj * GCAL_PER_GJ / qty, 6) if qty else None,
            "electrical_sec_kwh_per_unit": round(kwh / qty, 4) if qty else None,
            "scope1_combustion_co2e_kg": round(sum(p["scope1_combustion_co2e_kg"] for p in calc), 3),
            "pat_dc_threshold_toe": calc[0]["pat_dc_threshold_toe"] if calc else None,
            "is_designated_consumer_scale": (total_gj / GJ_PER_TOE >= calc[0]["pat_dc_threshold_toe"]) if (calc and calc[0]["pat_dc_threshold_toe"]) else None,
        },
        "periods_without_energy_data": [p["period_start"] for p in periods if p.get("status") != "calculated"],
    }
