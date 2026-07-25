"""Seed the emission factor library with source-verified official values.

BENAS rule: every value below is taken from an official publication
(CEA / DEFRA / IPCC) -- never invented. Run from backend/ with venv:
    python3 seed_factors.py
Safe to re-run: existing (source, source_year, meter_type) rows are skipped.
"""

from datetime import date

import app.main  # noqa: F401  (registers models, ensures tables)
from app.database.session import SessionLocal
from app.repositories.emission_factor_repository import (
    EmissionFactorRepository,
)
from app.schemas.emission_factor import EmissionFactorCreate
from app.services.emission_factor_service import EmissionFactorService

FACTORS = [
    EmissionFactorCreate(
        meter_type="electricity",
        unit="kWh",
        factor_kgco2e_per_unit=0.727,
        energy_content_gj_per_unit=0.0036,
        region="IN",
        source="CEA CO2 Baseline Database for the Indian Power Sector, Version 20.0",
        source_year=2024,
        document_reference=(
            "Weighted average grid emission factor incl. RES, "
            "FY 2023-24 (cea.nic.in, published Dec 2024)"
        ),
        valid_from=date(2024, 4, 1),
        valid_to=date(2025, 10, 31),
        is_active=True,
        notes=(
            "Location-based Scope 2 factor (GHG Protocol). Superseded by "
            "V21.0 from Nov 2025. energy_content_gj_per_unit: physical "
            "constant (1 kWh = 3.6 MJ)."
        ),
    ),
    EmissionFactorCreate(
        meter_type="electricity",
        unit="kWh",
        factor_kgco2e_per_unit=0.7117,
        energy_content_gj_per_unit=0.0036,
        region="IN",
        source="CEA CO2 Baseline Database for the Indian Power Sector, Version 21.0",
        source_year=2025,
        document_reference=(
            "Weighted average grid emission factor incl. RES & captive, "
            "excl. imports, FY 2024-25 (User Guide V21.0, cea.nic.in, "
            "published Nov 2025)"
        ),
        valid_from=date(2025, 11, 1),
        valid_to=None,
        is_active=True,
        notes=(
            "Location-based Scope 2 factor (GHG Protocol). One secondary "
            "source cites 0.710 provisional -- verify against official CEA "
            "Excel before formal disclosure. energy_content_gj_per_unit: "
            "physical constant (1 kWh = 3.6 MJ)."
        ),
    ),
    EmissionFactorCreate(
        meter_type="diesel",
        unit="litres",
        factor_kgco2e_per_unit=2.57082,
        energy_content_gj_per_unit=0.0363,
        region="IN",
        source="UK Government GHG Conversion Factors for Company Reporting 2025 (DEFRA/DESNZ)",
        source_year=2025,
        document_reference="Fuels -- Diesel (average biofuel blend), kgCO2e per litre",
        valid_from=date(2025, 1, 1),
        valid_to=None,
        is_active=True,
        notes=(
            "Scope 1 (DG sets). DEFRA fuel combustion factors are globally "
            "applicable. Average biofuel blend; 100% mineral diesel factor "
            "is slightly higher -- to be verified and added if needed. "
            "energy_content_gj_per_unit: IPCC 2006 NCV 43.0 GJ/tonne x "
            "density 0.845 kg/l, generic default."
        ),
    ),
    EmissionFactorCreate(
        meter_type="coal",
        unit="kg",
        factor_kgco2e_per_unit=2.441,
        energy_content_gj_per_unit=0.0258,
        region="IN",
        source="IPCC 2006 Guidelines for National Greenhouse Gas Inventories",
        source_year=2006,
        document_reference=(
            "Vol 2 Ch 1 Table 1.2 (NCV, Other Bituminous Coal, 25.8 GJ/tonne) "
            "x Vol 2 Ch 2 Table 2.2 (CO2 factor, 94.6 kgCO2/GJ) -- Tier 1 generic default"
        ),
        valid_from=date(2006, 1, 1),
        valid_to=None,
        is_active=True,
        notes=(
            "Scope 1 (Boiler/Furnace). GENERIC DEFAULT -- not calibrated to actual "
            "coal grade/GCV. Refine with plant-specific GCV certificate when known. "
            "CO2-only Tier 1 approximation (CH4/N2O contribution excluded, negligible)."
        ),
    ),
    EmissionFactorCreate(
        meter_type="furnace_oil",
        unit="kg",
        factor_kgco2e_per_unit=3.127,
        energy_content_gj_per_unit=0.0404,
        region="IN",
        source="IPCC 2006 Guidelines for National Greenhouse Gas Inventories",
        source_year=2006,
        document_reference=(
            "Vol 2 Ch 1 Table 1.2 (NCV, Residual Fuel Oil, 40.4 GJ/tonne) "
            "x Vol 2 Ch 2 Table 2.2 (CO2 factor, 77.4 kgCO2/GJ) -- Tier 1 generic default"
        ),
        valid_from=date(2006, 1, 1),
        valid_to=None,
        is_active=True,
        notes="Scope 1 (Boiler/Furnace). Generic default, CO2-only Tier 1 approximation.",
    ),
    EmissionFactorCreate(
        meter_type="biomass",
        unit="kg",
        factor_kgco2e_per_unit=1.747,
        energy_content_gj_per_unit=0.0156,
        region="IN",
        source="IPCC 2006 Guidelines for National Greenhouse Gas Inventories",
        source_year=2006,
        document_reference=(
            "Vol 2 Ch 1 Table 1.2 (NCV, Wood/Wood Waste, 15.6 GJ/tonne) "
            "x Vol 2 Ch 2 Table 2.2 (CO2 factor, 112 kgCO2/GJ) -- Tier 1 generic default"
        ),
        valid_from=date(2006, 1, 1),
        valid_to=None,
        is_active=True,
        notes=(
            "KNOWN LIMITATION -- biogenic CO2: per GHG Protocol, biomass combustion "
            "CO2 is conventionally biogenic and reported separately from the fossil "
            "Scope 1 total (only its CH4/N2O counts toward compliance total). This "
            "factor currently feeds into scope_1 like a fossil fuel pending a proper "
            "biogenic-accounting fix (planned for Phase 9 / BRSR-CSRD hardening)."
        ),
    ),
    EmissionFactorCreate(
        meter_type="natural_gas",
        unit="SCM",
        factor_kgco2e_per_unit=2.041,
        energy_content_gj_per_unit=0.0364,
        region="IN",
        source="IPCC 2006 Guidelines for National Greenhouse Gas Inventories",
        source_year=2006,
        document_reference=(
            "Vol 2 Ch 1 Table 1.2 (NCV, Natural Gas, ~36.4 MJ/SCM typical) "
            "x Vol 2 Ch 2 Table 2.2 (CO2 factor, 56.1 kgCO2/GJ) -- Tier 1 generic default"
        ),
        valid_from=date(2006, 1, 1),
        valid_to=None,
        is_active=True,
        notes=(
            "Scope 1 (Boiler/Furnace/heating). GENERIC DEFAULT -- refine with actual "
            "gas supplier's calorific value certificate when known."
        ),
    ),
    EmissionFactorCreate(
        meter_type="lpg",
        unit="kg",
        factor_kgco2e_per_unit=2.985,
        energy_content_gj_per_unit=0.0473,
        region="IN",
        source="IPCC 2006 Guidelines for National Greenhouse Gas Inventories",
        source_year=2006,
        document_reference=(
            "Vol 2 Ch 1 Table 1.2 (NCV, LPG, 47.3 GJ/tonne) "
            "x Vol 2 Ch 2 Table 2.2 (CO2 factor, 63.1 kgCO2/GJ) -- Tier 1 generic default"
        ),
        valid_from=date(2006, 1, 1),
        valid_to=None,
        is_active=True,
        notes="Scope 1 (Boiler/Furnace/DG). Generic default, CO2-only Tier 1 approximation.",
    ),
    EmissionFactorCreate(
        meter_type="petroleum_coke",
        unit="kg",
        factor_kgco2e_per_unit=3.183,
        energy_content_gj_per_unit=0.0325,
        region="IN",
        source="IPCC 2006 Guidelines Vol 2 (GHG Protocol Cross-Sector Tools EF workbook)",
        source_year=2006,
        document_reference="Stationary Combustion: Petroleum coke, CO2/CH4/N2O combined via AR5 GWP",
        valid_from=date(2006, 1, 1),
        valid_to=None,
        is_active=True,
        notes="Scope 1 process/combustion fuel (Cement, Refineries). CO2e incl. CH4/N2O (AR5). Tier 1 default.",
    ),
    EmissionFactorCreate(
        meter_type="coke_oven_coke",
        unit="kg",
        factor_kgco2e_per_unit=3.0365,
        energy_content_gj_per_unit=0.0282,
        region="IN",
        source="IPCC 2006 Guidelines Vol 2 (GHG Protocol Cross-Sector Tools EF workbook)",
        source_year=2006,
        document_reference="Stationary Combustion: Coke oven coke, CO2/CH4/N2O combined via AR5 GWP",
        valid_from=date(2006, 1, 1),
        valid_to=None,
        is_active=True,
        notes="Scope 1 fuel (Iron & Steel). CO2e incl. CH4/N2O (AR5). Tier 1 default.",
    ),
    EmissionFactorCreate(
        meter_type="blast_furnace_gas",
        unit="kg",
        factor_kgco2e_per_unit=0.6426,
        energy_content_gj_per_unit=0.00247,
        region="IN",
        source="IPCC 2006 Guidelines Vol 2 (GHG Protocol Cross-Sector Tools EF workbook)",
        source_year=2006,
        document_reference="Stationary Combustion: Blast furnace gas, CO2/CH4/N2O combined via AR5 GWP",
        valid_from=date(2006, 1, 1),
        valid_to=None,
        is_active=True,
        notes="Scope 1 byproduct gas fuel (Iron & Steel). Per-kg basis; per-SCM basis may be added later. CO2e incl. CH4/N2O (AR5).",
    ),
    EmissionFactorCreate(
        meter_type="anthracite",
        unit="kg",
        factor_kgco2e_per_unit=2.6427,
        energy_content_gj_per_unit=0.0267,
        region="IN",
        source="IPCC 2006 Guidelines Vol 2 (GHG Protocol Cross-Sector Tools EF workbook)",
        source_year=2006,
        document_reference="Stationary Combustion: Anthracite, CO2/CH4/N2O combined via AR5 GWP",
        valid_from=date(2006, 1, 1),
        valid_to=None,
        is_active=True,
        notes="Scope 1 fuel (Iron & Steel, high-grade coal). CO2e incl. CH4/N2O (AR5). Tier 1 default.",
    ),
    EmissionFactorCreate(
        meter_type="naphtha",
        unit="kg",
        factor_kgco2e_per_unit=3.2814,
        energy_content_gj_per_unit=0.0445,
        region="IN",
        source="IPCC 2006 Guidelines Vol 2 (GHG Protocol Cross-Sector Tools EF workbook)",
        source_year=2006,
        document_reference="Stationary Combustion: Naphtha, CO2/CH4/N2O combined via AR5 GWP",
        valid_from=date(2006, 1, 1),
        valid_to=None,
        is_active=True,
        notes="Scope 1 fuel (Fertilizer, Petrochemicals). CO2e incl. CH4/N2O (AR5). Tier 1 default.",
    ),
    EmissionFactorCreate(
        meter_type="sulphite_lyes_black_liquor",
        unit="kg",
        factor_kgco2e_per_unit=0.0072,
        energy_content_gj_per_unit=0.0118,
        region="IN",
        source="IPCC 2006 Guidelines Vol 2 (GHG Protocol Cross-Sector Tools EF workbook)",
        source_year=2006,
        document_reference="Stationary Combustion: Sulphite lyes (Black liquor), biogenic",
        valid_from=date(2006, 1, 1),
        valid_to=None,
        is_active=True,
        notes="Scope 1 fuel (Pulp & Paper). BIOGENIC: CO2 excluded from fossil compliance total per GHG Protocol; factor is CH4/N2O only (AR5). Report biogenic CO2 separately.",
    ),
]


def main() -> None:
    db = SessionLocal()
    try:
        repository = EmissionFactorRepository(db)
        service = EmissionFactorService(repository)

        for factor in FACTORS:
            existing = [
                f
                for f in repository.get_all(
                    meter_type=factor.meter_type,
                    region=factor.region,
                    include_inactive=True,
                )
                if f.source == factor.source
                and f.source_year == factor.source_year
            ]

            if existing:
                print(f"SKIP  (already seeded): {factor.source}")
                continue

            created = service.create_factor(factor)
            print(
                f"SEEDED id={created.id}: {created.meter_type}/"
                f"{created.unit} = {created.factor_kgco2e_per_unit} "
                f"kgCO2e/unit [{created.source}]"
            )

        print()
        print("TEST: electricity / kWh / IN on 2026-06-15 ->")
        picked = service.get_applicable_factor(
            meter_type="electricity",
            unit="kWh",
            on_date=date(2026, 6, 15),
        )
        print(
            f"PICKED id={picked.id}: {picked.factor_kgco2e_per_unit} "
            f"kgCO2e/kWh from [{picked.source}] "
            f"(valid {picked.valid_from} -> {picked.valid_to or 'open'})"
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
