from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.database.base import Base
from app.database.session import engine

from app.models.organization import Organization
from app.models.department import Department
from app.models.building import Building
from app.models.floor import Floor
from app.models.space import Space
from app.models.energy_meter import EnergyMeter
from app.models.utility_bill import UtilityBill
from app.models.emission_factor import EmissionFactor
from app.models.hvac_equipment import HvacEquipment
from app.models.occupant import Occupant
from app.models.manufacturing_unit import ManufacturingUnit
from app.models.production_record import ProductionRecord
from app.models.manufacturing_emission_record import ManufacturingEmissionRecord
from app.models.pat_cycle_target import PatCycleTarget
from app.models.facility_category import FacilityCategory
from app.models.net_zero_target import NetZeroTarget
from app.models.decarbonization_project import DecarbonizationProject
from app.models.climate_risk import ClimateRisk
from app.models.brsr_organization_profile import BrsrOrganizationProfile
from app.models.brsr_policy_disclosure import BrsrPolicyDisclosure
from app.models.water_record import WaterRecord
from app.models.policy_advocacy_record import PolicyAdvocacyRecord, TradeAssociation
from app.models.stakeholder_engagement_record import StakeholderEngagementRecord, StakeholderGroup
from app.models.csr_record import CsrRecord, CsrProject
from app.models.ethics_record import EthicsRecord
from app.models.waste_record import WasteRecord



# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Kamra ISOS API",
    description="Industrial Sustainability Operating System (includes BENAS Building/Real-Estate module and Manufacturing module)",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:4001",
        "http://127.0.0.1:4001",
        "http://localhost:4002",
        "http://127.0.0.1:4002",
        "https://benas.kamraengineeringsolution.com",
        "https://manufactureos.kamraengineeringsolution.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "application": "Kamra BENAS API",
        "status": "running",
        "version": "0.1.0",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


# Enterprise API
app.include_router(api_router, prefix="/api/v1")