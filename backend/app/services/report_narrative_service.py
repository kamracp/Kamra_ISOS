from typing import Optional, Dict, Any

from sqlalchemy.orm import Session

from app.models.report_narrative import ReportNarrative
from app.repositories.report_narrative_repository import ReportNarrativeRepository
from app.schemas.report_narrative import ReportNarrativeUpdate

# Entity-level narrative items counted for completeness.
# theme_colour is styling, not disclosure, so it is not counted.
ENTITY_ITEMS = {
    "cover_title": "Cover title",
    "about_company": "About the company",
    "leadership_message": "Leadership message",
    "milestones": "Milestones (at least one)",
}
PRINCIPLE_COUNT = 9


def _filled(value) -> bool:
    if value is None:
        return False
    if isinstance(value, (str, list, dict)):
        return len(value) > 0
    return True


class ReportNarrativeService:
    def __init__(self, db: Session, organization_id: int):
        self.repo = ReportNarrativeRepository(db, organization_id)

    def get(self, year: int) -> Optional[ReportNarrative]:
        return self.repo.get_by_year(year)

    def list_years(self) -> list[int]:
        return self.repo.list_years()

    def upsert(self, year: int, payload: ReportNarrativeUpdate) -> ReportNarrative:
        # exclude_unset -> partial update; mode="json" -> nested models
        # become plain dicts/lists so they can be stored in JSONB.
        data = payload.model_dump(exclude_unset=True, mode="json")
        return self.repo.upsert(year, data)

    def delete(self, year: int) -> bool:
        return self.repo.delete_by_year(year)

    def get_completeness(self, year: int) -> Dict[str, Any]:
        row = self.repo.get_by_year(year)
        missing: list[str] = []

        entity_answered = 0
        for field, label in ENTITY_ITEMS.items():
            if row is not None and _filled(getattr(row, field)):
                entity_answered += 1
            else:
                missing.append(label)

        # A principle counts as written when it has a highlight or an intro.
        written = set()
        for p in (row.principle_narratives or []) if row else []:
            if _filled(p.get("highlight")) or _filled(p.get("intro")):
                written.add(p["principle"])
        principles = {}
        for n in range(1, PRINCIPLE_COUNT + 1):
            principles[n] = n in written
            if n not in written:
                missing.append(f"Principle {n} narrative")

        total = len(ENTITY_ITEMS) + PRINCIPLE_COUNT
        answered = entity_answered + len(written)
        return {
            "reporting_year": year,
            "exists": row is not None,
            "answered": answered,
            "total": total,
            "percent": round(answered * 100 / total, 1),
            "entity_answered": entity_answered,
            "entity_total": len(ENTITY_ITEMS),
            "principles": principles,
            "missing": missing,
        }
