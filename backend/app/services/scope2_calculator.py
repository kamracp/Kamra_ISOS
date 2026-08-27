"""
Shared Scope 2 (purchased electricity) CO2e calculation helper.
Used by both ManufacturingElectricityService (per-record serialization)
and ManufacturingCarbonService (org-wide summary aggregation) so the
country-grid-factor derivation logic lives in exactly one place.
"""
from __future__ import annotations
from app.services.country_config import get_country_config


def calculate_scope2(country_code: str, consumed_kwh: float, renewable_kwh: float) -> dict:
    """Returns scope2_co2e_kg, grid_factor_kgco2e_per_kwh, grid_factor_source.
    scope2_co2e_kg stays None (never guessed/zeroed) when the country has
    no verified grid factor yet.
    """
    country_cfg = get_country_config(country_code)
    if not country_cfg or country_cfg.get("grid_factor_kgco2e_per_kwh") is None:
        return {
            "scope2_co2e_kg": None,
            "grid_factor_kgco2e_per_kwh": None,
            "grid_factor_source": None,
        }
    grid_factor = country_cfg["grid_factor_kgco2e_per_kwh"]
    billed_kwh = max((consumed_kwh or 0.0) - (renewable_kwh or 0.0), 0.0)
    return {
        "scope2_co2e_kg": round(billed_kwh * grid_factor, 3),
        "grid_factor_kgco2e_per_kwh": grid_factor,
        "grid_factor_source": country_cfg["grid_factor_source"],
    }
