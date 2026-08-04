"""
Pulp & Paper sector GHG calculator (biomass combustion CO2).

Sources:
- GHG Protocol / NCASI Pulp and Paper Sector Tool, version 1.4.0,
  worksheet "Biomass Combustion CO2", Part I (wood/bark) and Part II
  (spent pulping liquors) -- energy-basis (kg CO2/GJ LHV) factors and
  the calculation formula/worked examples.
- GHG Protocol Emission Factors for Cross-Sector Tools, version 2.0.0,
  worksheet "Stationary Combustion", Table 1 (CO2 Emission Factors by
  Fuel) -- adds the mass-basis factors (kg CO2/tonne) and confirms the
  energy-basis factors and net calorific values (GJ/tonne) for the
  same three biomass fuel entries. Both sources agree exactly on the
  energy-basis factors (112 and 95.3 kg CO2/GJ), and both trace to the
  2006 IPCC Guidelines for National Greenhouse Gas Inventories,
  Volume 2 Energy, Chapter 1, Table 1.4.

Biomass-derived CO2 is biogenic per the GHG Protocol convention: it is
reported as additional information, not included in fossil GHG
emission totals. This mirrors how sulphite_lyes_black_liquor is
already handled in the platform's Cross-Sector emission factor
library (is_biogenic=True, CO2 excluded from fossil totals).
"""

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class BiomassFuelType(str, Enum):
    """Biomass fuel types covered by the Pulp & Paper sector tool."""

    WOOD_BARK = "wood_bark"
    BLACK_LIQUOR = "black_liquor"
    OTHER_SOLID_BIOMASS = "other_solid_biomass"


class QuantityBasis(str, Enum):
    """Which physical basis the input quantity is measured on."""

    ENERGY_GJ_LHV = "energy_gj_lhv"
    MASS_TONNES = "mass_tonnes"


NET_CALORIFIC_VALUE_GJ_PER_TONNE: dict[BiomassFuelType, Decimal] = {
    BiomassFuelType.WOOD_BARK: Decimal("15.6"),
    BiomassFuelType.BLACK_LIQUOR: Decimal("11.8"),
    BiomassFuelType.OTHER_SOLID_BIOMASS: Decimal("11.6"),
}

DEFAULT_CO2_FACTORS_KG_PER_GJ_LHV: dict[BiomassFuelType, Decimal] = {
    BiomassFuelType.WOOD_BARK: Decimal("112"),
    BiomassFuelType.BLACK_LIQUOR: Decimal("95.3"),
    BiomassFuelType.OTHER_SOLID_BIOMASS: Decimal("100"),
}

DEFAULT_CO2_FACTORS_KG_PER_TONNE: dict[BiomassFuelType, Decimal] = {
    BiomassFuelType.WOOD_BARK: Decimal("1747.2"),
    BiomassFuelType.BLACK_LIQUOR: Decimal("1124.54"),
    BiomassFuelType.OTHER_SOLID_BIOMASS: Decimal("1160"),
}


@dataclass
class BiomassCO2Result:
    fuel_type: BiomassFuelType
    quantity_basis: QuantityBasis
    quantity: Decimal
    emission_factor: Decimal
    emission_factor_unit: str
    co2_kg_per_year: Decimal
    co2_tonnes_per_year: Decimal
    is_biogenic: bool = True
    note: str = (
        "Biogenic CO2 per GHG Protocol convention: reported as "
        "additional information, not included in fossil GHG totals."
    )


def calculate_biomass_co2(
    fuel_type: BiomassFuelType,
    quantity: Decimal,
    quantity_basis: QuantityBasis = QuantityBasis.MASS_TONNES,
    emission_factor: Decimal | None = None,
) -> BiomassCO2Result:
    """Calculate biogenic CO2 from combustion of a biomass fuel."""

    if not isinstance(fuel_type, BiomassFuelType):
        raise TypeError("fuel_type must be a BiomassFuelType")

    if not isinstance(quantity_basis, QuantityBasis):
        raise TypeError("quantity_basis must be a QuantityBasis")

    if quantity < 0:
        raise ValueError("quantity must not be negative")

    if quantity_basis is QuantityBasis.MASS_TONNES:
        factor = emission_factor
        if factor is None:
            factor = DEFAULT_CO2_FACTORS_KG_PER_TONNE[fuel_type]
        factor_unit = "kg CO2/tonne"
    else:
        factor = emission_factor
        if factor is None:
            factor = DEFAULT_CO2_FACTORS_KG_PER_GJ_LHV[fuel_type]
        factor_unit = "kg CO2/GJ LHV"

    if factor < 0:
        raise ValueError("emission_factor must not be negative")

    co2_kg = quantity * factor
    co2_tonnes = co2_kg / Decimal("1000")

    return BiomassCO2Result(
        fuel_type=fuel_type,
        quantity_basis=quantity_basis,
        quantity=quantity,
        emission_factor=factor,
        emission_factor_unit=factor_unit,
        co2_kg_per_year=co2_kg,
        co2_tonnes_per_year=co2_tonnes,
    )
