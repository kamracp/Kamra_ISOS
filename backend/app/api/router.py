from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.organization import router as organization_router
from app.api.department import router as department_router
from app.api.building import router as building_router
from app.api.floor import router as floor_router
from app.api.space import router as space_router
from app.api.energy_meter import router as energy_meter_router
from app.api.utility_bill import router as utility_bill_router
from app.api.emission_factor import router as emission_factor_router
from app.api.carbon import router as carbon_router
from app.api.manufacturing_carbon import router as manufacturing_carbon_router
from app.api.hvac_equipment import router as hvac_equipment_router
from app.api.occupant import router as occupant_router
from app.api.tenant_billing import router as tenant_billing_router
from app.api.manufacturing_unit import router as manufacturing_unit_router
from app.api.production_record import router as production_record_router
from app.api.facility_category import router as facility_category_router
from app.api.net_zero_target import router as net_zero_target_router
from app.api.decarbonization_project import router as decarbonization_project_router
from app.api.climate_risk import router as climate_risk_router
from app.api.countries import router as countries_router
from app.api.fuel_library import router as fuel_library_router
from app.api.esg_report import router as esg_report_router
from app.api.brsr_profile import router as brsr_profile_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(organization_router)
api_router.include_router(department_router)
api_router.include_router(building_router)
api_router.include_router(floor_router)
api_router.include_router(space_router)
api_router.include_router(energy_meter_router)
api_router.include_router(utility_bill_router)
api_router.include_router(emission_factor_router)
api_router.include_router(carbon_router)
api_router.include_router(manufacturing_carbon_router)
api_router.include_router(hvac_equipment_router)
api_router.include_router(occupant_router)
api_router.include_router(tenant_billing_router)
api_router.include_router(manufacturing_unit_router)
api_router.include_router(production_record_router)
api_router.include_router(facility_category_router)
api_router.include_router(net_zero_target_router)
api_router.include_router(decarbonization_project_router)
api_router.include_router(climate_risk_router)
api_router.include_router(countries_router)
api_router.include_router(fuel_library_router)
api_router.include_router(esg_report_router)
api_router.include_router(brsr_profile_router)
