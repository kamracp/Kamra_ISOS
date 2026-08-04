"""
CHP (Combined Heat and Power) GHG emissions allocation calculator.

Source: GHG Protocol "CHP Emissions Allocation Tool", version 1.0,
worksheet "CHP Efficiency Methodology_new", "Allocation of GHG
Emissions from a CHP Plant: Efficiency Method". Formula and column
structure are stated directly in the sheet's own header row.

Purpose: a CHP (cogeneration / captive power with waste-heat
recovery) plant produces both steam/heat and electricity from one
fuel input, so its total direct emissions must be split between the
two outputs before they can be attributed to a facility's Scope 1
(own generation) vs. exported/sold energy. This matches BEE PAT
Section IV "Captive Power Generation incl. Waste Heat Recovery" --
relevant to Manufacturing units with their own CHP plant.

Methodology: allocate total emissions in proportion to the fuel each
output would have consumed if produced separately at typical
(reference) efficiencies, not in proportion to raw energy output --
this correctly gives more emissions weight to the less-efficient
output (steam production is typically much more efficient than
power production, so a unit of steam output is allocated fewer
emissions per unit of energy than a unit of electricity output).

Verification: the source sheet's own worked example (total emissions
370.5 t; steam output 3205 [GJ/BTU/kWh] at 0.8 assumed steam
efficiency; power output 245 [same unit] at 0.35 assumed power
efficiency) yields steam emissions 315.39243 t / electricity
emissions 55.10757 t -- this implementation reproduces both exactly.
"""

from dataclasses import dataclass
from decimal import Decimal


REFERENCE_EFFICIENCIES = {
    "US Climate Leaders, EPA": {
        "power_efficiency": Decimal("0.35"),
        "steam_efficiency": Decimal("0.8"),
    },
    "UK Emissions Trading Scheme, DEFRA": {
        "power_efficiency": Decimal("0.33"),
        "steam_efficiency": Decimal("0.66"),
    },
}


@dataclass
class CHPAllocationResult:
    total_emissions: Decimal
    steam_output: Decimal
    power_output: Decimal
    steam_efficiency: Decimal
    power_efficiency: Decimal
    steam_emissions: Decimal
    power_emissions: Decimal
    steam_emission_factor: Decimal
    power_emission_factor: Decimal


def calculate_chp_emissions_allocation(
    total_emissions: Decimal,
    steam_output: Decimal,
    power_output: Decimal,
    steam_efficiency: Decimal,
    power_efficiency: Decimal,
) -> CHPAllocationResult:
    """
    Allocate a CHP plant's total direct GHG emissions between its
    steam/heat output and electricity output using the GHG Protocol
    CHP Efficiency Method.
    """

    if total_emissions < 0:
        raise ValueError("total_emissions must not be negative")

    if steam_output <= 0:
        raise ValueError("steam_output must be greater than zero")

    if power_output <= 0:
        raise ValueError("power_output must be greater than zero")

    if not (Decimal("0") < steam_efficiency <= Decimal("1")):
        raise ValueError("steam_efficiency must be between 0 and 1")

    if not (Decimal("0") < power_efficiency <= Decimal("1")):
        raise ValueError("power_efficiency must be between 0 and 1")

    steam_fuel_equivalent = steam_output / steam_efficiency
    power_fuel_equivalent = power_output / power_efficiency

    steam_emissions = total_emissions * (
        steam_fuel_equivalent
        / (steam_fuel_equivalent + power_fuel_equivalent)
    )

    power_emissions = total_emissions - steam_emissions

    steam_emission_factor = steam_emissions / steam_output
    power_emission_factor = power_emissions / power_output

    return CHPAllocationResult(
        total_emissions=total_emissions,
        steam_output=steam_output,
        power_output=power_output,
        steam_efficiency=steam_efficiency,
        power_efficiency=power_efficiency,
        steam_emissions=steam_emissions,
        power_emissions=power_emissions,
        steam_emission_factor=steam_emission_factor,
        power_emission_factor=power_emission_factor,
    )
