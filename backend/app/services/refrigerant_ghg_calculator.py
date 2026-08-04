"""
Refrigeration & Air-Conditioning Equipment GHG calculator
(fugitive HFC/PFC emissions, lifecycle-stage approach for equipment users).

Source: GHG Protocol "Refrigeration and Air-Conditioning Equipment"
tool, worksheet "WS 2 - Lifecycle Stage Approach", section "Lifecycle
Stage Approach: Emissions from Users of Air Conditioning and
Refrigeration Equipment". Formula and column structure are stated
directly in the sheet's own header row (columns G, M, N, Q below).

GWP values: Table 1 of the same tool ("GWPs of Common Greenhouse
Gases and Refrigerants"), sourced from ASHRAE Standard 34 (blends)
and the IPCC Second Assessment Report 1995 (pure HFCs/PFCs) -- the
GWP basis the GHG Protocol tool itself specifies. A newer AR5/AR6 GWP
set could be substituted via the optional override parameter if the
platform later needs it, but must never be silently guessed.

IMPORTANT LIMITATION: R-22 and other HCFCs are intentionally absent
from Table 1 and therefore from GWP_TABLE below. HCFCs are controlled
under the Montreal Protocol (ozone-depleting substances), not the
Kyoto Protocol basket of gases (CO2, CH4, N2O, HFCs, PFCs, SF6, NF3),
so the GHG Protocol tool itself excludes them from GHG inventories.
R-22 remains very common in India -- calling this calculator for an
R-22 system will correctly raise an error rather than silently
returning zero or a guessed value; R-22 leakage should be tracked
under refrigerant-management / ozone-depleting-substance reporting,
not GHG inventory reporting.
"""

from dataclasses import dataclass
from decimal import Decimal


# GWP (Global Warming Potential), Table 1 of the source tool.
# Source column noted per entry group.
GWP_TABLE: dict[str, Decimal] = {
    # IPCC Second Assessment Report (1995) -- pure HFCs/PFCs
    "HFC-23": Decimal("11700"),
    "HFC-32": Decimal("650"),
    "HFC-125": Decimal("2800"),
    "HFC-134a": Decimal("1300"),
    "HFC-143a": Decimal("3800"),
    "HFC-152a": Decimal("140"),
    "HFC-236fa": Decimal("6300"),
    "PFC-218 (C3F8)": Decimal("7000"),
    "PFC-116 (C2F6)": Decimal("9200"),
    "PFC-14 (CF4)": Decimal("6500"),
    # ASHRAE Standard 34 -- refrigerant blends
    "R-401A": Decimal("18.2"),
    "R-401B": Decimal("15.4"),
    "R-401C": Decimal("21"),
    "R-402A": Decimal("1680"),
    "R-402B": Decimal("1064"),
    "R-403A": Decimal("1400"),
    "R-403B": Decimal("2730"),
    "R-404A": Decimal("3260"),
    "R-406A": Decimal("0"),
    "R-407A": Decimal("1770"),
    "R-407B": Decimal("2285"),
    "R-407C": Decimal("1525.5"),
    "R-407D": Decimal("1428"),
    "R-407E": Decimal("1363"),
    "R-408A": Decimal("1944"),
    "R-409A": Decimal("0"),
    "R-409B": Decimal("0"),
    "R-410A": Decimal("1725"),
    "R-410B": Decimal("1832.5"),
    "R-411A": Decimal("15.4"),
    "R-411B": Decimal("4.2"),
    "R-412A": Decimal("350"),
    "R-413A": Decimal("1774"),
    "R-414A": Decimal("0"),
    "R-414B": Decimal("0"),
    "R-415A": Decimal("25"),
    "R-415B": Decimal("105"),
    "R-416A": Decimal("767"),
    "R-417A": Decimal("1954.8"),
    "R-418A": Decimal("3.5"),
    "R-419A": Decimal("2403"),
    "R-420A": Decimal("1144"),
    "R-500": Decimal("36.68"),
    "R-501": Decimal("0"),
    "R-502": Decimal("0"),
    "R-503": Decimal("4691.7"),
    "R-504": Decimal("313.3"),
    "R-505": Decimal("0"),
    "R-506": Decimal("0"),
    "R-507 or R-507A": Decimal("3300"),
    "R-508A": Decimal("10175"),
    "R-508B": Decimal("10350"),
    "R-509 or R-509A": Decimal("3920"),
}

KG_TO_TONNES = Decimal("0.001")


@dataclass(frozen=True)
class RefrigerantLifecycleEntry:
    """One refrigerant's lifecycle-stage inputs, all in kilograms.

    Field names and meaning follow the source tool's own columns
    (letters shown in comments) exactly, so a filled-in copy of the
    original worksheet maps directly onto this record.
    """

    refrigerant: str

    fill_new_equipment: Decimal = Decimal("0")           # C
    fill_retrofitted_equipment: Decimal = Decimal("0")   # D
    new_equipment_full_charge: Decimal = Decimal("0")    # E
    retrofit_equipment_full_charge: Decimal = Decimal("0")  # F

    service_amount_net: Decimal = Decimal("0")           # H

    retired_equipment_full_charge: Decimal = Decimal("0")        # I
    retrofitted_away_full_charge: Decimal = Decimal("0")         # J
    recovered_from_retiring: Decimal = Decimal("0")               # K
    recovered_from_retrofitted_away: Decimal = Decimal("0")       # L


@dataclass
class RefrigerantLifecycleResult:
    refrigerant: str
    installation_emissions_kg: Decimal   # G = C + D - E - F
    use_emissions_kg: Decimal            # H
    disposal_emissions_kg: Decimal       # M = I + J - K - L
    total_emissions_kg: Decimal          # N = G + H + M
    gwp: Decimal                          # P
    co2e_tonnes: Decimal                  # Q = N x 0.001 x P


def calculate_refrigerant_lifecycle_co2e(
    entry: RefrigerantLifecycleEntry,
    gwp_override: Decimal | None = None,
) -> RefrigerantLifecycleResult:
    """
    Calculate CO2e emissions from one refrigerant across its full
    lifecycle at the equipment user: installation losses, in-service
    (servicing/top-up) losses, and end-of-life disposal losses.

    gwp_override: supply only if a specific, sourced GWP value
    (e.g. a newer AR6 figure) is required instead of the tool's own
    ASHRAE-34/IPCC-SAR table. Never guess a GWP -- if the refrigerant
    is not in GWP_TABLE and no override is supplied, this raises
    rather than silently defaulting (this is the deliberate behavior
    for HCFCs like R-22, which the GHG Protocol excludes from GHG
    inventories -- see module docstring).
    """

    gwp = gwp_override
    if gwp is None:
        if entry.refrigerant not in GWP_TABLE:
            raise ValueError(
                f"No GWP on file for '{entry.refrigerant}'. If this is "
                "an HCFC (e.g. R-22), it is intentionally excluded from "
                "GHG Protocol inventories (Montreal Protocol substance, "
                "not a Kyoto gas) -- track it separately, don't report "
                "GHG-inventory CO2e for it. Otherwise supply gwp_override "
                "with a real, sourced GWP value."
            )
        gwp = GWP_TABLE[entry.refrigerant]

    installation_emissions = (
        entry.fill_new_equipment
        + entry.fill_retrofitted_equipment
        - entry.new_equipment_full_charge
        - entry.retrofit_equipment_full_charge
    )

    use_emissions = entry.service_amount_net

    disposal_emissions = (
        entry.retired_equipment_full_charge
        + entry.retrofitted_away_full_charge
        - entry.recovered_from_retiring
        - entry.recovered_from_retrofitted_away
    )

    total_emissions_kg = (
        installation_emissions + use_emissions + disposal_emissions
    )

    co2e_tonnes = total_emissions_kg * KG_TO_TONNES * gwp

    return RefrigerantLifecycleResult(
        refrigerant=entry.refrigerant,
        installation_emissions_kg=installation_emissions,
        use_emissions_kg=use_emissions,
        disposal_emissions_kg=disposal_emissions,
        total_emissions_kg=total_emissions_kg,
        gwp=gwp,
        co2e_tonnes=co2e_tonnes,
    )
