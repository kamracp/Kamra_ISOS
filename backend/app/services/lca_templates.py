"""Inventory templates per industry (LCA session 5, step 3).

A template is a CHECKLIST of the inputs a plant in that industry typically has to account for -
name, stage, how the factor is resolved, unit. Quantities are never pre-filled: the user adds each
row with the real figure. Rows whose factor is not yet in the system carry factor_gap=True and are
still worth entering for the mass balance; they stay 'no_factor' in the result (never a proxy).
Composition sources are registered in lca_references.py (ref field).
"""
IN = "IN"

TEMPLATES: dict[str, dict] = {
    "ceramic_tiles": {
        "ref": "epd_confindustria_ceramica_2016",   # sections 2.6 base materials, 2.7 manufacture, 2.10 packaging
        "typical_fu": "m2",
        "items": [
            {"name": "Clay (body)",            "stage": "raw_materials", "factor_source": "factor", "meter_type": None, "unit": "kg", "factor_gap": True,  "note": "no DEFRA factor for clay - enter mass for the balance; factor pending (ICE/ELCD)"},
            {"name": "Feldspar (body)",        "stage": "raw_materials", "factor_source": "factor", "meter_type": None, "unit": "kg", "factor_gap": True,  "note": "factor pending"},
            {"name": "Quartz / sand (body)",   "stage": "raw_materials", "factor_source": "factor", "meter_type": None, "unit": "kg", "factor_gap": True,  "note": "factor pending"},
            {"name": "Glaze frit",             "stage": "raw_materials", "factor_source": "factor", "meter_type": "mat_glass", "unit": "tonne", "factor_gap": False, "note": "DEFRA glass primary production used as proxy for frit"},
            {"name": "Spray-dryer fuel (natural gas)", "stage": "manufacturing", "factor_source": "fuel", "fuel_key": "natural_gas", "unit": "tonne", "factor_gap": False, "note": "or coal / producer gas - pick the fuel actually fired"},
            {"name": "Kiln fuel (coal)",       "stage": "manufacturing", "factor_source": "fuel", "fuel_key": "other_bituminous_coal", "unit": "tonne", "factor_gap": False, "note": "gasifier producer gas: enter the coal fed to the gasifier"},
            {"name": "Kiln fuel (natural gas)","stage": "manufacturing", "factor_source": "fuel", "fuel_key": "natural_gas", "unit": "tonne", "factor_gap": False, "note": "if gas-fired"},
            {"name": "Grid electricity",       "stage": "manufacturing", "factor_source": "electricity", "country_code": IN, "unit": "kWh", "factor_gap": False, "note": "plant meter, annual total"},
            {"name": "Carton (board)",         "stage": "packaging", "factor_source": "factor", "meter_type": "mat_paper_and_board_board", "unit": "tonne", "factor_gap": False, "note": ""},
            {"name": "Stretch film (LDPE)",    "stage": "packaging", "factor_source": "factor", "meter_type": "mat_ldpe_and_lldpe", "unit": "tonne", "factor_gap": False, "note": ""},
            {"name": "Wooden pallet",          "stage": "packaging", "factor_source": "factor", "meter_type": "mat_wood", "unit": "tonne", "factor_gap": False, "note": ""},
        ],
    },
    "cement_clinker": {
        "ref": "ipcc_2006_vol3_ch2_ch4",   # clinker calcination process CO2; raw-mix composition is generic plant practice
        "typical_fu": "tonne",
        "items": [
            {"name": "Limestone",              "stage": "raw_materials", "factor_source": "factor", "meter_type": None, "unit": "kg", "factor_gap": True,  "note": "quarry mass - factor pending; calcination CO2 is the separate process line below"},
            {"name": "Clay / shale",           "stage": "raw_materials", "factor_source": "factor", "meter_type": None, "unit": "kg", "factor_gap": True,  "note": "factor pending"},
            {"name": "Iron ore / laterite",    "stage": "raw_materials", "factor_source": "factor", "meter_type": None, "unit": "kg", "factor_gap": True,  "note": "factor pending"},
            {"name": "Gypsum (cement grinding)","stage": "raw_materials", "factor_source": "factor", "meter_type": None, "unit": "kg", "factor_gap": True,  "note": "factor pending"},
            {"name": "Fly ash / slag (blended cement)", "stage": "raw_materials", "factor_source": "factor", "meter_type": None, "unit": "kg", "factor_gap": True, "note": "secondary material - enter for mass and MCI recycled content"},
            {"name": "Clinker calcination (process CO2)", "stage": "manufacturing", "factor_source": "factor", "meter_type": "clinker_calcination", "unit": "kg", "factor_gap": False, "note": "kg clinker produced; IPCC Tier 1 factor"},
            {"name": "Kiln fuel (coal)",       "stage": "manufacturing", "factor_source": "fuel", "fuel_key": "other_bituminous_coal", "unit": "tonne", "factor_gap": False, "note": ""},
            {"name": "Kiln fuel (petcoke)",    "stage": "manufacturing", "factor_source": "fuel", "fuel_key": "petroleum_coke", "unit": "tonne", "factor_gap": False, "note": ""},
            {"name": "Alternative fuel (biomass)", "stage": "manufacturing", "factor_source": "fuel", "fuel_key": "other_primary_solid_biomass_fuels", "unit": "tonne", "factor_gap": False, "note": "biogenic CO2 reported separately"},
            {"name": "Grid electricity",       "stage": "manufacturing", "factor_source": "electricity", "country_code": IN, "unit": "kWh", "factor_gap": False, "note": "plant meter, annual total"},
            {"name": "Cement sacks (paper)",   "stage": "packaging", "factor_source": "factor", "meter_type": "mat_paper_and_board_paper", "unit": "tonne", "factor_gap": False, "note": ""},
            {"name": "HDPE / PP bags",         "stage": "packaging", "factor_source": "factor", "meter_type": "mat_pp", "unit": "tonne", "factor_gap": False, "note": ""},
        ],
    },
}


def get_template(industry: str) -> dict | None:
    return TEMPLATES.get(industry)
