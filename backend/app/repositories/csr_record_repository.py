"""Repository for CsrRecord + CsrProject -- tenant-scoped via organization_id."""
from __future__ import annotations
from sqlalchemy.orm import Session, joinedload
from app.models.csr_record import CsrRecord, CsrProject


class CsrRecordRepository:
    def __init__(self, db: Session, organization_id: int):
        self.db = db
        self.organization_id = organization_id

    def _base_query(self):
        return (
            self.db.query(CsrRecord)
            .options(joinedload(CsrRecord.projects))
            .filter(CsrRecord.organization_id == self.organization_id)
        )

    def get_all(self) -> list[CsrRecord]:
        return self._base_query().order_by(CsrRecord.reporting_year.desc()).all()

    def get_by_id(self, record_id: int) -> CsrRecord | None:
        return self._base_query().filter(CsrRecord.id == record_id).first()

    def get_by_year(self, year: int) -> CsrRecord | None:
        return self._base_query().filter(CsrRecord.reporting_year == year).first()

    def create(self, record: CsrRecord) -> CsrRecord:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def update(self, record: CsrRecord, data: dict) -> CsrRecord:
        for key, value in data.items():
            setattr(record, key, value)
        self.db.commit()
        self.db.refresh(record)
        return record

    def delete(self, record: CsrRecord) -> None:
        self.db.delete(record)
        self.db.commit()

    # ---- Projects (child of a record the caller already owns/verified) ----

    def get_project_by_id(self, project_id: int) -> CsrProject | None:
        return (
            self.db.query(CsrProject)
            .join(CsrRecord)
            .filter(
                CsrProject.id == project_id,
                CsrRecord.organization_id == self.organization_id,
            )
            .first()
        )

    def create_project(self, project: CsrProject) -> CsrProject:
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def update_project(self, project: CsrProject, data: dict) -> CsrProject:
        for key, value in data.items():
            setattr(project, key, value)
        self.db.commit()
        self.db.refresh(project)
        return project

    def delete_project(self, project: CsrProject) -> None:
        self.db.delete(project)
        self.db.commit()
