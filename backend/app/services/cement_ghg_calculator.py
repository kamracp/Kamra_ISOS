"""
Cement sector GHG calculator (clinker calcination CO2).

Source: WBCSD Cement Sustainability Initiative (CSI), CO2 Emissions
Inventory Protocol, Version 2.0, worksheet "Calcination CO2".

Stoichiometric methodology: CO2 emitted from calcination is derived
from the CaO and MgO content actually measured in the clinker, not
from a flat per-tonne assumption. This supersedes the platform's
earlier simple estimate (0.52 kg CO2/kg clinker, assuming 65% CaO,
uncorrected) with the real CSI stoichiometric method -- the two are
consistent (see verification below) but this one is auditable back to
each clinker type's actual measured composition, and supports the
non-carbonate correction the flat estimate could not.

Molecular weights (g/mol), from the source worksheet:
    CaCO3 = 100.1, MgCO3 = 84.3, CaO = 56.1, MgO = 40.3, CO2 = 44.0

CaCO3 -> CaO + CO2, so CO2 released per unit of CaO = 44.0 / 56.1
MgCO3 -> MgO + CO2, so CO2 released per unit of MgO = 44.0 / 40.3

Verification: for a clinker with 65% CaO and 1% MgO content (a
representative composition) and no non-carbonate correction, this
method yields 520.72 kg CO2/tonne clinker -- matching the platform's
prior flat 520 kg/tonne (0.52 kg/kg) estimate to within 0.15%.
"""

from dataclasses import dataclass
from decimal import Decimal


CO2_MOLAR_MASS = Decimal("44.0")
CAO_MOLAR_MASS = Decimal("56.1")
MGO_MOLAR_MASS = Decimal("40.3")

CO2_PER_CAO = CO2_MOLAR_MASS / CAO_MOLAR_MASS
CO2_PER_MGO = CO2_MOLAR_MASS / MGO_MOLAR_MASS


@dataclass(frozen=True)
class ClinkerEntry:
    """One clinker type's annual production and measured composition."""

    clinker_produced_tonnes: Decimal
    cao_content_percent: Decimal  # includes free lime, per source sheet
    mgo_content_percent: Decimal


@dataclass(frozen=True)
class NonCarbonateEntry:
    """
    One pre-calcined raw material entering the kiln (e.g. fly ash,
    slag) whose CaO/MgO content did NOT come from carbonate and so
    must be excluded from the calcination CO2 total. Do not include
    recycled kiln dust here (per the source sheet's own instruction).
    """

    raw_material_consumed_tonnes: Decimal
    cao_content_percent: Decimal
    mgo_content_percent: Decimal


@dataclass
class ClinkerCalcinationResult:
    total_clinker_produced_tonnes: Decimal
    total_cao_tonnes: Decimal
    total_mgo_tonnes: Decimal
    non_carbonate_cao_tonnes: Decimal
    non_carbonate_mgo_tonnes: Decimal
    uncorrected_co2_tonnes: Decimal
    non_carbonate_correction_co2_tonnes: Decimal
    corrected_co2_tonnes: Decimal
    calcination_factor_uncorrected_kg_per_tonne_clinker: Decimal
    calcination_factor_corrected_kg_per_tonne_clinker: Decimal


def calculate_clinker_calcination_co2(
    clinker_entries: list[ClinkerEntry],
    non_carbonate_entries: list[NonCarbonateEntry] | None = None,
) -> ClinkerCalcinationResult:
    """
    Calculate CO2 from clinker calcination using the CSI stoichiometric
    method: total CaO and MgO actually measured in the clinker,
    converted to CO2 via their carbonate-decomposition mass ratios,
    less any CaO/MgO known to have entered the kiln from non-carbonate
    (already-calcined) sources.
    """

    if not clinker_entries:
        raise ValueError("clinker_entries must not be empty")

    non_carbonate_entries = non_carbonate_entries or []

    total_clinker = Decimal("0")
    total_cao = Decimal("0")
    total_mgo = Decimal("0")

    for entry in clinker_entries:
        if entry.clinker_produced_tonnes < 0:
            raise ValueError("clinker_produced_tonnes must not be negative")
        if not (Decimal("0") <= entry.cao_content_percent <= Decimal("1")):
            raise ValueError("cao_content_percent must be a fraction between 0 and 1")
        if not (Decimal("0") <= entry.mgo_content_percent <= Decimal("1")):
            raise ValueError("mgo_content_percent must be a fraction between 0 and 1")

        total_clinker += entry.clinker_produced_tonnes
        total_cao += entry.clinker_produced_tonnes * entry.cao_content_percent
        total_mgo += entry.clinker_produced_tonnes * entry.mgo_content_percent

    if total_clinker == 0:
        raise ValueError("total clinker produced must be greater than zero")

    non_carbonate_cao = Decimal("0")
    non_carbonate_mgo = Decimal("0")

    for nc_entry in non_carbonate_entries:
        if nc_entry.raw_material_consumed_tonnes < 0:
            raise ValueError("raw_material_consumed_tonnes must not be negative")

        non_carbonate_cao += (
            nc_entry.raw_material_consumed_tonnes * nc_entry.cao_content_percent
        )
        non_carbonate_mgo += (
            nc_entry.raw_material_consumed_tonnes * nc_entry.mgo_content_percent
        )

    uncorrected_co2 = total_cao * CO2_PER_CAO + total_mgo * CO2_PER_MGO
    correction_co2 = (
        non_carbonate_cao * CO2_PER_CAO + non_carbonate_mgo * CO2_PER_MGO
    )
    corrected_co2 = uncorrected_co2 - correction_co2

    factor_uncorrected = uncorrected_co2 * Decimal("1000") / total_clinker
    factor_corrected = corrected_co2 * Decimal("1000") / total_clinker

    return ClinkerCalcinationResult(
        total_clinker_produced_tonnes=total_clinker,
        total_cao_tonnes=total_cao,
        total_mgo_tonnes=total_mgo,
        non_carbonate_cao_tonnes=non_carbonate_cao,
        non_carbonate_mgo_tonnes=non_carbonate_mgo,
        uncorrected_co2_tonnes=uncorrected_co2,
        non_carbonate_correction_co2_tonnes=correction_co2,
        corrected_co2_tonnes=corrected_co2,
        calcination_factor_uncorrected_kg_per_tonne_clinker=factor_uncorrected,
        calcination_factor_corrected_kg_per_tonne_clinker=factor_corrected,
    )
