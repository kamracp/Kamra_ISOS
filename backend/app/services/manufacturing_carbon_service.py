"""
Manufacturing Carbon Service -- the ManufactureOS counterpart to
CarbonService (BENAS). Sums persisted ManufacturingEmissionRecord rows
into a per-unit + organization-wide Scope 1 summary, mirroring
CarbonService.get_summary()'s shape so both can eventually be
consolidated into one org-level ESG total (see esg_report_service.py).

Unlike CarbonService (which computes bills live, on the fly), this
service sums already-computed, persisted calculator results -- because
sector calculators need detailed process inputs (CaO%, material lists)
that only a human/engineer can supply per run; there's nothing to
compute live from ProductionRecord alone.
"""
from collections import defaultdict
from dataclasses import asdict, dataclass

from app.repositories.manufacturing_emission_record_repository import (
    ManufacturingEmissionRecordRepository,
)
from app.repositories.manufacturing_unit_repository import ManufacturingUnitRepository


@dataclass
class UnitEmission:
    """One manufacturing unit's total for a period, with traceability."""

    manufacturing_unit_id: int
    unit_code: str
    unit_name: str
    sector: str
    co2_tonnes: float
    biogenic_co2_tonnes: float
    record_count: int


class ManufacturingCarbonService:
    """Sums persisted ManufacturingEmissionRecord rows per unit and org-wide.

    Methodology:
    - All sector calculator results (Cement CSI, Aluminium Tier-1,
      Iron & Steel mass-balance, Pulp & Paper biomass, Refrigerant
      lifecycle, CHP allocation) are Scope 1 process emissions.
    - Biogenic CO2 (e.g. Pulp & Paper biomass combustion) is tracked
      separately, never summed into the fossil Scope 1 total -- same
      convention as CarbonService's renewable-meter handling.
    - Units with no emission records yet are listed with zero totals,
      never silently omitted -- so a manufacturing unit's absence from
      totals is always visible, not ambiguous.
    """

    def __init__(
        self,
        emission_record_repository: ManufacturingEmissionRecordRepository,
        unit_repository: ManufacturingUnitRepository,
    ):
        self.emission_record_repository = emission_record_repository
        self.unit_repository = unit_repository

    def get_summary(self, year: int | None = None) -> dict:
        """Organization-wide Scope 1 process-emissions summary.

        year: optional calendar year to scope the summary to (matched
        against period_start). Omitted, covers all persisted records.
        """
        units = {u.id: u for u in self.unit_repository.get_all()}
        records = self.emission_record_repository.get_all(year=year)

        by_unit: dict[int, UnitEmission] = {}
        for unit_id, unit in units.items():
            by_unit[unit_id] = UnitEmission(
                manufacturing_unit_id=unit.id,
                unit_code=unit.unit_code,
                unit_name=unit.unit_name,
                sector=unit.sector.value,
                co2_tonnes=0.0,
                biogenic_co2_tonnes=0.0,
                record_count=0,
            )

        for record in records:
            entry = by_unit.get(record.manufacturing_unit_id)
            if entry is None:
                # Unit outside this tenant / deleted -- skip defensively.
                continue
            if record.is_biogenic:
                entry.biogenic_co2_tonnes += record.co2_tonnes
            else:
                entry.co2_tonnes += record.co2_tonnes
            entry.record_count += 1

        total_co2_tonnes = round(
            sum(e.co2_tonnes for e in by_unit.values()), 3
        )
        total_biogenic_co2_tonnes = round(
            sum(e.biogenic_co2_tonnes for e in by_unit.values()), 3
        )

        by_sector: dict[str, float] = defaultdict(float)
        for entry in by_unit.values():
            by_sector[entry.sector] += entry.co2_tonnes

        return {
            "total_co2_tonnes": total_co2_tonnes,
            "total_biogenic_co2_tonnes": total_biogenic_co2_tonnes,
            "by_sector_tonnes": {
                k: round(v, 3) for k, v in sorted(by_sector.items())
            },
            "units_with_records": sum(
                1 for e in by_unit.values() if e.record_count > 0
            ),
            "units_total": len(by_unit),
            "by_unit": [asdict(e) for e in by_unit.values()],
        }
