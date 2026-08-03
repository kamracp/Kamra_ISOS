from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import date

from app.repositories.emission_factor_repository import (
    EmissionFactorRepository,
)
from app.repositories.energy_meter_repository import EnergyMeterRepository
from app.repositories.utility_bill_repository import UtilityBillRepository


@dataclass
class BillEmission:
    """One bill's calculation, with a full audit trail."""

    bill_id: int
    meter_id: int
    meter_code: str
    meter_name: str
    meter_type: str
    unit: str
    scope: str
    period_start: date
    period_end: date
    consumption: float
    co2e_kg: float | None
    factor_id: int | None
    factor_value: float | None
    factor_source: str | None
    status: str  # "calculated" | "no_factor"


class CarbonService:
    """The carbon engine: bills x official factors = CO2e.

    Methodology (GHG Protocol, location-based):
    - Tenant-scoped bills and meters; GLOBAL factor library.
    - Factor lookup date = billing_period_start (deterministic;
      simplification for periods spanning a factor boundary —
      documented, refine later by splitting consumption).
    - Meters with scope "renewable" are reported as AVOIDED
      emissions, never subtracted from Scope 1/2 totals.
    - Bills with no applicable factor are listed as pending,
      never silently skipped and never estimated.
    - Optional year filter (matched against billing_period_start)
      scopes the summary to one calendar year; omitted, it covers
      all available bills exactly as before this option existed.
    """

    def __init__(
        self,
        bill_repository: UtilityBillRepository,
        meter_repository: EnergyMeterRepository,
        factor_repository: EmissionFactorRepository,
    ):
        self.bill_repository = bill_repository
        self.meter_repository = meter_repository
        self.factor_repository = factor_repository

    def _calculate_bills(
        self, year: int | None = None
    ) -> list[BillEmission]:
        bills = self.bill_repository.get_all(year=year)
        meters = {m.id: m for m in self.meter_repository.get_all()}

        results: list[BillEmission] = []

        for bill in bills:
            meter = meters.get(bill.meter_id)
            if meter is None:
                # Meter outside this tenant / deleted — skip defensively.
                continue

            factor = self.factor_repository.find_applicable(
                meter_type=meter.meter_type,
                unit=meter.unit,
                on_date=bill.billing_period_start,
            )

            if factor is None:
                results.append(
                    BillEmission(
                        bill_id=bill.id,
                        meter_id=meter.id,
                        meter_code=meter.meter_code,
                        meter_name=meter.meter_name,
                        meter_type=meter.meter_type,
                        unit=meter.unit,
                        scope=meter.scope,
                        period_start=bill.billing_period_start,
                        period_end=bill.billing_period_end,
                        consumption=bill.consumption,
                        co2e_kg=None,
                        factor_id=None,
                        factor_value=None,
                        factor_source=None,
                        status="no_factor",
                    )
                )
                continue

            co2e_kg = round(
                bill.consumption * factor.factor_kgco2e_per_unit,
                3,
            )

            results.append(
                BillEmission(
                    bill_id=bill.id,
                    meter_id=meter.id,
                    meter_code=meter.meter_code,
                    meter_name=meter.meter_name,
                    meter_type=meter.meter_type,
                    unit=meter.unit,
                    scope=meter.scope,
                    period_start=bill.billing_period_start,
                    period_end=bill.billing_period_end,
                    consumption=bill.consumption,
                    co2e_kg=co2e_kg,
                    factor_id=factor.id,
                    factor_value=factor.factor_kgco2e_per_unit,
                    factor_source=factor.source,
                    status="calculated",
                )
            )

        return results

    def get_summary(self, year: int | None = None) -> dict:
        """Organization-wide emissions summary with full traceability.

        year: optional calendar year to scope the summary to (matched
        against billing_period_start). Omitted, covers all bills —
        unchanged from behavior before this parameter existed, so
        existing callers (e.g. the Dashboard) are unaffected.
        """
        items = self._calculate_bills(year=year)

        totals_by_scope: dict[str, float] = defaultdict(float)
        avoided_kg = 0.0
        monthly: dict[str, float] = defaultdict(float)

        for item in items:
            if item.status != "calculated":
                continue

            month_key = item.period_start.strftime("%Y-%m")

            if item.scope == "renewable":
                avoided_kg += item.co2e_kg
            else:
                totals_by_scope[item.scope] += item.co2e_kg
                monthly[month_key] += item.co2e_kg

        total_kg = round(sum(totals_by_scope.values()), 3)

        return {
            "total_co2e_kg": total_kg,
            "total_co2e_tonnes": round(total_kg / 1000, 3),
            "by_scope_kg": {
                k: round(v, 3) for k, v in sorted(totals_by_scope.items())
            },
            "avoided_co2e_kg": round(avoided_kg, 3),
            "monthly_co2e_kg": {
                k: round(v, 3) for k, v in sorted(monthly.items())
            },
            "bills_calculated": sum(
                1 for i in items if i.status == "calculated"
            ),
            "bills_pending_factor": [
                asdict(i) for i in items if i.status == "no_factor"
            ],
            "line_items": [asdict(i) for i in items],
        }