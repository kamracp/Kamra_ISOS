"""
Ethics Record Service (BRSR Section C, Principle 1)
Manages anti-corruption training/disciplinary/complaints records and
derives training-coverage percentages -- never stores them, same
discipline as PAT SEC / water-waste / CSR totals.
"""
from __future__ import annotations
from app.repositories.ethics_record_repository import EthicsRecordRepository
from app.models.ethics_record import EthicsRecord


def _percent(trained, total):
    if trained is None or total is None or total == 0:
        return None
    return round(float(trained) / float(total) * 100, 2)


class EthicsRecordService:
    def __init__(self, db, organization_id: int):
        self.organization_id = organization_id
        self.repo = EthicsRecordRepository(db, organization_id)

    def create_record(self, data: dict) -> dict:
        record = EthicsRecord(organization_id=self.organization_id, **data)
        record = self.repo.create(record)
        return self._serialize(record)

    def list_records(self) -> list[dict]:
        return [self._serialize(r) for r in self.repo.get_all()]

    def get_record(self, record_id: int) -> dict | None:
        record = self.repo.get_by_id(record_id)
        return self._serialize(record) if record else None

    def get_by_year(self, year: int) -> dict | None:
        record = self.repo.get_by_year(year)
        return self._serialize(record) if record else None

    def update_record(self, record_id: int, data: dict) -> dict | None:
        record = self.repo.get_by_id(record_id)
        if record is None:
            return None
        record = self.repo.update(record, data)
        return self._serialize(record)

    def delete_record(self, record_id: int) -> bool:
        record = self.repo.get_by_id(record_id)
        if record is None:
            return False
        self.repo.delete(record)
        return True

    def _serialize(self, record: EthicsRecord) -> dict:
        return {
            "id": record.id,
            "organization_id": record.organization_id,
            "reporting_year": record.reporting_year,
            "board_kmp_total_count": record.board_kmp_total_count,
            "board_kmp_trained_count": record.board_kmp_trained_count,
            "employees_total_count": record.employees_total_count,
            "employees_trained_count": record.employees_trained_count,
            "workers_total_count": record.workers_total_count,
            "workers_trained_count": record.workers_trained_count,
            "disciplinary_actions_directors": record.disciplinary_actions_directors,
            "disciplinary_actions_kmp": record.disciplinary_actions_kmp,
            "disciplinary_actions_employees": record.disciplinary_actions_employees,
            "disciplinary_actions_workers": record.disciplinary_actions_workers,
            "fines_penalties_amount_inr": record.fines_penalties_amount_inr,
            "has_conflict_of_interest_process": record.has_conflict_of_interest_process,
            "conflict_of_interest_disclosures_count": record.conflict_of_interest_disclosures_count,
            "corruption_complaints_received": record.corruption_complaints_received,
            "corruption_complaints_pending": record.corruption_complaints_pending,
            "remarks": record.remarks,
            "board_kmp_trained_percent": _percent(
                record.board_kmp_trained_count, record.board_kmp_total_count
            ),
            "employees_trained_percent": _percent(
                record.employees_trained_count, record.employees_total_count
            ),
            "workers_trained_percent": _percent(
                record.workers_trained_count, record.workers_total_count
            ),
            "created_at": record.created_at,
            "updated_at": record.updated_at,
        }
