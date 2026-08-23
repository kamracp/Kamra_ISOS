"""Repository for PatCycleTarget -- tenant-scoped via organization_id."""
from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.pat_cycle_target import PatCycleTarget


class PatCycleTargetRepository:
    def __init__(self, db: Session, organization_id: int):
        self.db = db
        self.organization_id = organization_id

    def _base_query(self):
        return select(PatCycleTarget).where(
            PatCycleTarget.organization_id == self.organization_id
        )

    def get_by_id(self, target_id: int) -> PatCycleTarget | None:
        stmt = self._base_query().where(PatCycleTarget.id == target_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_unit(self, manufacturing_unit_id: int) -> list[PatCycleTarget]:
        stmt = self._base_query().where(
            PatCycleTarget.manufacturing_unit_id == manufacturing_unit_id
        ).order_by(PatCycleTarget.cycle_start_year.desc())
        return list(self.db.execute(stmt).scalars().all())

    def get_active_for_unit(self, manufacturing_unit_id: int, year: int) -> PatCycleTarget | None:
        stmt = self._base_query().where(
            PatCycleTarget.manufacturing_unit_id == manufacturing_unit_id,
            PatCycleTarget.cycle_start_year <= year,
            PatCycleTarget.cycle_end_year >= year,
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def create(self, target: PatCycleTarget) -> PatCycleTarget:
        self.db.add(target)
        self.db.commit()
        self.db.refresh(target)
        return target

    def update(self, target: PatCycleTarget, data: dict) -> PatCycleTarget:
        for key, value in data.items():
            setattr(target, key, value)
        self.db.commit()
        self.db.refresh(target)
        return target

    def delete(self, target: PatCycleTarget) -> None:
        self.db.delete(target)
        self.db.commit()
