"""Reference register for the LCA / PCF Studio (ISO 14044 clause 5 reporting; Section 7 'References').

Every standard, method, factor database, EPD, paper and tool convention the LCA tool relies on is
listed here ONCE, with a stable id. Benchmarks, presets, factor seeds and the PLCA report cite these
ids -- a number that cannot point at an entry here does not belong in the tool.

type: standard | method | factor_database | epd | journal | tool_convention
used_for: methodology | emission_factor | benchmark | distribution_preset | mci | grid_factor | td_loss
Only URLs/DOIs confirmed from the document itself are recorded; unknown -> "".
"""

REFERENCES: dict[str, dict] = {
    # ---------------------------------------------------------------- standards
    "iso_14040_2006": {"type": "standard", "used_for": ["methodology"],
        "citation": "ISO 14040:2006 Environmental management - Life cycle assessment - Principles and framework. International Organization for Standardization, Geneva.", "url": ""},
    "iso_14044_2006": {"type": "standard", "used_for": ["methodology"],
        "citation": "ISO 14044:2006 Environmental management - Life cycle assessment - Requirements and guidelines. International Organization for Standardization, Geneva. Clause 5.2: third-party report.", "url": ""},
    "iso_14067_2018": {"type": "standard", "used_for": ["methodology"],
        "citation": "ISO 14067:2018 Greenhouse gases - Carbon footprint of products - Requirements and guidelines for quantification. ISO, Geneva.", "url": ""},
    "iso_14025_2006": {"type": "standard", "used_for": ["methodology", "benchmark"],
        "citation": "ISO 14025:2006 Environmental labels and declarations - Type III environmental declarations - Principles and procedures. ISO, Geneva.", "url": ""},
    "en_15804_a2_2019": {"type": "standard", "used_for": ["methodology"],
        "citation": "EN 15804:2012+A2:2019 Sustainability of construction works - Environmental product declarations - Core rules for the product category of construction products. CEN, Brussels. Modules A1-A3 = cradle-to-gate.", "url": ""},
    "ghgp_product_2011": {"type": "standard", "used_for": ["methodology"],
        "citation": "WRI/WBCSD (2011) Greenhouse Gas Protocol - Product Life Cycle Accounting and Reporting Standard.", "url": ""},
    "pcr_ceramic_tiles_ibu_2014": {"type": "standard", "used_for": ["methodology"],
        "citation": "IBU PCR Part B (2014-07-04, V1.6): Requirements on the EPD for Ceramic tiles and panels. Institut Bauen und Umwelt e.V., Berlin.", "url": ""},
    # ------------------------------------------------------------------ methods
    "emf_mci_v1_1_2019": {"type": "method", "used_for": ["mci"],
        "citation": "Ellen MacArthur Foundation & Granta Design (2019) Circularity Indicators - An Approach to Measuring Circularity. Methodology v1.1. Material Circularity Indicator (MCI), product level.", "url": ""},
    "ipcc_ar5_gwp100": {"type": "method", "used_for": ["emission_factor"],
        "citation": "IPCC (2013) Fifth Assessment Report, WG I, Chapter 8, Table 8.A.1 - GWP-100 (CH4 = 28, N2O = 265) used to express CO2e.", "url": ""},
    # ---------------------------------------------------------- factor databases
    "defra_2026_flat_v1_2": {"type": "factor_database", "used_for": ["emission_factor", "distribution_preset"],
        "citation": "UK Government (DESNZ/DEFRA) GHG Conversion Factors for Company Reporting 2026, flat file v1.2 (revised 31 Jul 2026). Materials, freight, passenger, WTT fuels, WTT bioenergy, waste.", "url": ""},
    "defra_2025_flat": {"type": "factor_database", "used_for": ["emission_factor"],
        "citation": "UK Government (DESNZ/DEFRA) GHG Conversion Factors for Company Reporting 2025 - Fuels (diesel, average biofuel blend, kgCO2e per litre).", "url": ""},
    "ipcc_2006_vol2_ch2": {"type": "factor_database", "used_for": ["emission_factor"],
        "citation": "IPCC (2006) Guidelines for National Greenhouse Gas Inventories, Vol. 2 Energy, Ch. 2 Stationary Combustion, Tables 2.2-2.5 (default EF per TJ, NCV) - as reproduced in the GHG Protocol Cross-Sector Tools emission-factor workbook.", "url": ""},
    "ipcc_2006_vol3_ch2_ch4": {"type": "factor_database", "used_for": ["emission_factor"],
        "citation": "IPCC (2006) Guidelines, Vol. 3 Industrial Processes, Ch. 2 Mineral Industry (clinker calcination, Tier 1) and Ch. 4 Metal Industry (aluminium carbon anode, Tier 1).", "url": ""},
    "cea_co2_baseline_v21_2025": {"type": "factor_database", "used_for": ["grid_factor"],
        "citation": "Central Electricity Authority, Government of India (2025) CO2 Baseline Database for the Indian Power Sector, Version 21.0 - weighted average grid emission factor incl. RES.", "url": ""},
    "cea_co2_baseline_v20_2024": {"type": "factor_database", "used_for": ["grid_factor"],
        "citation": "Central Electricity Authority, Government of India (2024) CO2 Baseline Database for the Indian Power Sector, Version 20.0 (FY 2023-24 weighted average, valid for 2024 records).", "url": ""},
    "cea_general_review_2025": {"type": "factor_database", "used_for": ["td_loss"],
        "citation": "Central Electricity Authority (2025) All India Electricity Statistics - General Review 2025: transmission and distribution losses 17.63% of electricity available, FY 2023-24.", "url": ""},
    # --------------------------------------------------------------------- EPDs
    "epd_confindustria_ceramica_2016": {"type": "epd", "used_for": ["benchmark", "distribution_preset"],
        "citation": "Confindustria Ceramica / Institut Bauen und Umwelt e.V. (2016) Environmental Product Declaration - Italian Ceramic Tiles, EPD-COI-20160202-ICG1-EN, issued 26 Sep 2016, valid to 25 Sep 2021. Declared unit 1 m2 (19.9 kg); GWP A1-A3 = 10.5 kg CO2-eq; 76 companies / 84 plants, 2014 data, GaBi 7.", "url": ""},
    "epd_pca_portland_2021": {"type": "epd", "used_for": ["benchmark"],
        "citation": "Portland Cement Association (2021) Environmental Product Declaration - Portland Cement (ASTM C150), US industry average, Type III EPD verified by ASTM International, valid 2021-2026; LCA by Athena Sustainable Materials Institute with the GCCA Industry EPD Tool (North American module). Declared unit 1 metric ton; GWP-100 (IPCC 2013) A1-A3 = 922 kg CO2-eq; 91.4% clinker; calcination 480 kg CO2-eq.", "url": "https://www.heidelbergmaterials.us/docs/default-source/epds/627-epd_for_pca_portland_athena_03262021_final_revised.pdf"},
    "epd_pca_plc_2021": {"type": "epd", "used_for": ["benchmark"],
        "citation": "Portland Cement Association (2021, revised Nov 2023) Environmental Product Declaration - Portland-Limestone Cement (ASTM C595 Type IL), US industry average, Type III EPD verified by ASTM International, valid 2021-2026; Athena / GCCA EPD Tool. Declared unit 1 metric ton; GWP-100 (IPCC 2013) A1-A3 = 846 kg CO2-eq; 82.7% clinker; calcination 434 kg CO2-eq.", "url": "https://www.cement.org/wp-content/uploads/2024/07/pca_epd_plc_athena_final_revised_nov2023.pdf"},
    # ------------------------------------------------------------ journal papers
    "ibanez_fores_2011": {"type": "journal", "used_for": ["benchmark", "distribution_preset"],
        "citation": "Ibanez-Fores V., Bovea M.D., Simo A. (2011) Life cycle assessment of ceramic tiles. Environmental and statistical analysis. Int J Life Cycle Assess 16:916-928.", "url": "https://doi.org/10.1007/s11367-011-0322-6"},
    "pini_2014": {"type": "journal", "used_for": ["benchmark", "distribution_preset"],
        "citation": "Pini M., Ferrari A.M., Gamberini R., Neri P., Rimini B. (2014) Life cycle assessment of a large, thin ceramic tile with advantageous technological properties. Int J Life Cycle Assess 19:1567-1580.", "url": "https://doi.org/10.1007/s11367-014-0764-8"},
    "ferrari_2019": {"type": "journal", "used_for": ["benchmark", "distribution_preset"],
        "citation": "Ferrari A.M., Volpi L., Pini M., Siligardi C., Garcia-Muina F.E., Settembre-Blundo D. (2019) Building a Sustainability Benchmarking Framework of Ceramic Tiles Based on Life Cycle Sustainability Assessment (LCSA). Resources 8:11.", "url": "https://doi.org/10.3390/resources8010011"},
    # ---------------------------------------------------------- tool conventions
    "kes_conv_plausibility_band": {"type": "tool_convention", "used_for": ["benchmark"],
        "citation": "Kamra ClimateOS convention: a product GWP outside 0.5x-2x of the selected published benchmark raises a plausibility WARNING; the warning never alters the computed result. Band chosen by KES as an order-of-magnitude data-entry check, not a published threshold.", "url": ""},
    "kes_conv_td_loss_applied": {"type": "tool_convention", "used_for": ["td_loss"],
        "citation": "Kamra ClimateOS convention: published T&D loss L (fraction of electricity available) is applied as L/(1-L) kWh lost per kWh delivered before multiplying by the grid factor.", "url": ""},
    "kes_conv_mci_inputs": {"type": "tool_convention", "used_for": ["mci"],
        "citation": "Kamra ClimateOS convention (EMF MCI): product mass = raw_materials items with a mass unit, fuels excluded; Fr/Fu/Cr/Cu must be stated (no defaults); utility X = L/Lav, or X = 1 with an explicit note when no lifetime is given.", "url": ""},
    "kes_conv_factor_resolution": {"type": "tool_convention", "used_for": ["emission_factor"],
        "citation": "Kamra ClimateOS convention: factors are resolved at read time from the cited databases (never stored per product); an item whose unit differs from its factor's unit is reported 'unit mismatch' and excluded from the total.", "url": ""},
}


def list_references(used_for: str | None = None) -> list[dict]:
    out = []
    for k, v in REFERENCES.items():
        if used_for and used_for not in v["used_for"]:
            continue
        out.append({"id": k, **v})
    return out


def ref(ref_id: str) -> dict:
    """Strict lookup: a missing id is a programming error, never a silent blank citation."""
    return {"id": ref_id, **REFERENCES[ref_id]}
