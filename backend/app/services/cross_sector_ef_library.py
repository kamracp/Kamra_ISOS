"""
Cross-Sector Emission Factor Library for Kamra ClimateOS.

Source: GHG Protocol Cross-Sector Tools Emission Factors workbook
(Stationary Combustion sheet), reproducing IPCC 2006 Guidelines Vol 2
default Tier 1 factors: CO2/CH4/N2O in kg gas per TJ (energy basis),
plus each fuel Lower Heating Value (LHV) in TJ/Gg (= GJ/tonne).
54 fuels, 5 categories. Official published figures only, never
estimated or LLM-generated (project sourcing rule).

CO2e uses IPCC AR5 GWP-100 (CH4=28, N2O=265). Biomass CO2 is biogenic
and excluded from the fossil compliance total by default.
"""

from typing import Optional

GWP_AR5 = {"ch4": 28, "n2o": 265}


class FuelFactor:
    def __init__(self, key, name, category, lhv_tj_per_gg,
                 co2_kg_per_tj, ch4_kg_per_tj, n2o_kg_per_tj):
        self.key = key
        self.name = name
        self.category = category
        self.lhv_tj_per_gg = lhv_tj_per_gg
        self.co2_kg_per_tj = co2_kg_per_tj
        self.ch4_kg_per_tj = ch4_kg_per_tj
        self.n2o_kg_per_tj = n2o_kg_per_tj

    def to_dict(self):
        return {
            "key": self.key,
            "name": self.name,
            "category": self.category,
            "lhv_tj_per_gg": self.lhv_tj_per_gg,
            "co2_kg_per_tj": self.co2_kg_per_tj,
            "ch4_kg_per_tj": self.ch4_kg_per_tj,
            "n2o_kg_per_tj": self.n2o_kg_per_tj,
        }


FUEL_LIBRARY = {}


def _add(key, name, category, lhv, co2, ch4, n2o):
    FUEL_LIBRARY[key] = FuelFactor(key, name, category, lhv, co2, ch4, n2o)


_add("crude_oil", "Crude oil", "Oil products", 42.3, 73300, 10, 0.6)
_add("orimulsion", "Orimulsion", "Oil products", 27.5, 77000, 10, 0.6)
_add("natural_gas_liquids", "Natural Gas Liquids", "Oil products", 44.2, 64200, 10, 0.6)
_add("motor_gasoline", "Motor gasoline", "Oil products", 44.3, 69300, None, None)
_add("aviation_gasoline", "Aviation gasoline", "Oil products", 44.3, 70000, 10, 0.6)
_add("jet_gasoline", "Jet gasoline", "Oil products", 44.3, 70000, 10, 0.6)
_add("jet_kerosene", "Jet kerosene", "Oil products", 44.1, 71500, 10, 0.6)
_add("other_kerosene", "Other kerosene", "Oil products", 43.8, 71900, 10, 0.6)
_add("shale_oil", "Shale oil", "Oil products", 38.1, 73300, 10, 0.6)
_add("gas_diesel_oil", "Gas/Diesel oil", "Oil products", 43, 74100, None, None)
_add("residual_fuel_oil", "Residual fuel oil", "Oil products", 40.4, 77400, None, None)
_add("liquified_petroleum_gases", "Liquified Petroleum Gases", "Oil products", 47.3, 63100, 5, 0.1)
_add("ethane", "Ethane", "Oil products", 46.4, 61600, 5, 0.1)
_add("naphtha", "Naphtha", "Oil products", 44.5, 73300, 10, 0.6)
_add("bitumen", "Bitumen", "Oil products", 40.2, 80700, 10, 0.6)
_add("lubricants", "Lubricants", "Oil products", 40.2, 73300, 10, 0.6)
_add("petroleum_coke", "Petroleum coke", "Oil products", 32.5, 97500, 10, 0.6)
_add("refinery_feedstocks", "Refinery feedstocks", "Oil products", 43, 73300, 10, 0.6)
_add("refinery_gas", "Refinery gas", "Oil products", 49.5, 57600, 5, 0.1)
_add("paraffin_waxes", "Paraffin waxes", "Oil products", 40.2, 73300, 10, 0.6)
_add("white_spirit_sbp", "White Spirit/SBP", "Oil products", 40.2, 73300, 10, 0.6)
_add("other_petroleum_products", "Other petroleum products", "Oil products", 40.2, 73300, 10, 0.6)
_add("anthracite", "Anthracite", "Coal products", 26.7, 98300, 10, 1.5)
_add("coking_coal", "Coking coal", "Coal products", 28.2, 94600, 10, 1.5)
_add("other_bituminous_coal", "Other bituminous coal", "Coal products", 25.8, 94600, 10, 1.5)
_add("sub_bituminous_coal", "Sub bituminous coal", "Coal products", 18.9, 96100, 10, 1.5)
_add("lignite", "Lignite", "Coal products", 11.9, 101000, 10, 1.5)
_add("oil_shale_and_tar_sands", "Oil shale and tar sands", "Coal products", 8.9, 107000, 10, 1.5)
_add("brown_coal_briquettes", "Brown coal briquettes", "Coal products", 20.7, 97500, 10, 1.5)
_add("patent_fuel", "Patent fuel", "Coal products", 20.7, 97500, 10, 1.5)
_add("coke_oven_coke", "Coke oven coke", "Coal products", 28.2, 107000, 10, 1.5)
_add("lignite_coke", "Lignite coke", "Coal products", 28.2, 107000, 10, 1.5)
_add("gas_coke", "Gas coke", "Coal products", 28.2, 107000, 5, 0.1)
_add("coal_tar", "Coal tar", "Coal products", 28, 80700, 10, 1.5)
_add("gas_works_gas", "Gas works gas", "Coal products", 38.7, 44400, 5, 0.1)
_add("coke_oven_gas", "Coke oven gas", "Coal products", 38.7, 44400, 5, 0.1)
_add("blast_furnace_gas", "Blast furnace gas", "Coal products", 2.47, 260000, 5, 0.1)
_add("oxygen_steel_furnace_gas", "Oxygen steel furnace gas", "Coal products", 7.06, 182000, 5, 0.1)
_add("natural_gas", "Natural gas", "Natural gas", 48, 56100, None, None)
_add("municipal_waste_non_biomass_fraction", "Municipal waste (Non biomass fraction)", "Other wastes", 10, 91700, 300, 4)
_add("industrial_wastes", "Industrial wastes", "Other wastes", None, 143000, 300, 4)
_add("waste_oils", "Waste oils", "Other wastes", 40.2, 73300, 300, 4)
_add("wood_or_wood_waste", "Wood or Wood waste", "Biomass", 15.6, 112000, 300, 4)
_add("sulphite_lyes_black_liquor", "Sulphite lyes (Black liquor)", "Biomass", 11.8, 95300, 3, 2)
_add("other_primary_solid_biomass_fuels", "Other primary solid biomass fuels", "Biomass", 11.6, 100000, 300, 4)
_add("charcoal", "Charcoal", "Biomass", 29.5, 112000, 200, 1)
_add("biogasoline", "Biogasoline", "Biomass", 27, 70800, 10, 0.6)
_add("biodiesels", "Biodiesels", "Biomass", 27, 70800, 10, 0.6)
_add("other_liquid_biofuels", "Other liquid biofuels", "Biomass", 27.4, 79600, 10, 0.6)
_add("landfill_gas", "Landfill gas", "Biomass", 50.4, 54600, 5, 0.1)
_add("sludge_gas", "Sludge gas", "Biomass", 50.4, 54600, 5, 0.1)
_add("other_biogas", "Other biogas", "Biomass", 50.4, 54600, 5, 0.1)
_add("municipal_wastes_biomass_fraction", "Municipal wastes (Biomass fraction)", "Biomass", 11.6, 100000, 300, 4)
_add("peat", "Peat", "Biomass", 9.76, 106000, 10, 1.4)


_BIOGENIC_CATEGORIES = {"Biomass"}


def is_biogenic(fuel_key):
    f = FUEL_LIBRARY.get(fuel_key)
    return bool(f and f.category in _BIOGENIC_CATEGORIES)


def co2e_per_tj(fuel_key, include_biogenic_co2=False):
    """CO2e per TJ = CO2 + CH4*28 + N2O*265 (AR5). Biogenic CO2 excluded by default."""
    f = FUEL_LIBRARY.get(fuel_key)
    if f is None:
        return None
    co2 = f.co2_kg_per_tj
    if is_biogenic(fuel_key) and not include_biogenic_co2:
        co2 = 0.0
    ch4 = (f.ch4_kg_per_tj or 0.0) * GWP_AR5["ch4"]
    n2o = (f.n2o_kg_per_tj or 0.0) * GWP_AR5["n2o"]
    return round(co2 + ch4 + n2o, 2)


def co2e_per_tonne(fuel_key, include_biogenic_co2=False):
    """CO2e per tonne = co2e_per_tj * LHV(TJ/Gg) / 1000."""
    f = FUEL_LIBRARY.get(fuel_key)
    if f is None or f.lhv_tj_per_gg is None:
        return None
    per_tj = co2e_per_tj(fuel_key, include_biogenic_co2)
    if per_tj is None:
        return None
    return round(per_tj * f.lhv_tj_per_gg / 1000.0, 4)


def list_fuels():
    result = []
    for key, f in FUEL_LIBRARY.items():
        d = f.to_dict()
        d["co2e_kg_per_tj"] = co2e_per_tj(key)
        d["co2e_kg_per_tonne"] = co2e_per_tonne(key)
        d["is_biogenic"] = is_biogenic(key)
        result.append(d)
    return result


def get_fuel(fuel_key):
    f = FUEL_LIBRARY.get(fuel_key)
    if f is None:
        return None
    d = f.to_dict()
    d["co2e_kg_per_tj"] = co2e_per_tj(fuel_key)
    d["co2e_kg_per_tonne"] = co2e_per_tonne(fuel_key)
    d["is_biogenic"] = is_biogenic(fuel_key)
    return d
