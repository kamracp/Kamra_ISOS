"""Fuel-library key -> DEFRA 2026 'WTT- fuels' meter_type (Scope 3 category 3).

Name mapping only; factor VALUES come from the seeded emission_factors rows (DEFRA).
IPCC coal sub-types are mapped to DEFRA's single 'Coal (industrial)' WTT row -- the
closest published WTT figure; noted in the row's notes. Keys absent here stay
'not computed' with a visible reason (never a guessed proxy).
"""
FUEL_WTT_METER_TYPE: dict[str, str] = {
    "other_bituminous_coal": "wtt_coal_industrial",
    "sub_bituminous_coal": "wtt_coal_industrial",
    "anthracite": "wtt_coal_industrial",
    "lignite": "wtt_coal_industrial",
    "coking_coal": "wtt_coking_coal",
    "petroleum_coke": "wtt_petroleum_coke",
    "gas_diesel_oil": "wtt_diesel_100_mineral_diesel",
    "residual_fuel_oil": "wtt_fuel_oil",
    "motor_gasoline": "wtt_petrol_100_mineral_petrol",
    "jet_kerosene": "wtt_aviation_turbine_fuel",
    "other_kerosene": "wtt_burning_oil",
    "naphtha": "wtt_naphtha",
    "lubricants": "wtt_lubricants",
    "liquified_petroleum_gases": "wtt_lpg",
    "natural_gas": "wtt_natural_gas_100_mineral_blend",
    # DEFRA "WTT- bioenergy / WTT- biomass" rows (tonnes). Wood or wood waste -> Wood chips: industrial
    # wood-waste fuel is chipped/hogged, and chips is the published figure closest to that form
    # (logs = domestic, pellets = processed product). Agri-residues -> DEFRA's only agri-residue row.
    "wood_or_wood_waste": "wtt_wood_chips",
    "other_primary_solid_biomass_fuels": "wtt_grass_straw",
    # unmapped (no DEFRA tonnes row): charcoal, sulphite_lyes_black_liquor, biodiesels, biogasoline
}
