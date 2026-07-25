"""
Cross-Sector Fuel Library API.

GET /fuel-library        -> all 54 fuels with computed CO2e/TJ + CO2e/tonne
GET /fuel-library/{key}  -> one fuel's factors + computed CO2e

Read-only reference data (IPCC 2006 via GHG Protocol Cross-Sector Tools),
no auth scoping -- same spirit as the global emission_factors table.
"""

from fastapi import APIRouter, HTTPException, status

from app.services.cross_sector_ef_library import get_fuel, list_fuels

router = APIRouter(
    prefix="/fuel-library",
    tags=["Fuel Library"],
)


@router.get("/")
def get_all_fuels():
    """All 54 cross-sector fuels with computed CO2e (AR5 GWP)."""
    return list_fuels()


@router.get("/{fuel_key}")
def get_one_fuel(fuel_key: str):
    """One fuel's LHV + CO2/CH4/N2O factors + computed CO2e."""
    fuel = get_fuel(fuel_key)
    if fuel is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No fuel in library with key: {fuel_key}",
        )
    return fuel
