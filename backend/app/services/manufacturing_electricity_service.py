"""
Manufacturing Electricity Service (Scope 2 purchased electricity for
ManufactureOS). Manages raw kWh records and derives Scope 2 CO2e --
never stored -- by looking up each record's manufacturing unit's
country_code in app.services.country_config and applying that
country's location-based grid factor to (consumed - renewable) kWh.

This is the piece that makes ManufactureOS's carbon accounting
actually global: a unit in the UK, US, UAE, or Australia gets that
country's real grid factor, not an assumed India default.
"""
from __future__ import annotations
from app.repositories.manufacturing_electricity_record_repository import (
    ManufacturingElectricityRecordRepository,
)
from app.repositories.manufacturing_unit_repository import ManufacturingUnitRepository
from app.models.manufacturing_electricity_record import ManufacturingElectricityRecord
from app.services.scope2_calculator import calculate_scope2


class ManufacturingElectricityService:
    def __init__(
        self,
        electricity_repository: ManufacturingElectricityRecordRepository,
        unit_repository: ManufacturingUnitRepository,
    ):
        self.electricity_repository = electricity_repository
        self.unit_repository = unit_repository

    def create_record(self, data) -> dict:
        db_record = self.electricity_repository.create(data)
        return self._serialize(db_record)

    def list_records(self, year: int | None = None) -> list[dict]:
        records = self.electricity_repository.get_all(year=year)
        return [self._serialize(r) for r in records]

    def list_by_unit(self, manufacturing_unit_id: int, year: int | None = None) -> list[dict]:
        records = self.electricity_repository.get_by_unit(manufacturing_unit_id, year=year)
        return [self._serialize(r) for r in records]

    def get_record(self, record_id: int) -> dict | None:
        record = self.electricity_repository.get_by_id(record_id)
        return self._serialize(record) if record else None

    def update_record(self, record_id: int, data) -> dict | None:
        record = self.electricity_repository.get_by_id(record_id)
        if record is None:
            return None
        record = self.electricity_repository.update(record, data)
        return self._serialize(record)

    def delete_record(self, record_id: int) -> bool:
        record = self.electricity_repository.get_by_id(record_id)
        if record is None:
            return False
        self.electricity_repository.delete(record)
        return True

    def _serialize(self, record: ManufacturingElectricityRecord) -> dict:
        """Attach derived Scope 2 CO2e using the unit's country grid factor.
        scope2_co2e_kg stays None (not zero) when the country has no
        verified grid factor yet -- never guess a number.
        """
        unit = self.unit_repository.get_by_id(record.manufacturing_unit_id)
        country_code = unit.country_code if unit else "IN"
        scope2 = calculate_scope2(
            country_code, record.electricity_consumed_kwh, record.renewable_kwh
        )
        scope2_co2e_kg = scope2["scope2_co2e_kg"]
        grid_factor = scope2["grid_factor_kgco2e_per_kwh"]
        grid_factor_source = scope2["grid_factor_source"]

        return {
            "id": record.id,
            "organization_id": record.organization_id,
            "manufacturing_unit_id": record.manufacturing_unit_id,
            "period_start": record.period_start,
            "period_end": record.period_end,
            "electricity_consumed_kwh": record.electricity_consumed_kwh,
            "renewable_kwh": record.renewable_kwh,
            "source": record.source,
            "remarks": record.remarks,
            "scope2_co2e_kg": scope2_co2e_kg,
            "grid_factor_kgco2e_per_kwh": grid_factor,
            "grid_factor_source": grid_factor_source,
            "created_at": record.created_at,
            "updated_at": record.updated_at,
        }
