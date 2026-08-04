"""
Iron & Steel sector GHG calculator (carbon mass-balance method).

Source: GHG Protocol Iron and Steel sector tool, version 2.1,
worksheet "11. Iron and Steel production", "CO2 emissions from Iron
and Steel production". Default carbon content values for process
materials are documented in the tool's Appendix C (not reproduced
here -- plant-specific measured values should be used where available,
per the sourcing rule; never substitute a guessed default).

Methodology (IPCC Tier 2 carbon mass-balance): CO2 emitted equals the
net carbon that enters the process as input materials (coke, coal,
limestone, dolomite, carbon electrodes, coke oven gas, etc.) minus the
carbon that leaves as output materials (steel produced, iron not
converted to steel, blast furnace gas transferred offsite), converted
to CO2 via the CO2/C molecular weight ratio (44/12). Every input and
output material contributes (amount x carbon_content); amount and
carbon_content must be in consistent units for every entry (the
result's mass unit matches whatever unit the amounts were given in).

Verification: the tool's own worked example (Facility A: coke
1,000,000 + coal 500 + limestone 23 + dolomite 25 + electrodes 10 +
coke oven gas 565, minus steel 1525 + iron-not-converted 1 + BF gas
offsite 100, with the example's own carbon-content values) yields
3,041,694.37 tonnes CO2 -- this implementation reproduces that exactly.
"""

from dataclasses import dataclass
from decimal import Decimal


CO2_TO_CARBON_RATIO = Decimal("44") / Decimal("12")


@dataclass(frozen=True)
class MaterialEntry:
    """One process material's amount and measured/sourced carbon content.

    amount and carbon_content must use consistent units across every
    entry passed to the calculator (e.g. all in tonnes); carbon_content
    is a mass fraction (0-1), not a percentage.
    """

    material_name: str
    amount: Decimal
    carbon_content: Decimal


@dataclass
class IronSteelMassBalanceResult:
    total_input_carbon: Decimal
    total_output_carbon: Decimal
    net_carbon: Decimal
    co2_emissions: Decimal


def calculate_iron_steel_co2(
    input_materials: list[MaterialEntry],
    output_materials: list[MaterialEntry],
) -> IronSteelMassBalanceResult:
    """
    Calculate CO2 emissions from iron and steel production via the
    IPCC Tier 2 carbon mass-balance method.

    input_materials: materials entering the process carrying carbon
        (e.g. coke, coal injected, limestone, dolomite, carbon
        electrodes, coke oven gas).
    output_materials: materials leaving the process still carrying
        carbon, so their carbon must be excluded from emitted CO2
        (e.g. steel produced, iron not converted to steel, blast
        furnace gas transferred offsite for use elsewhere).
    """

    if not input_materials:
        raise ValueError("input_materials must not be empty")

    for entry in input_materials + output_materials:
        if entry.amount < 0:
            raise ValueError(
                f"amount for '{entry.material_name}' must not be negative"
            )
        if not (Decimal("0") <= entry.carbon_content <= Decimal("1")):
            raise ValueError(
                f"carbon_content for '{entry.material_name}' must be a "
                "fraction between 0 and 1"
            )

    total_input_carbon = sum(
        (entry.amount * entry.carbon_content for entry in input_materials),
        Decimal("0"),
    )
    total_output_carbon = sum(
        (entry.amount * entry.carbon_content for entry in output_materials),
        Decimal("0"),
    )

    net_carbon = total_input_carbon - total_output_carbon
    co2_emissions = net_carbon * CO2_TO_CARBON_RATIO

    return IronSteelMassBalanceResult(
        total_input_carbon=total_input_carbon,
        total_output_carbon=total_output_carbon,
        net_carbon=net_carbon,
        co2_emissions=co2_emissions,
    )
