"""
ESG Report generation service for Kamra ClimateOS.

Aggregator + formatter, not a new calculator: maps existing platform
data (CarbonService Scope 1/2) into standards report structures.
Frameworks: BRSR Section C Principle 6 (Environment), GRI 305
(Emissions), ESRS E1 (Climate Change / CSRD). Untracked datapoints are
marked "not_tracked", never guessed.
"""

from sqlalchemy.orm import Session

from app.repositories.emission_factor_repository import EmissionFactorRepository
from app.repositories.energy_meter_repository import EnergyMeterRepository
from app.repositories.utility_bill_repository import UtilityBillRepository
from app.services.carbon_service import CarbonService
from app.models.organization import Organization

NOT_TRACKED = {
    "value": None,
    "status": "not_tracked",
    "note": "Not yet tracked on the platform; to be collected.",
}


def _tracked(value, unit, source, standard=None):
    """standard: optional list of distinct emission-factor citations
    (e.g. ["CEA CO2 Baseline Database ... Version 21.0"]) actually used
    to compute this value. Only set for datapoints that trace directly
    to the emission factor library -- never collapsed to a single
    string when multiple factor versions contributed, so an auditor
    always sees every standard actually in play, not an implied one.
    """
    result = {"value": value, "unit": unit, "status": "tracked", "source": source}
    if standard:
        result["standard"] = standard
    return result


def _get_scope_summary(db, organization_id, reporting_year):
    """Shared helper: run CarbonService for one org/year, return
    (scope1_t, scope2_t, src, scope1_standards, scope2_standards).

    scope*_standards: sorted list of distinct emission_factors.source
    strings actually used across that scope's calculated bills for the
    year -- can have more than one entry if a factor version changed
    mid-year (e.g. CEA v20 -> v21), and that is reported as-is rather
    than picked down to one.
    """
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

    line_items = summary.get("line_items", [])
    scope1_standards = sorted({
        item["factor_source"]
        for item in line_items
        if item["status"] == "calculated"
        and item["scope"] == "scope_1"
        and item["factor_source"]
    })
    scope2_standards = sorted({
        item["factor_source"]
        for item in line_items
        if item["status"] == "calculated"
        and item["scope"] == "scope_2"
        and item["factor_source"]
    })

    return scope1_t, scope2_t, src, scope1_standards, scope2_standards


def _get_intensity_metrics(db, organization_id, total_scope1_2_t):
    """Compute tCO2e per employee and tCO2e per Rs crore revenue, if data is tracked."""
    org = db.query(Organization).filter(Organization.id == organization_id).first()
    result = {}

    if org and org.employee_count:
        result["intensity_per_employee_tco2e"] = _tracked(
            round(total_scope1_2_t / org.employee_count, 4),
            "tCO2e/employee",
            f"Scope 1+2 ({total_scope1_2_t} tCO2e) / {org.employee_count} employees",
        )
    else:
        result["intensity_per_employee_tco2e"] = NOT_TRACKED

    if org and org.annual_revenue_inr:
        revenue_crore = float(org.annual_revenue_inr) / 1e7
        result["intensity_per_revenue_tco2e"] = _tracked(
            round(total_scope1_2_t / revenue_crore, 4),
            "tCO2e/Rs crore",
            f"Scope 1+2 ({total_scope1_2_t} tCO2e) / Rs {revenue_crore:.2f} crore revenue",
        )
    else:
        result["intensity_per_revenue_tco2e"] = NOT_TRACKED

    return result


def generate_brsr_principle6(db: Session, organization_id: int,
                             reporting_year: int) -> dict:
    """BRSR Section C, Principle 6 (Environment) -- Essential Indicators."""
    scope1_t, scope2_t, src, scope1_std, scope2_std = _get_scope_summary(
        db, organization_id, reporting_year
    )

    return {
        "framework": "BRSR",
        "section": "Section C, Principle 6 (Environment)",
        "reporting_year": reporting_year,
        "organization_id": organization_id,
        "data_basis": f"Utility-bill data with billing period starting in calendar year {reporting_year}.",
        "essential_indicators": _build_brsr_indicators(
            scope1_t, scope2_t, src, scope1_std, scope2_std,
            intensity=_get_intensity_metrics(db, organization_id, round(scope1_t + scope2_t, 3)),
        ),
        "totals": {
            "scope1_plus_2_tCO2e": round(scope1_t + scope2_t, 3),
            "total_all_scopes": _tracked(
                round(scope1_t + scope2_t, 3), "tCO2e",
                src + " (Scope 1+2 only; Scope 3 not tracked)",
                standard=sorted(set(scope1_std) | set(scope2_std)),
            ),
        },
    }


def _build_brsr_indicators(scope1_t, scope2_t, src, scope1_std, scope2_std, intensity=None):
    intensity = intensity or {}
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
            "data": _tracked(scope1_t, "tCO2e", src, standard=scope1_std),
        },
        "EI_7_ghg_scope2": {
            "label": "Total Scope 2 emissions (tCO2e)",
            "data": _tracked(scope2_t, "tCO2e", src, standard=scope2_std),
        },
        "EI_7_ghg_scope3": {
            "label": "Total Scope 3 emissions (tCO2e)",
            "data": NOT_TRACKED,
        },
        "EI_7_ghg_intensity": {
            "label": "GHG emission intensity per rupee of turnover",
            "data": intensity.get("intensity_per_revenue_tco2e", NOT_TRACKED),
            "note": "tCO2e per Rs crore of annual revenue, as set in organization profile.",
        },
        "EI_7_ghg_intensity_per_employee": {
            "label": "GHG emission intensity per employee",
            "data": intensity.get("intensity_per_employee_tco2e", NOT_TRACKED),
            "note": "tCO2e per employee, as set in organization profile.",
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
    scope1_t, scope2_t, src, scope1_std, scope2_std = _get_scope_summary(
        db, organization_id, reporting_year
    )

    return {
        "framework": "GRI 305",
        "section": "Emissions",
        "reporting_year": reporting_year,
        "organization_id": organization_id,
        "data_basis": f"Utility-bill data with billing period starting in calendar year {reporting_year}.",
        "essential_indicators": _build_gri_indicators(
            scope1_t, scope2_t, src, scope1_std, scope2_std,
            intensity=_get_intensity_metrics(db, organization_id, round(scope1_t + scope2_t, 3)),
        ),
        "totals": {
            "scope1_plus_2_tCO2e": round(scope1_t + scope2_t, 3),
            "total_all_scopes": _tracked(
                round(scope1_t + scope2_t, 3), "tCO2e",
                src + " (Scope 1+2 only; Scope 3 not tracked)",
                standard=sorted(set(scope1_std) | set(scope2_std)),
            ),
        },
    }


def _build_gri_indicators(scope1_t, scope2_t, src, scope1_std, scope2_std, intensity=None):
    intensity = intensity or {}
    """GRI 305 core disclosures. Emissions filled, rest not_tracked."""
    return {
        "305_1_direct_ghg": {
            "label": "305-1 Direct (Scope 1) GHG emissions",
            "data": _tracked(scope1_t, "tCO2e", src, standard=scope1_std),
        },
        "305_2_energy_indirect_ghg": {
            "label": "305-2 Energy indirect (Scope 2) GHG emissions, location-based",
            "data": _tracked(scope2_t, "tCO2e", src, standard=scope2_std),
        },
        "305_3_other_indirect_ghg": {
            "label": "305-3 Other indirect (Scope 3) GHG emissions",
            "data": NOT_TRACKED,
        },
        "305_4_ghg_intensity": {
            "label": "305-4 GHG emissions intensity (per revenue)",
            "data": intensity.get("intensity_per_revenue_tco2e", NOT_TRACKED),
            "note": "tCO2e per Rs crore of annual revenue, as set in organization profile.",
        },
        "305_4_ghg_intensity_per_employee": {
            "label": "305-4 GHG emissions intensity (per employee)",
            "data": intensity.get("intensity_per_employee_tco2e", NOT_TRACKED),
            "note": "tCO2e per employee, as set in organization profile.",
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


def generate_esrs_e1(db: Session, organization_id: int,
                     reporting_year: int) -> dict:
    """ESRS E1 (Climate Change) -- CSRD disclosures, emissions-focused subset."""
    scope1_t, scope2_t, src, scope1_std, scope2_std = _get_scope_summary(
        db, organization_id, reporting_year
    )

    return {
        "framework": "ESRS E1",
        "section": "Climate Change (CSRD)",
        "reporting_year": reporting_year,
        "organization_id": organization_id,
        "data_basis": f"Utility-bill data with billing period starting in calendar year {reporting_year}.",
        "essential_indicators": _build_esrs_indicators(
            scope1_t, scope2_t, src, scope1_std, scope2_std,
            intensity=_get_intensity_metrics(db, organization_id, round(scope1_t + scope2_t, 3)),
        ),
        "totals": {
            "scope1_plus_2_tCO2e": round(scope1_t + scope2_t, 3),
            "total_all_scopes": _tracked(
                round(scope1_t + scope2_t, 3), "tCO2e",
                src + " (Scope 1+2 only; Scope 3 not tracked)",
                standard=sorted(set(scope1_std) | set(scope2_std)),
            ),
        },
    }


def _build_esrs_indicators(scope1_t, scope2_t, src, scope1_std, scope2_std, intensity=None):
    intensity = intensity or {}
    """ESRS E1 disclosures. Emissions filled, rest not_tracked."""
    return {
        "E1_4_targets": {
            "label": "E1-4 Targets related to climate change mitigation and adaptation",
            "data": NOT_TRACKED,
            "note": "See the platform's Net Zero Action Plan module for target-vs-actual tracking, not yet mapped into this disclosure.",
        },
        "E1_5_energy_consumption": {
            "label": "E1-5 Energy consumption and mix",
            "renewable_gj": NOT_TRACKED,
            "non_renewable_gj": NOT_TRACKED,
            "note": "Energy in GJ available via SEC engine per unit; org-wide split not yet aggregated here.",
        },
        "E1_6_scope1": {
            "label": "E1-6 Gross Scope 1 GHG emissions",
            "data": _tracked(scope1_t, "tCO2e", src, standard=scope1_std),
        },
        "E1_6_scope2": {
            "label": "E1-6 Gross Scope 2 GHG emissions, location-based",
            "data": _tracked(scope2_t, "tCO2e", src, standard=scope2_std),
        },
        "E1_6_scope3": {
            "label": "E1-6 Gross Scope 3 GHG emissions",
            "data": NOT_TRACKED,
        },
        "E1_6_total": {
            "label": "E1-6 Total GHG emissions (location-based)",
            "data": _tracked(
                round(scope1_t + scope2_t, 3), "tCO2e", src,
                standard=sorted(set(scope1_std) | set(scope2_std)),
            ),
        },
        "E1_6_intensity_per_employee": {
            "label": "E1-6 GHG intensity per employee",
            "data": intensity.get("intensity_per_employee_tco2e", NOT_TRACKED),
            "note": "tCO2e per employee, as set in organization profile.",
        },
        "E1_6_intensity": {
            "label": "E1-6 GHG intensity per net revenue",
            "data": intensity.get("intensity_per_revenue_tco2e", NOT_TRACKED),
            "note": "tCO2e per Rs crore of annual revenue, as set in organization profile.",
        },
        "E1_7_removals": {
            "label": "E1-7 GHG removals and carbon credits",
            "data": NOT_TRACKED,
        },
        "E1_8_carbon_pricing": {
            "label": "E1-8 Internal carbon pricing",
            "data": NOT_TRACKED,
        },
        "E1_9_financial_effects": {
            "label": "E1-9 Anticipated financial effects of climate risks/opportunities",
            "data": NOT_TRACKED,
        },
    }


def generate_trend(db: Session, organization_id: int, years: list[int]) -> dict:
    """Multi-year trend table for Scope 1, Scope 2, and Scope 1+2 emissions."""
    trend_data = []
    for year in sorted(years):
        try:
            scope1_t, scope2_t, src, _scope1_std, _scope2_std = _get_scope_summary(
                db, organization_id, year
            )
            trend_data.append({
                "year": year,
                "scope1_tco2e": scope1_t,
                "scope2_tco2e": scope2_t,
                "scope1_plus_2_tco2e": round(scope1_t + scope2_t, 3),
                "status": "tracked",
            })
        except Exception:
            trend_data.append({
                "year": year,
                "scope1_tco2e": None,
                "scope2_tco2e": None,
                "scope1_plus_2_tco2e": None,
                "status": "no_data",
            })
    return {
        "organization_id": organization_id,
        "years": sorted(years),
        "trend": trend_data,
    }
