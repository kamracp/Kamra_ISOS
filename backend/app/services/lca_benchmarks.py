"""Published GWP benchmarks for plausibility checks on LCA results (LCA session 4).

Every entry is a published, cited figure; the source string names the document the value was read
from. Never add a value from memory. The check is a plausibility WARNING only -- it never alters
the computed result -- and it is skipped (not_computed, with a reason) whenever the product's
functional unit does not match the benchmark's, so nothing is silently rescaled.
"""

# ratio = product GWP / benchmark. Outside [LOW, HIGH] -> warning.
RATIO_LOW, RATIO_HIGH = 0.5, 2.0

BENCHMARKS: dict[str, dict] = {
    # --- cradle-to-gate (A1-A3): same boundary as this Studio -> primary choices for pressed tiles ---
    "ceramic_tile_epd_italy_2016": {
        "label": "Ceramic tiles - Italian sector average, cradle-to-gate A1-A3 (Confindustria Ceramica EPD 2016)",
        "value_kgco2e_per_fu": 10.5, "functional_unit": "m2", "range_low": 10.5, "range_high": 10.5,
        "boundary": "cradle-to-gate A1-A3 (EN 15804) - same boundary as this Studio; average tile 19.9 kg/m2",
        "source": "Confindustria Ceramica / IBU, EPD-COI-20160202-ICG1-EN (issued 26 Sep 2016), Italian average ceramic tile, 76 companies / 84 plants (82.6% of Italian output), 2014 data, GaBi 7; GWP A1-A3 = 1.05E+1 kg CO2-eq per m2",
    },
    "porcelain_stoneware_ferrari_2019_gate": {
        "label": "Porcelain stoneware - Italian district 2016, cradle-to-gate (Ferrari 2019, Table 9 body+glazes+production+packaging)",
        "value_kgco2e_per_fu": 11.98, "functional_unit": "m2", "range_low": 11.98, "range_high": 11.98,
        "boundary": "cradle-to-gate, derived as the sum of the Body (2.98), Glazes (0.168), Production (8.74) and Packaging (0.0924) columns of Table 9; full cradle-to-grave total is 23.8",
        "source": "Ferrari A.M., Volpi L., Pini M., Siligardi C., Garcia-Muina F.E., Settembre-Blundo D. (2019) Building a Sustainability Benchmarking Framework of Ceramic Tiles Based on LCSA. Resources 8:11, Table 9 (52,455,661 m2 sample, ~15% of Italian porcelain stoneware, 2016, IMPACT 2002+ modified, Ecoinvent 3.4)",
    },
    # --- cradle-to-grave: a cradle-to-gate result should sit BELOW these ---
    "ceramic_tile_ibanez_2011": {
        "label": "Ceramic tiles - Spanish sector average, cradle-to-grave (Ibanez-Fores 2011)",
        "value_kgco2e_per_fu": 13.2, "functional_unit": "m2", "range_low": 13.1, "range_high": 13.3,
        "boundary": "cradle-to-grave: 1 m2 over 20 years, 7 stages (clay mining, atomising, frits/glazes, tile production, distribution, installation and use, C&D waste); tile 17.23 kg/m2 - a cradle-to-gate result should sit below this",
        "source": "Ibanez-Fores V., Bovea M.D., Simo A. (2011) Life cycle assessment of ceramic tiles. Environmental and statistical analysis. Int J LCA 16:916-928; 35 Spanish enterprises; GWP mean 13.2 kg CO2 eq/m2, 95% CI [13.1, 13.3] (Table 8), CML 2001",
    },
    # --- niche product, kept for completeness; NOT comparable with pressed 600x600 tiles ---
    "ceramic_thin_slab_pini_2014": {
        "label": "Large thin porcelain slab 3.5 mm with fibreglass backing - single plant, cradle-to-grave (Pini 2014) - not for pressed tiles",
        "value_kgco2e_per_fu": 16.32, "functional_unit": "m2", "range_low": 16.32, "range_high": 16.32,
        "boundary": "cradle-to-grave excluding installation and use; distribution 100 km EPD scenario; single plant (Laminam), slab 8.2 kg/m2 with polyurethane-bonded fibreglass backing",
        "source": "Pini M., Ferrari A.M., Gamberini R., Neri P., Rimini B. (2014) Life cycle assessment of a large, thin ceramic tile with advantageous technological properties. Int J LCA 19:1567-1580; Table 7 climate change 16.32 kg CO2 eq per m2 (IMPACT 2002+)",
    },
}

_UNIT_ALIASES = {"m²": "m2", "sqm": "m2", "sq.m": "m2", "t": "tonne", "tonnes": "tonne", "mt": "tonne"}


def _norm(u: str | None) -> str:
    u = (u or "").strip().lower()
    return _UNIT_ALIASES.get(u, u)


def list_benchmark_options() -> list[dict]:
    return [{"key": k, "label": v["label"], "functional_unit": v["functional_unit"], "value_kgco2e_per_fu": v["value_kgco2e_per_fu"]}
            for k, v in BENCHMARKS.items()]


def benchmark_check(key: str | None, functional_unit: str | None, gwp_kgco2e_per_fu: float | None) -> dict | None:
    """None when no benchmark is selected; otherwise a dict with status calculated / not_computed."""
    if not key:
        return None
    b = BENCHMARKS.get(key)
    base = {"key": key}
    if b is None:
        return {**base, "status": "not_computed", "reason": f"unknown benchmark key '{key}'"}
    base.update({"label": b["label"], "value_kgco2e_per_fu": b["value_kgco2e_per_fu"], "functional_unit": b["functional_unit"],
                 "range_low": b["range_low"], "range_high": b["range_high"], "boundary": b["boundary"], "source": b["source"]})
    if _norm(functional_unit) != _norm(b["functional_unit"]):
        return {**base, "status": "not_computed",
                "reason": f"functional unit '{functional_unit}' does not match benchmark unit '{b['functional_unit']}' - no rescaling attempted"}
    if gwp_kgco2e_per_fu is None:
        return {**base, "status": "not_computed", "reason": "product GWP not computed"}
    ratio = gwp_kgco2e_per_fu / b["value_kgco2e_per_fu"]
    if ratio > RATIO_HIGH:
        warning = f"result is {ratio:.1f}x the published benchmark - check inventory quantities, units and basis (per FU vs annual total)"
    elif ratio < RATIO_LOW:
        warning = f"result is {ratio:.2f}x the published benchmark - check for missing inventory items or an incomplete boundary"
    else:
        warning = None
    return {**base, "status": "calculated", "ratio": round(ratio, 3), "warning": warning}
