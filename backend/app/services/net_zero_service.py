"""
Net Zero calculation service (function-style, mirrors sec_calculation_service.py).

Two jobs:
1. MACC (Marginal Abatement Cost Curve): for every Decarbonization
   Project, MAC ($/tCO2e) = (Annualized CAPEX + Annual delta-OPEX) /
   Annual tCO2e abated. Sorted cheapest-first -- this is the order
   projects should be implemented in for cheapest path to target.
2. BAU vs Target trajectory: given a NetZeroTarget (baseline year/
   value, target year/%), plus today's actual emissions (reusing the
   same bill x factor logic as CarbonService), compute where the org
   SHOULD be on a straight-line path right now, and the gap vs actual.

Both a NetZeroTarget and a DecarbonizationProject may optionally be
scoped to one ManufacturingUnit (manufacturing_unit_id, nullable FK --
already existed on both models). When a target IS unit-scoped, its
summary and MACC are filtered to that unit only: projects to that
unit's own projects, and actual emissions to meters at that unit's
linked Building. Org-wide (manufacturing_unit_id is None) behaves
exactly as before -- all org projects/meters, unfiltered.
"""
from datetime import date

from sqlalchemy.orm import Session

from app.models.decarbonization_project import DecarbonizationProject
from app.models.emission_factor import EmissionFactor
from app.models.energy_meter import EnergyMeter
from app.models.manufacturing_unit import ManufacturingUnit
from app.models.net_zero_target import NetZeroTarget
from app.models.utility_bill import UtilityBill


def calculate_macc(
    db: Session, organization_id: int, manufacturing_unit_id: int | None = None
) -> list[dict]:
    query = db.query(DecarbonizationProject).filter(
        DecarbonizationProject.organization_id == organization_id
    )
    if manufacturing_unit_id is not None:
        query = query.filter(
            DecarbonizationProject.manufacturing_unit_id == manufacturing_unit_id
        )
    projects = query.all()

    results = []
    for p in projects:
        annualized_capex = p.capex / p.lifespan_years if p.lifespan_years else 0.0
        annual_cost = annualized_capex + p.annual_opex_delta

        mac = None
        if p.annual_co2e_abated_tonnes > 0:
            mac = round(annual_cost / p.annual_co2e_abated_tonnes, 2)

        results.append(
            {
                "id": p.id,
                "project_name": p.project_name,
                "category": p.category,
                "status": p.status,
                "capex": p.capex,
                "annual_opex_delta": p.annual_opex_delta,
                "lifespan_years": p.lifespan_years,
                "annual_co2e_abated_tonnes": p.annual_co2e_abated_tonnes,
                "annualized_capex": round(annualized_capex, 2),
                "marginal_abatement_cost": mac,
            }
        )

    # Cheapest (most negative / lowest cost per tonne) first. None (can't
    # compute) sorted to the end rather than dropped -- audit-trail discipline.
    results.sort(
        key=lambda r: (r["marginal_abatement_cost"] is None, r["marginal_abatement_cost"])
    )
    return results


def _get_current_total_co2e_tonnes(
    db: Session, organization_id: int, manufacturing_unit_id: int | None = None
) -> float:
    """Same bill x factor logic as CarbonService, condensed to a single total
    (Scope 1 + Scope 2 only, renewable/avoided excluded -- matches CarbonService).
    When manufacturing_unit_id is given, scoped to meters at that unit's
    linked Building only; None (or unit has no building linked) falls back
    to all org meters."""
    meter_query = db.query(EnergyMeter).filter(
        EnergyMeter.organization_id == organization_id
    )

    if manufacturing_unit_id is not None:
        unit = (
            db.query(ManufacturingUnit)
            .filter(
                ManufacturingUnit.id == manufacturing_unit_id,
                ManufacturingUnit.organization_id == organization_id,
            )
            .first()
        )
        if unit is not None and unit.building_id is not None:
            meter_query = meter_query.filter(EnergyMeter.building_id == unit.building_id)
        else:
            # Unit not found or has no building linked -- no meters to attribute, not "all org meters".
            return 0.0

    meters = meter_query.all()
    meters_by_id = {m.id: m for m in meters}
    if not meters_by_id:
        return 0.0

    bills = (
        db.query(UtilityBill)
        .filter(
            UtilityBill.organization_id == organization_id,
            UtilityBill.meter_id.in_(meters_by_id.keys()),
        )
        .all()
    )

    total_kg = 0.0
    for bill in bills:
        meter = meters_by_id.get(bill.meter_id)
        if meter is None or meter.scope not in ("scope_1", "scope_2"):
            continue

        factor = (
            db.query(EmissionFactor)
            .filter(
                EmissionFactor.meter_type == meter.meter_type,
                EmissionFactor.unit == meter.unit,
                EmissionFactor.region == "IN",
                EmissionFactor.is_active.is_(True),
                EmissionFactor.valid_from <= bill.billing_period_start,
                (EmissionFactor.valid_to.is_(None))
                | (EmissionFactor.valid_to >= bill.billing_period_start),
            )
            .order_by(EmissionFactor.valid_from.desc())
            .first()
        )

        if factor is None:
            continue

        total_kg += bill.consumption * factor.factor_kgco2e_per_unit

    return round(total_kg / 1000, 3)


def get_net_zero_summary(db: Session, organization_id: int, target_id: int) -> dict:
    target = (
        db.query(NetZeroTarget)
        .filter(
            NetZeroTarget.id == target_id,
            NetZeroTarget.organization_id == organization_id,
        )
        .first()
    )
    if target is None:
        return {"status": "target_not_found"}

    current_year = date.today().year
    current_actual_tonnes = _get_current_total_co2e_tonnes(
        db, organization_id, target.manufacturing_unit_id
    )

    target_co2e_tonnes = round(
        target.baseline_co2e_tonnes * (1 - target.reduction_percentage / 100), 3
    )

    total_years = target.target_year - target.baseline_year
    years_elapsed = max(0, min(current_year - target.baseline_year, total_years))

    if total_years > 0:
        expected_co2e_tonnes = round(
            target.baseline_co2e_tonnes
            - (target.baseline_co2e_tonnes - target_co2e_tonnes)
            * (years_elapsed / total_years),
            3,
        )
    else:
        expected_co2e_tonnes = target.baseline_co2e_tonnes

    gap_tonnes = round(current_actual_tonnes - expected_co2e_tonnes, 3)

    return {
        "status": "ok",
        "target_id": target.id,
        "target_name": target.target_name,
        "manufacturing_unit_id": target.manufacturing_unit_id,
        "baseline_year": target.baseline_year,
        "baseline_co2e_tonnes": target.baseline_co2e_tonnes,
        "target_year": target.target_year,
        "target_co2e_tonnes": target_co2e_tonnes,
        "reduction_percentage": target.reduction_percentage,
        "current_year": current_year,
        "current_actual_co2e_tonnes": current_actual_tonnes,
        "expected_co2e_tonnes_on_trajectory": expected_co2e_tonnes,
        "gap_tonnes": gap_tonnes,
        "on_track": gap_tonnes <= 0,
        "macc": calculate_macc(db, organization_id, target.manufacturing_unit_id),
    }
