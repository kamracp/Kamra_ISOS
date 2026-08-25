"""
ESG Report generation service for Kamra ClimateOS.

Aggregator + formatter, not a new calculator: maps existing platform
data (CarbonService Scope 1/2 from BENAS bills, ManufacturingCarbonService
Scope 1 from ManufactureOS process emissions) into standards report
structures. Frameworks: BRSR Section C Principle 6 (Environment), GRI 305
(Emissions), ESRS E1 (Climate Change / CSRD). Untracked datapoints are
marked "not_tracked", never guessed.
"""

from sqlalchemy.orm import Session

from app.repositories.emission_factor_repository import EmissionFactorRepository
from app.repositories.energy_meter_repository import EnergyMeterRepository
from app.repositories.manufacturing_emission_record_repository import (
    ManufacturingEmissionRecordRepository,
)
from app.repositories.manufacturing_unit_repository import ManufacturingUnitRepository
from app.repositories.utility_bill_repository import UtilityBillRepository
from app.services.carbon_service import CarbonService
from app.services.manufacturing_carbon_service import ManufacturingCarbonService
from app.services.water_waste_service import WaterWasteService
from app.services.csr_record_service import CsrRecordService
from app.services.ethics_record_service import EthicsRecordService
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
    """Shared helper: consolidate CarbonService (BENAS bills, Scope 1+2)
    with ManufacturingCarbonService (ManufactureOS process emissions,
    Scope 1 only -- on-site combustion/process CO2 is always Scope 1
    under GHG Protocol, never Scope 2) for one org/year.

    Returns (scope1_t, scope2_t, src, scope1_standards, scope2_standards).

    - scope1_t = BENAS Scope 1 (bills) + ManufactureOS Scope 1 (process,
      fossil only -- biogenic CO2 is tracked separately and never summed
      into this total, matching GHG Protocol convention).
    - scope2_t = BENAS Scope 2 only. ManufactureOS does not separately
      track purchased electricity for its units yet -- if a manufacturing
      unit's own grid electricity needs to be counted, it should be
      metered via the same energy_meters/utility_bills path BENAS uses
      (a manufacturing unit can share an org with tracked buildings),
      not a separate mechanism.
    - scope1_standards / scope2_standards: sorted list of distinct
      traceability citations. For Scope 1 this now merges BENAS's
      emission_factors.source strings with ManufactureOS's
      calculation_source strings (e.g. "cement_csi_stoichiometric") --
      both are legitimate "what was this computed with" citations, just
      from different calculation paths, and neither is dropped.
    """
    carbon = CarbonService(
        bill_repository=UtilityBillRepository(db, organization_id=organization_id),
        meter_repository=EnergyMeterRepository(db, organization_id=organization_id),
        factor_repository=EmissionFactorRepository(db),
    )
    bills_summary = carbon.get_summary(year=reporting_year)
    by_scope_kg = bills_summary.get("by_scope_kg", {})
    bills_scope1_t = round(by_scope_kg.get("scope_1", 0.0) / 1000, 3)
    scope2_t = round(by_scope_kg.get("scope_2", 0.0) / 1000, 3)

    line_items = bills_summary.get("line_items", [])
    bills_scope1_standards = {
        item["factor_source"]
        for item in line_items
        if item["status"] == "calculated"
        and item["scope"] == "scope_1"
        and item["factor_source"]
    }
    scope2_standards = sorted({
        item["factor_source"]
        for item in line_items
        if item["status"] == "calculated"
        and item["scope"] == "scope_2"
        and item["factor_source"]
    })

    manufacturing = ManufacturingCarbonService(
        emission_record_repository=ManufacturingEmissionRecordRepository(
            db, organization_id=organization_id
        ),
        unit_repository=ManufacturingUnitRepository(db, organization_id=organization_id),
    )
    mfg_summary = manufacturing.get_summary(year=reporting_year)
    mfg_scope1_t = round(mfg_summary.get("total_co2_tonnes", 0.0), 3)
    # calculation_source lives per-record, not on ManufacturingCarbonService's
    # aggregated by_unit summary -- pull it from the raw records directly.
    mfg_records = ManufacturingEmissionRecordRepository(
        db, organization_id=organization_id
    ).get_all(year=reporting_year)
    mfg_scope1_standards = {
        record.calculation_source for record in mfg_records if not record.is_biogenic
    }

    scope1_t = round(bills_scope1_t + mfg_scope1_t, 3)
    scope1_standards = sorted(bills_scope1_standards | mfg_scope1_standards)

    src = (
        f"CarbonService + ManufacturingCarbonService "
        f"(year {reporting_year}, org {organization_id})"
    )

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
        "data_basis": f"Utility-bill + manufacturing process-emission data for calendar year {reporting_year}.",
        "essential_indicators": _build_brsr_indicators(
            scope1_t, scope2_t, src, scope1_std, scope2_std,
            intensity=_get_intensity_metrics(db, organization_id, round(scope1_t + scope2_t, 3)),
            # P6 also covers water and waste, which are metered rather than
            # derived from emission factors - hence a separate service.
            water_waste=WaterWasteService(
                db, organization_id
            ).get_summary(reporting_year),
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


def generate_brsr_principle8(db: Session, organization_id: int,
                             reporting_year: int) -> dict:
    """BRSR Section C, Principle 8 (Transparent & Inclusive Growth) --
    CSR spend and project indicators. Applicability (whether CSR is
    mandated for this org) lives in BrsrOrganizationProfile Section A
    Q22, deliberately not repeated here -- this section reports actual
    spend/projects for whichever year the caller asks for."""
    csr_service = CsrRecordService(db, organization_id)
    record = csr_service.get_by_year(reporting_year)

    if record is None:
        essential_indicators = {
            "EI_2_csr_amount_spent": {
                "label": "Total CSR amount spent (Rs)",
                "data": NOT_TRACKED,
            },
            "EI_2_csr_percent_spent": {
                "label": "CSR amount spent as % of prescribed budget",
                "data": NOT_TRACKED,
            },
            "EI_3_csr_projects": {
                "label": "CSR projects undertaken",
                "data": NOT_TRACKED,
            },
        }
    else:
        src = f"CSR records for reporting year {reporting_year}."
        essential_indicators = {
            "EI_2_csr_amount_spent": {
                "label": "Total CSR amount spent (Rs)",
                "data": _tracked(
                    float(record["csr_amount_spent_inr"]), "INR", src
                ) if record.get("csr_amount_spent_inr") is not None else NOT_TRACKED,
            },
            "EI_2_csr_percent_spent": {
                "label": "CSR amount spent as % of prescribed budget",
                "data": _tracked(
                    record["percent_spent_vs_budget"], "%", src
                ) if record.get("percent_spent_vs_budget") is not None else NOT_TRACKED,
            },
            "EI_3_csr_projects": {
                "label": "CSR projects undertaken",
                "data": _tracked(
                    len(record["projects"]), "projects", src
                ) if record.get("projects") else NOT_TRACKED,
                "projects": [
                    {
                        "project_name": p["project_name"],
                        "activity_category": p.get("activity_category"),
                        "location": p.get("location"),
                        "amount_spent_inr": p.get("amount_spent_inr"),
                        "direct_beneficiaries_count": p.get("direct_beneficiaries_count"),
                    }
                    for p in record["projects"]
                ],
            },
        }

    return {
        "framework": "BRSR",
        "section": "Section C, Principle 8 (Transparent & Inclusive Growth)",
        "reporting_year": reporting_year,
        "organization_id": organization_id,
        "data_basis": f"CSR spend and project records for calendar year {reporting_year}.",
        "essential_indicators": essential_indicators,
    }


def generate_brsr_principle1(db: Session, organization_id: int,
                             reporting_year: int) -> dict:
    """BRSR Section C, Principle 1 (Ethics, Transparency & Accountability) --
    anti-corruption training coverage, disciplinary actions, conflict of
    interest process, and corruption complaints for one reporting year."""
    ethics_service = EthicsRecordService(db, organization_id)
    record = ethics_service.get_by_year(reporting_year)
    if record is None:
        essential_indicators = {
            "EI_1_training_board_kmp": {
                "label": "Anti-corruption training coverage - Board/KMP (%)",
                "data": NOT_TRACKED,
            },
            "EI_1_training_employees": {
                "label": "Anti-corruption training coverage - Employees (%)",
                "data": NOT_TRACKED,
            },
            "EI_1_training_workers": {
                "label": "Anti-corruption training coverage - Workers (%)",
                "data": NOT_TRACKED,
            },
            "EI_2_disciplinary_actions": {
                "label": "Disciplinary actions for corruption/conflict of interest",
                "data": NOT_TRACKED,
            },
            "EI_2_fines_penalties": {
                "label": "Fines/penalties amount (Rs)",
                "data": NOT_TRACKED,
            },
            "EI_3_conflict_of_interest_process": {
                "label": "Process exists to avoid conflict of interest (Board/KMP)",
                "data": NOT_TRACKED,
            },
            "EI_4_corruption_complaints": {
                "label": "Corruption complaints received",
                "data": NOT_TRACKED,
            },
        }
    else:
        src = f"Ethics records for reporting year {reporting_year}."
        disc_vals = [
            record.get("disciplinary_actions_directors"),
            record.get("disciplinary_actions_kmp"),
            record.get("disciplinary_actions_employees"),
            record.get("disciplinary_actions_workers"),
        ]
        total_disciplinary = (
            sum(v for v in disc_vals if v is not None)
            if any(v is not None for v in disc_vals) else None
        )
        essential_indicators = {
            "EI_1_training_board_kmp": {
                "label": "Anti-corruption training coverage - Board/KMP (%)",
                "data": _tracked(record["board_kmp_trained_percent"], "%", src)
                if record.get("board_kmp_trained_percent") is not None else NOT_TRACKED,
            },
            "EI_1_training_employees": {
                "label": "Anti-corruption training coverage - Employees (%)",
                "data": _tracked(record["employees_trained_percent"], "%", src)
                if record.get("employees_trained_percent") is not None else NOT_TRACKED,
            },
            "EI_1_training_workers": {
                "label": "Anti-corruption training coverage - Workers (%)",
                "data": _tracked(record["workers_trained_percent"], "%", src)
                if record.get("workers_trained_percent") is not None else NOT_TRACKED,
            },
            "EI_2_disciplinary_actions": {
                "label": "Disciplinary actions for corruption/conflict of interest",
                "data": _tracked(total_disciplinary, "actions", src)
                if total_disciplinary is not None else NOT_TRACKED,
            },
            "EI_2_fines_penalties": {
                "label": "Fines/penalties amount (Rs)",
                "data": _tracked(float(record["fines_penalties_amount_inr"]), "INR", src)
                if record.get("fines_penalties_amount_inr") is not None else NOT_TRACKED,
            },
            "EI_3_conflict_of_interest_process": {
                "label": "Process exists to avoid conflict of interest (Board/KMP)",
                "data": _tracked(record["has_conflict_of_interest_process"], "yes/no", src)
                if record.get("has_conflict_of_interest_process") is not None else NOT_TRACKED,
            },
            "EI_4_corruption_complaints": {
                "label": "Corruption complaints received",
                "data": _tracked(record["corruption_complaints_received"], "complaints", src)
                if record.get("corruption_complaints_received") is not None else NOT_TRACKED,
            },
        }
    return {
        "framework": "BRSR",
        "section": "Section C, Principle 1 (Ethics, Transparency & Accountability)",
        "reporting_year": reporting_year,
        "organization_id": organization_id,
        "data_basis": f"Ethics/anti-corruption records for calendar year {reporting_year}.",
        "essential_indicators": essential_indicators,
    }


def _build_brsr_indicators(scope1_t, scope2_t, src, scope1_std, scope2_std, intensity=None,
                           water_waste=None):
    intensity = intensity or {}
    water_waste = water_waste or {}
    water = water_waste.get("water", {})
    waste = water_waste.get("waste", {})
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
            "note": "Includes BENAS fuel-combustion bills and ManufactureOS process emissions (fossil only; biogenic CO2 excluded per GHG Protocol convention).",
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
            # Measured quantities, so no `standard` - that field carries
            # emission-factor citations, and water is metered, not derived
            # from a factor. Claiming a standard here would mislead.
            "data": _tracked(
                float(water["total_withdrawal_kl"]), "kL",
                f"Water records for {water.get('record_count', 0)} period(s).",
            ) if water.get("total_withdrawal_kl") is not None else NOT_TRACKED,
        },
        "EI_3_water_discharge": {
            "label": "Water discharge by destination (kL)",
            "data": _tracked(
                float(water["total_discharge_kl"]), "kL",
                f"Water records for {water.get('record_count', 0)} period(s).",
            ) if water.get("total_discharge_kl") is not None else NOT_TRACKED,
        },
        "EI_4_water_consumption": {
            "label": "Total water consumption (kL)",
            "data": _tracked(
                float(water["total_consumption_kl"]), "kL",
                "Withdrawal minus discharge, per SEBI definition.",
            ) if water.get("total_consumption_kl") is not None else NOT_TRACKED,
        },
        "EI_5_air_emissions": {
            "label": "Air emissions NOx / SOx / PM (excl. GHG)",
            "data": NOT_TRACKED,
        },
        "EI_8_waste_generated": {
            "label": "Total waste generated (MT)",
            "data": _tracked(
                float(waste["total_generated_mt"]), "MT",
                f"Waste records for {waste.get('record_count', 0)} period(s).",
            ) if waste.get("total_generated_mt") is not None else NOT_TRACKED,
        },
        "EI_8b_hazardous_waste": {
            "label": "Hazardous waste generated (MT)",
            "data": _tracked(
                float(waste["hazardous_generated_mt"]), "MT",
                "Bio-medical, battery, radioactive and other hazardous categories.",
            ) if waste.get("hazardous_generated_mt") is not None else NOT_TRACKED,
        },
        "EI_9_waste_recovered": {
            "label": "Waste recovered / diverted from disposal (MT)",
            "data": _tracked(
                float(waste["total_recovered_mt"]), "MT",
                "Recycled, re-used and other recovery operations.",
            ) if waste.get("total_recovered_mt") is not None else NOT_TRACKED,
        },
        "EI_9b_waste_disposed": {
            "label": "Waste disposed (MT)",
            "data": _tracked(
                float(waste["total_disposed_mt"]), "MT",
                "Incineration, landfilling and other disposal operations.",
            ) if waste.get("total_disposed_mt") is not None else NOT_TRACKED,
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
        "data_basis": f"Utility-bill + manufacturing process-emission data for calendar year {reporting_year}.",
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
        "data_basis": f"Utility-bill + manufacturing process-emission data for calendar year {reporting_year}.",
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
