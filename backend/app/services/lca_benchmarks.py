"""Published GWP benchmarks for plausibility checks on LCA results (LCA session 4).

Every entry is a published, cited figure; the source string names the document the value was read
from. Never add a value from memory. The check is a plausibility WARNING only -- it never alters
the computed result -- and it is skipped (not_computed, with a reason) whenever the product's
functional unit does not match the benchmark's, so nothing is silently rescaled.
"""

# ratio = product GWP / benchmark. Outside [LOW, HIGH] -> warning.
RATIO_LOW, RATIO_HIGH = 0.5, 2.0

BENCHMARKS: dict[str, dict] = {
    "ceramic_tile_ibanez_2011": {
        "label": "Ceramic tiles - Spanish sector average (Ibanez-Fores 2011)",
        "value_kgco2e_per_fu": 13.2,
        "functional_unit": "m2",
        "range_low": 13.1, "range_high": 13.3,
        "boundary": "as published -- confirm the system boundary in the paper before citing it alongside a cradle-to-gate result",
        "source": "Ibanez-Fores V., Bovea M.D., Simo A. (2011) Life cycle assessment of ceramic tiles. Environmental and statistical analysis. Int J LCA 16:916-928; mean GWP per m2, 95% CI 13.1-13.3",
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
