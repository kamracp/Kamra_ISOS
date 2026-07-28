"""
ESG Report generation service for Kamra ClimateOS.

Aggregator + formatter, not a new calculator: maps existing platform
data (CarbonService Scope 1/2) into standards report structures.
First framework: BRSR Section C, Principle 6 (Environment). Untracked
datapoints are marked "not_tracked", never guessed.
"""

from sqlalchemy.orm import Session

from app.repositories.emission_factor_repository import EmissionFactorRepository
from app.repositories.energy_meter_repository import EnergyMeterRepository
from app.repositories.utility_bill_repository import UtilityBillRepository
from app.services.carbon_service import CarbonService

NOT_TRACKED = {
    "value": None,
    "status": "not_tracked",
    "note": "Not yet tracked on the platform; to be collected.",
}


def _tracked(value, unit, source):
    return {"value": value, "unit": unit, "status": "tracked", "source": source}


def generate_brsr_principle6(db: Session, organization_id: int,
                             reporting_year: int) -> dict:
    """BRSR Section C, Principle 6 (Environment) -- Essential Indicators."""
    carbon = CarbonService(
        bill_repository=UtilityBillRepository(db, organization_id=organization_id),
        meter_repository=EnergyMeterRepository(db, organization_id=organization_id),
        factor_repository=EmissionFactorRepository(db),
    )
    summary = carbon.get_summary()
    by_scope_kg = summary.get("by_scope_kg", {})
    scope1_t = round(by_scope_kg.get("scope_1", 0.0) / 1000, 3)
    scope2_t = round(by_scope_kg.get("scope_2", 0.0) / 1000, 3)
    src = f"CarbonService (all available bills, org {organization_id})"

    return {
        "framework": "BRSR",
        "section": "Section C, Principle 6 (Environment)",
        "reporting_year": reporting_year,
        "organization_id": organization_id,
        "data_basis": "All available utility-bill data (not yet year-filtered).",
        "essential_indicators": _build_indicators(scope1_t, scope2_t, src),
        "totals": {
            "scope1_plus_2_tCO2e": round(scope1_t + scope2_t, 3),
            "total_all_scopes": _tracked(
                round(scope1_t + scope2_t, 3), "tCO2e",
                src + " (Scope 1+2 only; Scope 3 not tracked)",
            ),
        },
    }


def _build_indicators(scope1_t, scope2_t, src):
    """BRSR Principle 6 Essential Indicators. Emissions filled, rest not_tracked."""
    return {
        "EI_1_energy_consumption": {
            "label": "Total energy consumption (renewable & non-renewable)",
            "renewable_gj": NOT_TRACKED,
            "non_renewable_gj": NOT_TRACKED,
            "note": "Energy in GJ available via SEC engine per unit; org-wide split not yet aggregated here.",
        },
        "EI_3_energy_intensity": {
            "label": "Energy intensity per rupee of turnover",
            "data": NOT_TRACKED,
            "note": "Turnover not tracked on the platform.",
        },
        "EI_7_ghg_scope1": {
            "label": "Total Scope 1 emissions (tCO2e)",
            "data": _tracked(scope1_t, "tCO2e", src),
        },
        "EI_7_ghg_scope2": {
            "label": "Total Scope 2 emissions (tCO2e)",
            "data": _tracked(scope2_t, "tCO2e", src),
        },
        "EI_7_ghg_scope3": {
            "label": "Total Scope 3 emissions (tCO2e)",
            "data": NOT_TRACKED,
        },
        "EI_7_ghg_intensity": {
            "label": "GHG emission intensity per rupee of turnover",
            "data": NOT_TRACKED,
            "note": "Turnover not tracked on the platform.",
        },
        "EI_2_water_withdrawal": {
            "label": "Water withdrawal by source (kL)",
            "data": NOT_TRACKED,
        },
        "EI_5_air_emissions": {
            "label": "Air emissions NOx / SOx / PM (excl. GHG)",
            "data": NOT_TRACKED,
        },
        "EI_8_waste_generated": {
            "label": "Total waste generated (MT)",
            "data": NOT_TRACKED,
        },
    }
