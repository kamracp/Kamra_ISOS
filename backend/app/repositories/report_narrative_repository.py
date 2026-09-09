from typing import Optional, Dict, Any

from sqlalchemy.orm import Session

from app.models.report_narrative import ReportNarrative


class ReportNarrativeRepository:
    """Tenant-scoped access to report_narratives. One row per (org, year)."""

    def __init__(self, db: Session, organization_id: int):
        self.db = db
        self.organization_id = organization_id

    def _base_query(self):
        # The ONLY place the tenant filter lives.
        return self.db.query(ReportNarrative).filter(
            ReportNarrative.organization_id == self.organization_id
        )

    def get_by_year(self, year: int) -> Optional[ReportNarrative]:
        return self._base_query().filter(
            ReportNarrative.reporting_year == year
        ).first()

    def list_years(self) -> list[int]:
        rows = self._base_query().with_entities(
            ReportNarrative.reporting_year
        ).order_by(ReportNarrative.reporting_year.desc()).all()
        return [r[0] for r in rows]

    def upsert(self, year: int, data: Dict[str, Any]) -> ReportNarrative:
        """
        `data` holds only the fields the caller actually sent
        (exclude_unset applied in the service), so untouched columns
        keep their value on update.
        """
        row = self.get_by_year(year)
        if row is None:
            row = ReportNarrative(
                organization_id=self.organization_id, reporting_year=year
            )
            self.db.add(row)
        for key, value in data.items():
            setattr(row, key, value)
        self.db.commit()
        self.db.refresh(row)
        return row

    def delete_by_year(self, year: int) -> bool:
        row = self.get_by_year(year)
        if row is None:
            return False
        self.db.delete(row)
        self.db.commit()
        return True
