"""
Aluminium GHG Protocol Sector Tool - Cluster 1: Tier 1 Default CO2.

Source: International Aluminium Institute (IAI) / GHG Protocol Addendum,
"Aluminium Sector Greenhouse Gas Protocol" (October 2006), Worksheet 4 -
Tier 1 default method for CO2 from anode consumption (smelting).

Tier 1 default calculation:
    CO2 emissions (t) = production (t Al) x default factor (t CO2 / t Al)
"""

from enum import Enum


class AluminiumCellTechnology(str, Enum):
    """Smelter cell technology types recognised by the IAI Tier 1 method."""
    PREBAKE = "prebake"
    SODERBERG = "soderberg"


# Tier 1 default CO2 factors, tonnes CO2 per tonne aluminium produced.
# Source: IAI/GHG Protocol Aluminium Addendum (Oct 2006), Worksheet 4.
TIER1_DEFAULT_FACTORS_T_CO2_PER_T_AL = {
    AluminiumCellTechnology.PREBAKE: 1.6,
    AluminiumCellTechnology.SODERBERG: 1.7,
}


def calculate_tier1_default_co2(
    technology: AluminiumCellTechnology,
    aluminium_production_tonnes: float,
) -> dict:
    """Compute Tier 1 default CO2 from aluminium smelting."""
    if aluminium_production_tonnes < 0:
        raise ValueError("aluminium_production_tonnes cannot be negative")

    factor = TIER1_DEFAULT_FACTORS_T_CO2_PER_T_AL[technology]
    co2_tonnes = aluminium_production_tonnes * factor

    return {
        "method": "IAI/GHG Protocol Tier 1 Default CO2 (anode consumption)",
        "source": "IAI Aluminium Sector GHG Protocol Addendum, Oct 2006, Worksheet 4",
        "technology": technology.value,
        "default_factor_t_co2_per_t_al": factor,
        "aluminium_production_tonnes": aluminium_production_tonnes,
        "co2_emissions_tonnes": round(co2_tonnes, 4),
    }
