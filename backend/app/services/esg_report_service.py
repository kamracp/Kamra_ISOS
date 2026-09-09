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
from app.repositories.manufacturing_electricity_record_repository import (
    ManufacturingElectricityRecordRepository,
)
from app.repositories.manufacturing_unit_repository import ManufacturingUnitRepository
from app.repositories.manufacturing_fuel_record_repository import ManufacturingFuelRecordRepository
from app.repositories.utility_bill_repository import UtilityBillRepository
from app.services.carbon_service import CarbonService
from app.services.manufacturing_carbon_service import ManufacturingCarbonService
from app.services.water_waste_service import WaterWasteService
from app.services.csr_record_service import CsrRecordService
from app.services.ethics_record_service import EthicsRecordService
from app.services.policy_advocacy_record_service import PolicyAdvocacyRecordService
from app.services.sustainable_product_record_service import SustainableProductRecordService
from app.services.human_rights_record_service import HumanRightsRecordService
from app.services.consumer_responsibility_record_service import ConsumerResponsibilityRecordService
from app.services.employee_wellbeing_record_service import EmployeeWellbeingRecordService
from app.services.energy_service import org_year_energy
from app.services.stakeholder_engagement_record_service import StakeholderEngagementRecordService
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
    - scope2_t = BENAS Scope 2 (bills) + ManufactureOS Scope 2 (purchased
      electricity per manufacturing unit, via ManufacturingElectricityRecord
      + each unit's country grid factor -- see scope2_calculator.py).
      Units with no electricity records, or whose country lacks a
      verified grid factor, contribute nothing to this total (never
      silently zeroed) -- same discipline as ManufacturingCarbonService's
      own total_scope2_co2e_kg.
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
        fuel_record_repository=ManufacturingFuelRecordRepository(db, organization_id=organization_id),
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

    # ManufactureOS Scope 2: rebuild the service with an electricity
    # repository (the earlier instance above was built without one,
    # for the Scope 1 pull) so the summary includes total_scope2_co2e_kg.
    manufacturing_with_electricity = ManufacturingCarbonService(
        emission_record_repository=ManufacturingEmissionRecordRepository(
            db, organization_id=organization_id
        ),
        unit_repository=ManufacturingUnitRepository(db, organization_id=organization_id),
        fuel_record_repository=ManufacturingFuelRecordRepository(db, organization_id=organization_id),
        electricity_record_repository=ManufacturingElectricityRecordRepository(
            db, organization_id=organization_id
        ),
    )
    mfg_summary_with_scope2 = manufacturing_with_electricity.get_summary(year=reporting_year)
    mfg_scope2_kg = mfg_summary_with_scope2.get("total_scope2_co2e_kg")
    if mfg_scope2_kg is not None:
        scope2_t = round(scope2_t + (mfg_scope2_kg / 1000), 3)

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
            energy=org_year_energy(db, organization_id, reporting_year),
            reporting_year=reporting_year,
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


def generate_brsr_principle7(db: Session, organization_id: int,
                             reporting_year: int) -> dict:
    """BRSR Section C, Principle 7 (Public and Regulatory Policy Advocacy) --
    trade/industry association memberships and anti-competitive conduct
    disclosures for one reporting year."""
    policy_service = PolicyAdvocacyRecordService(db, organization_id)
    record = policy_service.get_by_year(reporting_year)
    if record is None:
        essential_indicators = {
            "EI_1_trade_associations": {
                "label": "Trade and industry chamber/association affiliations",
                "data": NOT_TRACKED,
            },
            "EI_2_anti_competitive_conduct": {
                "label": "Anti-competitive conduct corrective actions",
                "data": NOT_TRACKED,
            },
        }
    else:
        src = f"Policy advocacy records for reporting year {reporting_year}."
        essential_indicators = {
            "EI_1_trade_associations": {
                "label": "Trade and industry chamber/association affiliations",
                "data": _tracked(len(record["associations"]), "associations", src)
                if record.get("associations") else NOT_TRACKED,
                "associations": [
                    {
                        "association_name": a["association_name"],
                        "reach": a.get("reach"),
                    }
                    for a in record["associations"]
                ],
            },
            "EI_2_anti_competitive_conduct": {
                "label": "Anti-competitive conduct corrective actions",
                "data": _tracked(
                    "Yes" if record["has_anti_competitive_conduct_issue"] else "No",
                    "yes/no", src,
                ) if record.get("has_anti_competitive_conduct_issue") is not None else NOT_TRACKED,
                "details": record.get("anti_competitive_conduct_details"),
                "corrective_action_taken": record.get("corrective_action_taken"),
            },
        }
    return {
        "framework": "BRSR",
        "section": "Section C, Principle 7 (Public and Regulatory Policy Advocacy)",
        "reporting_year": reporting_year,
        "organization_id": organization_id,
        "data_basis": f"Policy advocacy records for calendar year {reporting_year}.",
        "essential_indicators": essential_indicators,
    }


def generate_brsr_principle4(db: Session, organization_id: int,
                             reporting_year: int) -> dict:
    """BRSR Section C, Principle 4 (Stakeholder Responsiveness) --
    stakeholder group identification and consultation process for one
    reporting year."""
    stakeholder_service = StakeholderEngagementRecordService(db, organization_id)
    record = stakeholder_service.get_by_year(reporting_year)
    if record is None:
        essential_indicators = {
            "EI_1_stakeholder_groups": {
                "label": "Stakeholder groups identified",
                "data": NOT_TRACKED,
            },
            "EI_2_consultation_process": {
                "label": "Consultation on economic, environmental, and social topics",
                "data": NOT_TRACKED,
            },
        }
    else:
        src = f"Stakeholder engagement records for reporting year {reporting_year}."
        essential_indicators = {
            "EI_1_stakeholder_groups": {
                "label": "Stakeholder groups identified",
                "data": _tracked(len(record["stakeholder_groups"]), "groups", src)
                if record.get("stakeholder_groups") else NOT_TRACKED,
                "stakeholder_groups": [
                    {
                        "group_name": g["group_name"],
                        "is_vulnerable_marginalized": g.get("is_vulnerable_marginalized"),
                        "communication_channels": g.get("communication_channels"),
                        "frequency_of_engagement": g.get("frequency_of_engagement"),
                    }
                    for g in record["stakeholder_groups"]
                ],
            },
            "EI_2_consultation_process": {
                "label": "Consultation on economic, environmental, and social topics",
                "data": _tracked(
                    "Yes" if record["has_consultation_process"] else "No",
                    "yes/no", src,
                ) if record.get("has_consultation_process") is not None else NOT_TRACKED,
                "details": record.get("consultation_process_details"),
                "resulted_in_policy_change": record.get("resulted_in_policy_change"),
                "policy_change_details": record.get("policy_change_details"),
            },
        }
    return {
        "framework": "BRSR",
        "section": "Section C, Principle 4 (Stakeholder Responsiveness)",
        "reporting_year": reporting_year,
        "organization_id": organization_id,
        "data_basis": f"Stakeholder engagement records for calendar year {reporting_year}.",
        "essential_indicators": essential_indicators,
    }


def _energy_indicator(label, energy, src_year):
    """EI 1 / E1-5 energy block from energy_service.org_year_energy(); NOT_TRACKED
    when no electricity/fuel record exists for the year."""
    if not energy or energy["record_count"] == 0:
        return {"label": label, "renewable_gj": NOT_TRACKED, "non_renewable_gj": NOT_TRACKED,
                "note": "No electricity or fuel records for this year."}
    src = f"{energy['source']}, reporting year {src_year}."
    return {
        "label": label,
        "renewable_gj": _tracked(energy["renewable_gj"], "GJ", src),
        "non_renewable_gj": _tracked(energy["non_renewable_gj"], "GJ", src),
        "total_gj": _tracked(energy["total_gj"], "GJ", src),
        "total_toe": energy["total_toe"],
        "electricity_kwh": energy["electricity_kwh"],
        "renewable_kwh": energy["renewable_kwh"],
        "thermal_gj": energy["thermal_gj"],
        "biomass_gj": energy["biomass_gj"],
        "by_fuel_gj": energy["by_fuel_gj"],
        "units_with_data": energy["units_with_data"],
    }


def _build_brsr_indicators(scope1_t, scope2_t, src, scope1_std, scope2_std, intensity=None,
                           water_waste=None, energy=None, reporting_year=None):
    intensity = intensity or {}
    water_waste = water_waste or {}
    water = water_waste.get("water", {})
    waste = water_waste.get("waste", {})
    """BRSR Principle 6 Essential Indicators. Emissions filled, rest not_tracked."""
    return {
        "EI_1_energy_consumption": _energy_indicator(
            "Total energy consumption (renewable & non-renewable)", energy, reporting_year),
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
            energy=org_year_energy(db, organization_id, reporting_year),
            reporting_year=reporting_year,
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


def _build_esrs_indicators(scope1_t, scope2_t, src, scope1_std, scope2_std, intensity=None,
                           energy=None, reporting_year=None):
    intensity = intensity or {}
    """ESRS E1 disclosures. Emissions filled, rest not_tracked."""
    return {
        "E1_4_targets": {
            "label": "E1-4 Targets related to climate change mitigation and adaptation",
            "data": NOT_TRACKED,
            "note": "See the platform's Net Zero Action Plan module for target-vs-actual tracking, not yet mapped into this disclosure.",
        },
        "E1_5_energy_consumption": _energy_indicator(
            "E1-5 Energy consumption and mix", energy, reporting_year),
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


def generate_brsr_principle2(db: Session, organization_id: int,
                             reporting_year: int) -> dict:
    """BRSR Section C, Principle 2 (Sustainable and Safe Goods and Services)
    for one reporting year. Every indicator tests `is not None`, never
    truthiness, so a disclosed 0% or an explicit 'No' reports as tracked.
    Reclaimed-material totals come from the service (derived on read),
    never from a stored column."""
    service = SustainableProductRecordService(db, organization_id)
    record = service.get_by_year(reporting_year)
    src = f"Principle 2 sustainable product records for reporting year {reporting_year}."

    def _ind(label, value, unit, **extra):
        # None -> NOT_TRACKED; anything else (including 0 / False) -> tracked.
        if isinstance(value, bool):
            value = "Yes" if value else "No"
        out = {"label": label, "data": _tracked(value, unit, src) if value is not None else NOT_TRACKED}
        out.update({k: v for k, v in extra.items() if v is not None})
        return out

    g = (lambda k: record.get(k)) if record else (lambda k: None)

    essential_indicators = {
        "EI_1a_rnd_percent_current": _ind(
            "R&D on sustainable technologies (% of total, current FY)",
            g("rnd_sustainable_percent_current"), "%"),
        "EI_1b_rnd_percent_previous": _ind(
            "R&D on sustainable technologies (% of total, previous FY)",
            g("rnd_sustainable_percent_previous"), "%"),
        "EI_1c_capex_percent_current": _ind(
            "Capex on sustainable technologies (% of total, current FY)",
            g("capex_sustainable_percent_current"), "%"),
        "EI_1d_capex_percent_previous": _ind(
            "Capex on sustainable technologies (% of total, previous FY)",
            g("capex_sustainable_percent_previous"), "%", details=g("rnd_capex_details")),
        "EI_2a_sustainable_sourcing_procedure": _ind(
            "Procedures in place for sustainable sourcing",
            g("has_sustainable_sourcing_procedure"), "yes/no",
            details=g("sustainable_sourcing_details")),
        "EI_2b_sustainable_sourcing_percent": _ind(
            "Inputs sourced sustainably (% of total)",
            g("sustainable_sourcing_percent"), "%"),
        "EI_3_reclaim_processes": {
            "label": "Processes to safely reclaim products at end of life",
            "data": _tracked(
                sum(1 for k in ("plastics", "e_waste", "hazardous", "other") if g(f"reclaim_process_{k}")),
                "material categories described", src,
            ) if record else NOT_TRACKED,
            "plastics": g("reclaim_process_plastics"),
            "e_waste": g("reclaim_process_e_waste"),
            "hazardous": g("reclaim_process_hazardous"),
            "other": g("reclaim_process_other"),
        },
        "EI_4a_epr_applicable": _ind(
            "Extended Producer Responsibility applicable",
            g("epr_applicable"), "yes/no", details=g("epr_details")),
        "EI_4b_epr_plan_in_line": _ind(
            "Waste collection plan in line with EPR",
            g("epr_plan_in_line"), "yes/no"),
    }

    leadership_indicators = {
        "LI_1_lca_conducted": _ind(
            "Life Cycle Assessment conducted", g("has_conducted_lca"), "yes/no",
            details=g("lca_details")),
        "LI_3_recycled_input_percent": _ind(
            "Recycled or re-used input material (% of total)",
            g("recycled_input_percent"), "%"),
        "LI_4_reclaimed_reused_mt": _ind(
            "Reclaimed products/packaging re-used", g("total_reused_mt"), "MT"),
        "LI_4_reclaimed_recycled_mt": _ind(
            "Reclaimed products/packaging recycled", g("total_recycled_mt"), "MT"),
        "LI_4_reclaimed_disposed_mt": _ind(
            "Reclaimed products/packaging safely disposed", g("total_disposed_mt"), "MT",
            by_category=[
                {"material_category": m["material_category"], "reused_mt": m.get("reused_mt"),
                 "recycled_mt": m.get("recycled_mt"), "disposed_mt": m.get("disposed_mt")}
                for m in (record or {}).get("reclaimed_materials", [])
            ] or None),
        "LI_5_reclaimed_percent_of_products_sold": _ind(
            "Reclaimed products and packaging as % of products sold",
            g("reclaimed_products_percent_details"), "narrative"),
    }

    return {
        "framework": "BRSR",
        "section": "Section C, Principle 2 (Sustainable and Safe Goods and Services)",
        "reporting_year": reporting_year,
        "organization_id": organization_id,
        "data_basis": src,
        "essential_indicators": essential_indicators,
        "leadership_indicators": leadership_indicators,
    }


def generate_brsr_principle5(db: Session, organization_id: int,
                             reporting_year: int) -> dict:
    """BRSR Section C, Principle 5 (Human Rights) for one reporting year.
    Tabular indicators (EI 1-3, EI 6) are reported as the row lists the
    entity entered plus derived aggregates from the service (training
    coverage %, complaint totals); nothing is re-derived here."""
    service = HumanRightsRecordService(db, organization_id)
    record = service.get_by_year(reporting_year)
    src = f"Principle 5 human rights records for reporting year {reporting_year}."

    def _ind(label, value, unit, **extra):
        if isinstance(value, bool):
            value = "Yes" if value else "No"
        out = {"label": label, "data": _tracked(value, unit, src) if value is not None else NOT_TRACKED}
        out.update({k: v for k, v in extra.items() if v is not None})
        return out

    g = (lambda k: record.get(k)) if record else (lambda k: None)
    rows = (lambda k: record.get(k, [])) if record else (lambda k: [])

    def _table(label, key, unit_label):
        items = rows(key)
        return {
            "label": label,
            "data": _tracked(len(items), unit_label, src) if items else NOT_TRACKED,
            "rows": items or None,
        }

    essential_indicators = {
        "EI_1_2_workforce_training_and_wages": _table(
            "Training on human rights and minimum-wage bands, by workforce category",
            "workforce_coverage", "workforce categories disclosed"),
        "EI_3_median_remuneration": _table(
            "Median remuneration/salary/wages by gender",
            "remuneration", "remuneration categories disclosed"),
        "EI_4_focal_point": _ind("Focal point for human rights impacts",
                                 g("has_human_rights_focal_point"), "yes/no", details=g("focal_point_details")),
        "EI_5_grievance_mechanism": _ind("Internal grievance redressal mechanism",
                                         g("grievance_mechanism_details"), "narrative"),
        "EI_6_complaints": {
            **_table("Complaints on human rights issues", "complaints", "complaint categories disclosed"),
            "total_filed": g("total_complaints_filed"),
            "total_pending": g("total_complaints_pending"),
        },
        "EI_7_complainant_protection": _ind("Mechanisms preventing adverse consequences to the complainant",
                                            g("complainant_protection_details"), "narrative"),
        "EI_8_hr_in_contracts": _ind("Human rights requirements in business agreements and contracts",
                                     g("hr_requirements_in_contracts"), "yes/no", details=g("hr_requirements_details")),
        "EI_9_assessments": {
            "label": "Plants and offices assessed (% of total), by topic",
            "data": _tracked(
                sum(1 for k in ("child_labour", "forced_labour", "sexual_harassment", "discrimination", "wages", "other")
                    if g(f"assessed_{k}_percent") is not None),
                "topics disclosed", src) if record else NOT_TRACKED,
            "child_labour_percent": g("assessed_child_labour_percent"),
            "forced_labour_percent": g("assessed_forced_labour_percent"),
            "sexual_harassment_percent": g("assessed_sexual_harassment_percent"),
            "discrimination_percent": g("assessed_discrimination_percent"),
            "wages_percent": g("assessed_wages_percent"),
            "other_percent": g("assessed_other_percent"),
            "other_description": g("assessed_other_description"),
        },
        "EI_10_corrective_actions": _ind("Corrective actions arising from assessments",
                                         g("corrective_actions_from_assessments"), "narrative"),
    }

    leadership_indicators = {
        "LI_1_process_modifications": _ind("Business process modifications from human rights grievances",
                                           g("process_modifications_from_grievances"), "narrative"),
        "LI_2_due_diligence": _ind("Scope and coverage of human rights due diligence",
                                   g("human_rights_due_diligence_details"), "narrative"),
        "LI_3_accessibility": _ind("Premises accessible to differently abled visitors",
                                   g("premises_accessible_to_differently_abled"), "yes/no", details=g("accessibility_details")),
        "LI_4_value_chain_assessed": _ind("Value chain partners assessed (% of total)",
                                          g("value_chain_partners_assessed_percent"), "%",
                                          details=g("value_chain_assessment_details")),
        "LI_5_value_chain_corrective_actions": _ind("Corrective actions from value chain assessments",
                                                    g("value_chain_corrective_actions"), "narrative"),
    }

    return {
        "framework": "BRSR",
        "section": "Section C, Principle 5 (Human Rights)",
        "reporting_year": reporting_year,
        "organization_id": organization_id,
        "data_basis": src,
        "essential_indicators": essential_indicators,
        "leadership_indicators": leadership_indicators,
    }


def generate_brsr_principle9(db: Session, organization_id: int,
                             reporting_year: int) -> dict:
    """BRSR Section C, Principle 9 (Responsible Engagement with Consumers)
    for one reporting year. Complaint rows are the entity's own; totals
    come from the service (derived on read)."""
    service = ConsumerResponsibilityRecordService(db, organization_id)
    record = service.get_by_year(reporting_year)
    src = f"Principle 9 consumer responsibility records for reporting year {reporting_year}."

    def _ind(label, value, unit, **extra):
        if isinstance(value, bool):
            value = "Yes" if value else "No"
        out = {"label": label, "data": _tracked(value, unit, src) if value is not None else NOT_TRACKED}
        out.update({k: v for k, v in extra.items() if v is not None})
        return out

    g = (lambda k: record.get(k)) if record else (lambda k: None)
    complaints = record.get("complaints", []) if record else []

    essential_indicators = {
        "EI_1_complaint_mechanism": _ind("Mechanisms to receive and respond to consumer complaints and feedback",
                                         g("complaint_mechanism_details"), "narrative"),
        "EI_2a_turnover_env_social_info": _ind("Turnover of products/services carrying environmental and social information",
                                               g("turnover_percent_env_social_info"), "% of turnover"),
        "EI_2b_turnover_safe_usage_info": _ind("Turnover of products/services carrying safe and responsible usage information",
                                               g("turnover_percent_safe_usage_info"), "% of turnover"),
        "EI_2c_turnover_recycling_info": _ind("Turnover of products/services carrying recycling / safe disposal information",
                                              g("turnover_percent_recycling_info"), "% of turnover"),
        "EI_3a_voluntary_recalls": _ind("Voluntary product recalls", g("voluntary_recalls_count"), "recalls",
                                        reasons=g("voluntary_recalls_reasons")),
        "EI_3b_forced_recalls": _ind("Forced product recalls", g("forced_recalls_count"), "recalls",
                                     reasons=g("forced_recalls_reasons")),
        "EI_4_cyber_security_policy": _ind("Framework / policy on cyber security and data privacy",
                                           g("has_cyber_security_policy"), "yes/no", web_link=g("cyber_security_policy_link")),
        "EI_5_corrective_actions": _ind("Corrective actions on advertising, delivery, recalls, cyber / data privacy issues",
                                        g("corrective_actions_details"), "narrative"),
        "EI_6_consumer_complaints": {
            "label": "Consumer complaints by category (received / pending)",
            "data": _tracked(len(complaints), "complaint categories disclosed", src) if complaints else NOT_TRACKED,
            "rows": complaints or None,
            "total_received": g("total_complaints_received"),
            "total_pending": g("total_complaints_pending"),
        },
    }

    leadership_indicators = {
        "LI_1_product_information_channels": _ind("Channels where product/service information is available",
                                                  g("product_information_channels"), "narrative"),
        "LI_2_consumer_education": _ind("Steps to inform and educate consumers on safe and responsible usage",
                                        g("consumer_education_details"), "narrative"),
        "LI_3_disruption_disclosure": _ind("Mechanisms to inform consumers of risk of disruption / discontinuation",
                                           g("service_disruption_disclosure_details"), "narrative"),
        "LI_4a_info_beyond_mandate": _ind("Product information displayed beyond what is mandated",
                                          g("displays_product_info_beyond_mandate"), "yes/no"),
        "LI_4b_consumer_survey": _ind("Consumer satisfaction survey conducted", g("consumer_survey_conducted"), "yes/no",
                                      details=g("consumer_survey_details")),
        "LI_5a_data_breaches": _ind("Instances of data breaches", g("data_breaches_count"), "breaches",
                                    impact=g("data_breach_impact_details")),
        "LI_5b_data_breaches_pii": _ind("Data breaches involving personally identifiable information",
                                        g("data_breach_pii_percent"), "% of breaches"),
    }

    return {
        "framework": "BRSR",
        "section": "Section C, Principle 9 (Responsible Engagement with Consumers)",
        "reporting_year": reporting_year,
        "organization_id": organization_id,
        "data_basis": src,
        "essential_indicators": essential_indicators,
        "leadership_indicators": leadership_indicators,
    }


def generate_brsr_principle3(db: Session, organization_id: int,
                             reporting_year: int) -> dict:
    """BRSR Section C, Principle 3 (Employee Well-being) for one reporting
    year. Tabular indicators (EI 1, 6, 8-9, 13) carry the entity's rows with
    the service's derived percentages; scalar indicators use the None ->
    NOT_TRACKED rule (0 and 'No' are tracked)."""
    service = EmployeeWellbeingRecordService(db, organization_id)
    record = service.get_by_year(reporting_year)
    src = f"Principle 3 employee well-being records for reporting year {reporting_year}."

    def _ind(label, value, unit, **extra):
        if isinstance(value, bool):
            value = "Yes" if value else "No"
        out = {"label": label, "data": _tracked(value, unit, src) if value is not None else NOT_TRACKED}
        out.update({k: v for k, v in extra.items() if v is not None})
        return out

    g = (lambda k: record.get(k)) if record else (lambda k: None)

    def _table(label, key, unit_label, **extra):
        items = record.get(key, []) if record else []
        out = {"label": label, "data": _tracked(len(items), unit_label, src) if items else NOT_TRACKED, "rows": items or None}
        out.update({k: v for k, v in extra.items() if v is not None})
        return out

    def _pair(label, emp_key, wkr_key, unit):
        # Employees / workers pairs: tracked if either side is disclosed.
        e, w = g(emp_key), g(wkr_key)
        count = sum(v is not None for v in (e, w))
        return {"label": label, "data": _tracked(count, "of 2 groups disclosed", src) if count else NOT_TRACKED,
                "employees": e, "workers": w, "unit": unit}

    essential_indicators = {
        "EI_1_wellbeing_measures": _table("Well-being measures by workforce category and gender", "wellbeing_measures", "categories disclosed"),
        "EI_2_wellbeing_spend": _ind("Spending on well-being measures", g("wellbeing_spend_percent_revenue"), "% of revenue"),
        "EI_3_retirement_benefits": {
            "label": "Retirement benefits (% covered, deposited with authority)",
            "data": _tracked(sum(1 for b in ("pf", "gratuity", "esi", "other_benefit")
                                 if g(f"{b}_employees_percent") is not None or g(f"{b}_workers_percent") is not None),
                             "benefits disclosed", src) if record else NOT_TRACKED,
            "benefits": [
                {"benefit": b, "employees_percent": g(f"{b}_employees_percent"), "workers_percent": g(f"{b}_workers_percent"),
                 "deposited": g(f"{b}_deposited"), **({"name": g("other_benefit_name")} if b == "other_benefit" else {})}
                for b in ("pf", "gratuity", "esi", "other_benefit")
            ] if record else None,
        },
        "EI_4_accessibility": _ind("Premises accessible to differently abled employees and workers",
                                   g("premises_accessible_to_differently_abled"), "yes/no", details=g("accessibility_details")),
        "EI_5_equal_opportunity_policy": _ind("Equal opportunity policy under the RPwD Act 2016",
                                              g("has_equal_opportunity_policy"), "yes/no", web_link=g("equal_opportunity_policy_link")),
        "EI_6_parental_leave": _table("Return to work and retention rates after parental leave", "parental_leave", "categories disclosed"),
        "EI_7_union_membership": _pair("Permanent employees / workers in associations or unions (%)",
                                       "permanent_employees_union_percent", "permanent_workers_union_percent", "%"),
        "EI_8_9_training_and_reviews": _table("Training (H&S, skill upgradation) and performance reviews", "training", "categories disclosed"),
        "EI_10_ohs_management_system": _ind("Occupational health and safety management system",
                                            g("has_ohs_management_system"), "yes/no", coverage=g("ohs_system_coverage"),
                                            hazard_identification=g("hazard_identification_process"),
                                            non_routine_risk_reporting=g("non_routine_risk_reporting_process"),
                                            medical_facilities=g("has_medical_facilities")),
        "EI_11a_ltifr": _pair("Lost Time Injury Frequency Rate (per one million person-hours)", "ltifr_employees", "ltifr_workers", "LTIFR"),
        "EI_11b_recordable_injuries": _pair("Total recordable work-related injuries", "recordable_injuries_employees", "recordable_injuries_workers", "count"),
        "EI_11c_fatalities": _pair("Fatalities", "fatalities_employees", "fatalities_workers", "count"),
        "EI_11d_high_consequence_injuries": _pair("High-consequence work-related injuries (excluding fatalities)",
                                                  "high_consequence_injuries_employees", "high_consequence_injuries_workers", "count"),
        "EI_12_safe_workplace": _ind("Measures to ensure a safe and healthy workplace", g("safe_workplace_measures"), "narrative"),
        "EI_13_complaints": _table("Complaints on working conditions and health & safety", "complaints", "categories disclosed",
                                   total_filed=g("total_complaints_filed"), total_pending=g("total_complaints_pending")),
        "EI_14_complainant_protection": _ind("Mechanisms preventing adverse consequences to the complainant",
                                             g("complainant_protection_details"), "narrative"),
        "EI_15_assessments": _pair("Plants and offices assessed (% of total): health & safety / working conditions",
                                   "assessed_health_safety_percent", "assessed_working_conditions_percent", "%"),
    }
    # _pair keys read 'employees'/'workers'; EI 15 is health-safety/working-conditions -- relabel.
    ei15 = essential_indicators["EI_15_assessments"]
    ei15["health_safety_percent"], ei15["working_conditions_percent"] = ei15.pop("employees"), ei15.pop("workers")
    ei15["corrective_actions"] = g("corrective_actions_from_assessments")

    leadership_indicators = {
        "LI_1_life_insurance": _pair("Life insurance or compensatory package in the event of death",
                                     "life_insurance_employees", "life_insurance_workers", "yes/no"),
        "LI_2_value_chain_statutory_dues": _ind("Measures ensuring statutory dues are deducted and deposited by value chain partners",
                                                g("value_chain_statutory_dues_details"), "narrative"),
        "LI_3_rehabilitated": _pair("Employees / workers rehabilitated and placed in suitable employment after injury",
                                    "rehabilitated_employees_count", "rehabilitated_workers_count", "count"),
        "LI_4_transition_assistance": _ind("Transition assistance programs on retirement or termination",
                                           g("has_transition_assistance"), "yes/no"),
        "LI_5_value_chain_assessed": _pair("Value chain partners assessed (% of total): health & safety / working conditions",
                                           "value_chain_assessed_health_safety_percent", "value_chain_assessed_working_conditions_percent", "%"),
        "LI_6_value_chain_corrective_actions": _ind("Corrective actions from value chain assessments",
                                                    g("value_chain_corrective_actions"), "narrative"),
    }

    return {
        "framework": "BRSR",
        "section": "Section C, Principle 3 (Employee Well-being)",
        "reporting_year": reporting_year,
        "organization_id": organization_id,
        "data_basis": src,
        "essential_indicators": essential_indicators,
        "leadership_indicators": leadership_indicators,
    }
