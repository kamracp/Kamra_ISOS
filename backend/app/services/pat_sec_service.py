"""
PAT SEC Service (Manufacturing / Energy module)
Computes actual Specific Energy Consumption (SEC) per manufacturing
unit per year from measured EnergyProductionRecord rows, compares
against the applicable PatCycleTarget's derived target SEC.
Conversion constant: 1 toe = 41.868 GJ (IPCC/BEE standard).
"""
from __future__ import annotations
from app.repositories.pat_cycle_target_repository import PatCycleTargetRepository
from app.repositories.energy_production_record_repository import (
    EnergyProductionRecordRepository,
)
from app.models.pat_cycle_target import PatCycleTarget
from app.models.energy_production_record import EnergyProductionRecord

GJ_PER_TOE = 41.868


def _to_toe(energy_gj: float) -> float:
    return energy_gj / GJ_PER_TOE


def _target_sec(target: PatCycleTarget) -> tuple[float, float]:
    """Returns (baseline_sec, target_sec) in GJ per production unit."""
    baseline_sec = target.baseline_energy_gj / target.baseline_production_qty
    target_sec = baseline_sec * (1 - target.mandated_reduction_percent / 100)
    return baseline_sec, target_sec


class PatSecService:
    def __init__(self, db, organization_id: int):
        self.organization_id = organization_id
        self.target_repo = PatCycleTargetRepository(db, organization_id)
        self.record_repo = EnergyProductionRecordRepository(db, organization_id)

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

    # ---- Energy/Production Records ----

    def create_record(self, manufacturing_unit_id: int, data: dict) -> dict:
        record = EnergyProductionRecord(
            organization_id=self.organization_id,
            manufacturing_unit_id=manufacturing_unit_id,
            **data,
        )
        record = self.record_repo.create(record)
        return self._serialize_record(record)

    def list_records(self, manufacturing_unit_id: int, year: int | None = None) -> list[dict]:
        records = self.record_repo.get_by_unit(manufacturing_unit_id, year)
        return [self._serialize_record(r) for r in records]

    def update_record(self, record_id: int, data: dict) -> dict | None:
        record = self.record_repo.get_by_id(record_id)
        if record is None:
            return None
        record = self.record_repo.update(record, data)
        return self._serialize_record(record)

    def delete_record(self, record_id: int) -> bool:
        record = self.record_repo.get_by_id(record_id)
        if record is None:
            return False
        self.record_repo.delete(record)
        return True

    def _serialize_record(self, record: EnergyProductionRecord) -> dict:
        sec = record.energy_consumed_gj / record.production_quantity
        return {
            "id": record.id,
            "organization_id": record.organization_id,
            "manufacturing_unit_id": record.manufacturing_unit_id,
            "period_start": record.period_start,
            "period_end": record.period_end,
            "energy_consumed_gj": record.energy_consumed_gj,
            "production_quantity": record.production_quantity,
            "production_unit": record.production_unit,
            "energy_consumed_toe": round(_to_toe(record.energy_consumed_gj), 4),
            "sec_gj_per_unit": round(sec, 6),
            "created_at": record.created_at,
            "updated_at": record.updated_at,
        }

    # ---- Summary: actual SEC vs target for a year ----

    def get_sec_summary(self, manufacturing_unit_id: int, year: int) -> dict:
        records = self.record_repo.get_by_unit(manufacturing_unit_id, year)
        target = self.target_repo.get_active_for_unit(manufacturing_unit_id, year)

        if not records:
            return {
                "manufacturing_unit_id": manufacturing_unit_id,
                "year": year,
                "actual_energy_gj": None,
                "actual_production_qty": None,
                "actual_sec_gj_per_unit": None,
                "actual_energy_toe": None,
                "target": self._serialize_target(target) if target else None,
                "on_track": None,
                "message": "No energy/production records for this year.",
            }

        total_energy = sum(r.energy_consumed_gj for r in records)
        total_production = sum(r.production_quantity for r in records)
        actual_sec = total_energy / total_production if total_production else None

        on_track = None
        if target is not None and actual_sec is not None:
            _, target_sec = _target_sec(target)
            on_track = actual_sec <= target_sec

        return {
            "manufacturing_unit_id": manufacturing_unit_id,
            "year": year,
            "actual_energy_gj": round(total_energy, 4),
            "actual_production_qty": round(total_production, 4),
            "actual_sec_gj_per_unit": round(actual_sec, 6) if actual_sec else None,
            "actual_energy_toe": round(_to_toe(total_energy), 4),
            "target": self._serialize_target(target) if target else None,
            "on_track": on_track,
            "message": None if target else "No PAT cycle target covers this year.",
        }
