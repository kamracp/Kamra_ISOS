"""
PAT SEC Service (Manufacturing / Energy module)
Adds BEE PAT compliance on top of the EXISTING sec_calculation_service
(which already derives SEC automatically from utility bills + ProductionRecord).
This service does NOT recompute energy/production -- it only manages
PatCycleTarget (BEE-notified baseline + mandated reduction%) and
compares the existing engine's actual SEC against the derived target.
"""
from __future__ import annotations
from sqlalchemy.orm import Session

from app.repositories.pat_cycle_target_repository import PatCycleTargetRepository
from app.models.pat_cycle_target import PatCycleTarget
from app.services import sec_calculation_service


def _target_sec(target: PatCycleTarget) -> tuple[float, float]:
    """Returns (baseline_sec, target_sec) in GJ per production unit."""
    baseline_sec = target.baseline_energy_gj / target.baseline_production_qty
    target_sec = baseline_sec * (1 - target.mandated_reduction_percent / 100)
    return baseline_sec, target_sec


class PatSecService:
    def __init__(self, db: Session, organization_id: int):
        self.db = db
        self.organization_id = organization_id
        self.target_repo = PatCycleTargetRepository(db, organization_id)

    # ---- PAT Cycle Targets ----

    def create_target(self, manufacturing_unit_id: int, data: dict) -> dict:
        target = PatCycleTarget(
            organization_id=self.organization_id,
            manufacturing_unit_id=manufacturing_unit_id,
            **data,
        )
        target = self.target_repo.create(target)
        return self._serialize_target(target)

    def list_targets(self, manufacturing_unit_id: int) -> list[dict]:
        targets = self.target_repo.get_by_unit(manufacturing_unit_id)
        return [self._serialize_target(t) for t in targets]

    def update_target(self, target_id: int, data: dict) -> dict | None:
        target = self.target_repo.get_by_id(target_id)
        if target is None:
            return None
        target = self.target_repo.update(target, data)
        return self._serialize_target(target)

    def delete_target(self, target_id: int) -> bool:
        target = self.target_repo.get_by_id(target_id)
        if target is None:
            return False
        self.target_repo.delete(target)
        return True

    def _serialize_target(self, target: PatCycleTarget) -> dict:
        baseline_sec, target_sec = _target_sec(target)
        return {
            "id": target.id,
            "organization_id": target.organization_id,
            "manufacturing_unit_id": target.manufacturing_unit_id,
            "cycle_number": target.cycle_number,
            "cycle_start_year": target.cycle_start_year,
            "cycle_end_year": target.cycle_end_year,
            "baseline_production_qty": target.baseline_production_qty,
            "production_unit": target.production_unit,
            "baseline_energy_gj": target.baseline_energy_gj,
            "mandated_reduction_percent": target.mandated_reduction_percent,
            "baseline_sec_gj_per_unit": round(baseline_sec, 6),
            "target_sec_gj_per_unit": round(target_sec, 6),
            "created_at": target.created_at,
            "updated_at": target.updated_at,
        }

    # ---- PAT-aware summary: reuses existing sec_calculation_service ----

    def get_pat_summary(self, manufacturing_unit_id: int, year: int) -> dict:
        # Existing engine: bills + ProductionRecord -> actual SEC per period.
        engine_summary = sec_calculation_service.get_sec_summary(
            self.db, self.organization_id, manufacturing_unit_id
        )

        year_periods = [
            p
            for p in engine_summary.get("periods", [])
            if p.get("period_start") and p["period_start"].year == year
        ]

        total_energy = sum(p["total_energy_gj"] for p in year_periods if p.get("total_energy_gj") is not None)
        total_production = sum(
            p["production_quantity"] for p in year_periods if p.get("production_quantity") is not None
        )
        actual_sec = round(total_energy / total_production, 6) if total_production else None

        target = self.target_repo.get_active_for_unit(manufacturing_unit_id, year)
        on_track = None
        if target is not None and actual_sec is not None:
            _, target_sec = _target_sec(target)
            on_track = actual_sec <= target_sec

        return {
            "manufacturing_unit_id": manufacturing_unit_id,
            "year": year,
            "actual_energy_gj": round(total_energy, 4) if year_periods else None,
            "actual_production_qty": round(total_production, 4) if year_periods else None,
            "actual_sec_gj_per_unit": actual_sec,
            "target": self._serialize_target(target) if target else None,
            "on_track": on_track,
            "message": (
                None
                if year_periods
                else "No production/energy periods found for this year (add via /production-records)."
            ),
        }
