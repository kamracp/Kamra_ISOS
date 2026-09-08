"""Consumer Responsibility Record Service (BRSR Section C, Principle 9).
One record per organization per year + complaint rows; complaint totals
derived on read (None only when no row discloses the figure)."""
from __future__ import annotations
from decimal import Decimal
from app.repositories.consumer_responsibility_record_repository import ConsumerResponsibilityRecordRepository
from app.models.consumer_responsibility_record import ConsumerResponsibilityRecord, ConsumerComplaint
from app.services.sustainable_product_record_service import DuplicateReportingYear  # noqa: F401

RECORD_FIELDS = (
    "reporting_year", "complaint_mechanism_details",
    "turnover_percent_env_social_info", "turnover_percent_safe_usage_info", "turnover_percent_recycling_info",
    "voluntary_recalls_count", "voluntary_recalls_reasons", "forced_recalls_count", "forced_recalls_reasons",
    "has_cyber_security_policy", "cyber_security_policy_link", "corrective_actions_details",
    "product_information_channels", "consumer_education_details", "service_disruption_disclosure_details",
    "displays_product_info_beyond_mandate", "consumer_survey_conducted", "consumer_survey_details",
    "data_breaches_count", "data_breach_pii_percent", "data_breach_impact_details", "remarks",
)
COMPLAINT_FIELDS = ("category", "received_count", "pending_count", "remarks")


def _num(v):
    return float(v) if isinstance(v, Decimal) else v


def _sum_field(rows, field):
    vals = [getattr(r, field) for r in rows if getattr(r, field) is not None]
    return sum(vals) if vals else None


class ConsumerResponsibilityRecordService:
    def __init__(self, db, organization_id: int):
        self.organization_id = organization_id
        self.repo = ConsumerResponsibilityRecordRepository(db, organization_id)

    def create_record(self, data: dict) -> dict:
        if self.repo.get_by_year(data["reporting_year"]) is not None:
            raise DuplicateReportingYear(data["reporting_year"])
        return self._serialize(self.repo.create(ConsumerResponsibilityRecord(organization_id=self.organization_id, **data)))

    def list_records(self):
        return [self._serialize(r) for r in self.repo.get_all()]

    def get_record(self, record_id: int):
        r = self.repo.get_by_id(record_id)
        return self._serialize(r) if r else None

    def get_by_year(self, year: int):
        r = self.repo.get_by_year(year)
        return self._serialize(r) if r else None

    def update_record(self, record_id: int, data: dict):
        r = self.repo.get_by_id(record_id)
        if r is None:
            return None
        ny = data.get("reporting_year")
        if ny is not None and ny != r.reporting_year and self.repo.get_by_year(ny) is not None:
            raise DuplicateReportingYear(ny)
        return self._serialize(self.repo.update(r, data))

    def delete_record(self, record_id: int) -> bool:
        r = self.repo.get_by_id(record_id)
        if r is None:
            return False
        self.repo.delete(r)
        return True

    def create_complaint(self, record_id: int, data: dict):
        if self.repo.get_by_id(record_id) is None:
            return None
        return self._serialize_complaint(self.repo.create_complaint(ConsumerComplaint(consumer_responsibility_record_id=record_id, **data)))

    def update_complaint(self, complaint_id: int, data: dict):
        c = self.repo.get_complaint_by_id(complaint_id)
        return self._serialize_complaint(self.repo.update_complaint(c, data)) if c else None

    def delete_complaint(self, complaint_id: int) -> bool:
        c = self.repo.get_complaint_by_id(complaint_id)
        if c is None:
            return False
        self.repo.delete_complaint(c)
        return True

    def _serialize(self, r) -> dict:
        out = {"id": r.id, "organization_id": r.organization_id}
        for f in RECORD_FIELDS:
            out[f] = _num(getattr(r, f))
        out["complaints"] = [self._serialize_complaint(c) for c in r.complaints]
        out["total_complaints_received"] = _sum_field(r.complaints, "received_count")
        out["total_complaints_pending"] = _sum_field(r.complaints, "pending_count")
        out["created_at"] = r.created_at
        out["updated_at"] = r.updated_at
        return out

    def _serialize_complaint(self, c) -> dict:
        out = {"id": c.id, "consumer_responsibility_record_id": c.consumer_responsibility_record_id}
        for f in COMPLAINT_FIELDS:
            out[f] = _num(getattr(c, f))
        out["created_at"] = c.created_at
        out["updated_at"] = c.updated_at
        return out
