"""
Countries API — exposes the country/region config layer.

GET /countries        -> full list (region-grouped dropdown source)
GET /countries/{code} -> one country's grid factor + applicable standards

Read-only reference data, no auth scoping (same spirit as the global
emission_factors table). Backed by app.services.country_config.
"""

from fastapi import APIRouter, HTTPException, status

from app.services.country_config import get_country_config, list_countries

router = APIRouter(
    prefix="/countries",
    tags=["Countries"],
)


@router.get("/")
def get_all_countries():
    """All configured countries (each carries its region for grouping)."""
    return list_countries()


@router.get("/{code}")
def get_country(code: str):
    """One country's config by ISO code (e.g. IN, GB, AE)."""
    cfg = get_country_config(code)
    if cfg is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No country config for code: {code}",
        )
    return cfg
