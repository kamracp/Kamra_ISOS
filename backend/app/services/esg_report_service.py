"""
ESG Report generation service for Kamra ClimateOS.

Aggregator + formatter, not a new calculator: maps existing platform
data (CarbonService Scope 1/2) into standards report structures.
Frameworks: BRSR Section C Principle 6 (Environment), GRI 305
(Emissions). Untracked datapoints are marked "not_tracked", never
guessed.
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


def _get_scope_summary(db, organization_id, reporting_year):
    """Shared helper: run CarbonService for one org/year, return (scope1_t, scope2_t, src)."""
    carbon = CarbonService(
        bill_repository=UtilityBillRepository(db, organization_id=organization_id),
        meter_repository=EnergyMeterRepository(db, organization_id=organization_id),
        factor_repository=EmissionFactorRepository(db),
    )
    summary = carbon.get_summary(year=reporting_year)
    by_scope_kg = summary.get("by_scope_kg", {})
    scope1_t = round(by_scope_kg.get("scope_1", 0.0) / 1000, 3)
    scope2_t = round(by_scope_kg.get("scope_2", 0.0) / 1000, 3)
    src = f"CarbonService (year {reporting_year} bills, org {organization_id})"
    return scope1_t, scope2_t, src


def generate_brsr_principle6(db: Session, organization_id: int,
                             reporting_year: int) -> dict:
    """BRSR Section C, Principle 6 (Environment) -- Essential Indicators."""
    scope1_t, scope2_t, src = _get_scope_summary(db, organization_id, reporting_year)

    return {
        "framework": "BRSR",
        "section": "Section C, Principle 6 (Environment)",
        "reporting_year": reporting_year,
        "organization_id": organization_id,
        "data_basis": f"Utility-bill data with billing period starting in calendar year {reporting_year}.",
        "essential_indicators": _build_brsr_indicators(scope1_t, scope2_t, src),
        "totals": {
            "scope1_plus_2_tCO2e": round(scope1_t + scope2_t, 3),
            "total_all_scopes": _tracked(
                round(scope1_t + scope2_t, 3), "tCO2e",
                src + " (Scope 1+2 only; Scope 3 not tracked)",
            ),
        },
    }


def _build_brsr_indicators(scope1_t, scope2_t, src):
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


def generate_gri_305(db: Session, organization_id: int,
                     reporting_year: int) -> dict:
    """GRI 305 (Emissions) -- core disclosures 305-1 to 305-7."""
    scope1_t, scope2_t, src = _get_scope_summary(db, organization_id, reporting_year)

    return {
        "framework": "GRI 305",
        "section": "Emissions",
        "reporting_year": reporting_year,
        "organization_id": organization_id,
        "data_basis": f"Utility-bill data with billing period starting in calendar year {reporting_year}.",
        "essential_indicators": _build_gri_indicators(scope1_t, scope2_t, src),
        "totals": {
            "scope1_plus_2_tCO2e": round(scope1_t + scope2_t, 3),
            "total_all_scopes": _tracked(
                round(scope1_t + scope2_t, 3), "tCO2e",
                src + " (Scope 1+2 only; Scope 3 not tracked)",
            ),
        },
    }


def _build_gri_indicators(scope1_t, scope2_t, src):
    """GRI 305 core disclosures. Emissions filled, rest not_tracked."""
    return {
        "305_1_direct_ghg": {
            "label": "305-1 Direct (Scope 1) GHG emissions",
            "data": _tracked(scope1_t, "tCO2e", src),
        },
        "305_2_energy_indirect_ghg": {
            "label": "305-2 Energy indirect (Scope 2) GHG emissions, location-based",
            "data": _tracked(scope2_t, "tCO2e", src),
        },
        "305_3_other_indirect_ghg": {
            "label": "305-3 Other indirect (Scope 3) GHG emissions",
            "data": NOT_TRACKED,
        },
        "305_4_ghg_intensity": {
            "label": "305-4 GHG emissions intensity",
            "data": NOT_TRACKED,
            "note": "No intensity denominator (revenue/output/floor area) tracked yet.",
        },
        "305_5_ghg_reduction": {
            "label": "305-5 Reduction of GHG emissions",
            "data": NOT_TRACKED,
            "note": "See the platform's Net Zero Action Plan module for target-vs-actual tracking, not yet mapped into this disclosure.",
        },
        "305_6_ods": {
            "label": "305-6 Emissions of ozone-depleting substances (ODS)",
            "data": NOT_TRACKED,
        },
        "305_7_other_air_emissions": {
            "label": "305-7 NOx, SOx, and other significant air emissions",
            "data": NOT_TRACKED,
        },
    }