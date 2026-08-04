from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, require_writer
from app.database.session import get_db
from app.models.user import User
from app.repositories.manufacturing_unit_repository import ManufacturingUnitRepository
from app.schemas.manufacturing_unit import (
    ManufacturingUnitCreate,
    ManufacturingUnitResponse,
    ManufacturingUnitUpdate,
)
from app.services import sec_calculation_service
from app.services.aluminium_ghg_calculator import (
    AluminiumCellTechnology,
    calculate_tier1_default_co2,
)
from app.services.pulp_paper_ghg_calculator import (
    BiomassFuelType,
    QuantityBasis,
    calculate_biomass_co2,
)
from app.services.cement_ghg_calculator import (
    ClinkerEntry,
    NonCarbonateEntry,
    calculate_clinker_calcination_co2,
)
from app.services.iron_steel_ghg_calculator import (
    MaterialEntry,
    calculate_iron_steel_co2,
)
from app.services.refrigerant_ghg_calculator import (
    RefrigerantLifecycleEntry,
    calculate_refrigerant_lifecycle_co2e,
)
from pydantic import BaseModel
from app.services.manufacturing_unit_service import ManufacturingUnitService
router = APIRouter(
    prefix="/manufacturing-units",
    tags=["Manufacturing Units"],
)
def get_service(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ManufacturingUnitService:
    repository = ManufacturingUnitRepository(db, organization_id=current_user.organization_id)
    return ManufacturingUnitService(repository)
@router.get("/", response_model=list[ManufacturingUnitResponse])
def get_all_units(service: ManufacturingUnitService = Depends(get_service)):
    return service.get_all()
@router.get("/{unit_id}", response_model=ManufacturingUnitResponse)
def get_unit(unit_id: int, service: ManufacturingUnitService = Depends(get_service)):
    return service.get_by_id(unit_id)
@router.post(
    "/",
    response_model=ManufacturingUnitResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_writer)],
)
def create_unit(unit: ManufacturingUnitCreate, service: ManufacturingUnitService = Depends(get_service)):
    return service.create(unit)
@router.put(
    "/{unit_id}",
    response_model=ManufacturingUnitResponse,
    dependencies=[Depends(require_writer)],
)
def update_unit(
    unit_id: int,
    unit: ManufacturingUnitUpdate,
    service: ManufacturingUnitService = Depends(get_service),
):
    return service.update(unit_id, unit)
@router.delete(
    "/{unit_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_writer)],
)
def delete_unit(unit_id: int, service: ManufacturingUnitService = Depends(get_service)):
    service.delete(unit_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
@router.get("/{unit_id}/sec-summary")
def get_sec_summary(
    unit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """SEC (BEE PAT) / EnPI (ISO 50001) summary: baseline vs every period."""
    return sec_calculation_service.get_sec_summary(
        db=db,
        organization_id=current_user.organization_id,
        manufacturing_unit_id=unit_id,
    )
@router.get("/{unit_id}/aluminium-tier1-co2")
def get_aluminium_tier1_co2(
    unit_id: int,
    technology: AluminiumCellTechnology,
    aluminium_production_tonnes: float,
    current_user: User = Depends(get_current_user),
):
    """
    Aluminium GHG Protocol Cluster 1 - Tier 1 Default CO2 from smelting.
    Query params:
        technology: prebake | soderberg
        aluminium_production_tonnes: aluminium produced in the period (t)
    """
    return calculate_tier1_default_co2(
        technology=technology,
        aluminium_production_tonnes=aluminium_production_tonnes,
    )
@router.get("/{unit_id}/pulp-paper-biomass-co2")
def get_pulp_paper_biomass_co2(
    unit_id: int,
    fuel_type: BiomassFuelType,
    quantity: float,
    quantity_basis: QuantityBasis = QuantityBasis.MASS_TONNES,
    current_user: User = Depends(get_current_user),
):
    """
    Pulp & Paper sector GHG Protocol tool - biomass combustion CO2
    (biogenic, reported separately from fossil GHG totals).
    Query params:
        fuel_type: wood_bark | black_liquor | other_solid_biomass
        quantity: fuel quantity burned, in the unit named by quantity_basis
        quantity_basis: mass_tonnes (default) | energy_gj_lhv
    """
    from decimal import Decimal

    result = calculate_biomass_co2(
        fuel_type=fuel_type,
        quantity=Decimal(str(quantity)),
        quantity_basis=quantity_basis,
    )
    return {
        "fuel_type": result.fuel_type,
        "quantity_basis": result.quantity_basis,
        "quantity": str(result.quantity),
        "emission_factor": str(result.emission_factor),
        "emission_factor_unit": result.emission_factor_unit,
        "co2_kg_per_year": str(result.co2_kg_per_year),
        "co2_tonnes_per_year": str(result.co2_tonnes_per_year),
        "is_biogenic": result.is_biogenic,
        "note": result.note,
    }
@router.get("/{unit_id}/cement-calcination-co2")
def get_cement_calcination_co2(
    unit_id: int,
    clinker_produced_tonnes: float,
    cao_content_percent: float,
    mgo_content_percent: float,
    non_carbonate_raw_material_tonnes: float = 0,
    non_carbonate_cao_content_percent: float = 0,
    non_carbonate_mgo_content_percent: float = 0,
    current_user: User = Depends(get_current_user),
):
    """
    Cement sector CSI Protocol - clinker calcination CO2 (stoichiometric method).
    Query params:
        clinker_produced_tonnes: clinker produced in the period (t)
        cao_content_percent / mgo_content_percent: measured clinker
            composition, as a fraction (e.g. 0.65 for 65%)
        non_carbonate_*: optional correction for pre-calcined raw
            materials (e.g. fly ash, slag) entering the kiln; omit
            (defaults to 0) if none apply
    """
    from decimal import Decimal

    non_carbonate_entries = []
    if non_carbonate_raw_material_tonnes > 0:
        non_carbonate_entries.append(
            NonCarbonateEntry(
                raw_material_consumed_tonnes=Decimal(str(non_carbonate_raw_material_tonnes)),
                cao_content_percent=Decimal(str(non_carbonate_cao_content_percent)),
                mgo_content_percent=Decimal(str(non_carbonate_mgo_content_percent)),
            )
        )

    result = calculate_clinker_calcination_co2(
        clinker_entries=[
            ClinkerEntry(
                clinker_produced_tonnes=Decimal(str(clinker_produced_tonnes)),
                cao_content_percent=Decimal(str(cao_content_percent)),
                mgo_content_percent=Decimal(str(mgo_content_percent)),
            )
        ],
        non_carbonate_entries=non_carbonate_entries or None,
    )
    return {
        "total_clinker_produced_tonnes": str(result.total_clinker_produced_tonnes),
        "total_cao_tonnes": str(result.total_cao_tonnes),
        "total_mgo_tonnes": str(result.total_mgo_tonnes),
        "uncorrected_co2_tonnes": str(result.uncorrected_co2_tonnes),
        "non_carbonate_correction_co2_tonnes": str(result.non_carbonate_correction_co2_tonnes),
        "corrected_co2_tonnes": str(result.corrected_co2_tonnes),
        "calcination_factor_uncorrected_kg_per_tonne_clinker": str(
            result.calcination_factor_uncorrected_kg_per_tonne_clinker
        ),
        "calcination_factor_corrected_kg_per_tonne_clinker": str(
            result.calcination_factor_corrected_kg_per_tonne_clinker
        ),
    }
class MaterialEntryInput(BaseModel):
    material_name: str
    amount: float
    carbon_content: float


class IronSteelCO2Request(BaseModel):
    input_materials: list[MaterialEntryInput]
    output_materials: list[MaterialEntryInput] = []


@router.post("/{unit_id}/iron-steel-co2")
def get_iron_steel_co2(
    unit_id: int,
    payload: IronSteelCO2Request,
    current_user: User = Depends(get_current_user),
):
    """
    Iron & Steel sector GHG Protocol tool - CO2 via carbon mass-balance.
    Body:
        input_materials: list of {material_name, amount, carbon_content}
            for materials entering the process (e.g. coke, coal, limestone,
            dolomite, carbon electrodes, coke oven gas)
        output_materials: list of {material_name, amount, carbon_content}
            for materials leaving the process still carrying carbon
            (e.g. steel produced, iron not converted, BF gas offsite)
    amount and carbon_content must use consistent units across all
    entries; carbon_content is a fraction (0-1), not a percentage.
    """
    from decimal import Decimal

    result = calculate_iron_steel_co2(
        input_materials=[
            MaterialEntry(
                material_name=m.material_name,
                amount=Decimal(str(m.amount)),
                carbon_content=Decimal(str(m.carbon_content)),
            )
            for m in payload.input_materials
        ],
        output_materials=[
            MaterialEntry(
                material_name=m.material_name,
                amount=Decimal(str(m.amount)),
                carbon_content=Decimal(str(m.carbon_content)),
            )
            for m in payload.output_materials
        ],
    )
    return {
        "total_input_carbon": str(result.total_input_carbon),
        "total_output_carbon": str(result.total_output_carbon),
        "net_carbon": str(result.net_carbon),
        "co2_emissions": str(result.co2_emissions),
    }
class RefrigerantLifecycleRequest(BaseModel):
    refrigerant: str
    fill_new_equipment: float = 0
    fill_retrofitted_equipment: float = 0
    new_equipment_full_charge: float = 0
    retrofit_equipment_full_charge: float = 0
    service_amount_net: float = 0
    retired_equipment_full_charge: float = 0
    retrofitted_away_full_charge: float = 0
    recovered_from_retiring: float = 0
    recovered_from_retrofitted_away: float = 0


@router.post("/{unit_id}/refrigerant-lifecycle-co2e")
def get_refrigerant_lifecycle_co2e(
    unit_id: int,
    payload: RefrigerantLifecycleRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Refrigeration & AC Equipment GHG Protocol tool - fugitive HFC/PFC
    CO2e via the lifecycle-stage approach for equipment users
    (installation + use/servicing + disposal losses).
    All amounts in kilograms.
    Note: HCFCs (e.g. R-22) intentionally raise a 400 error -- the
    GHG Protocol excludes Montreal Protocol substances from GHG
    inventories; track R-22 leakage separately, not here.
    """
    from decimal import Decimal
    from fastapi import HTTPException

    entry = RefrigerantLifecycleEntry(
        refrigerant=payload.refrigerant,
        fill_new_equipment=Decimal(str(payload.fill_new_equipment)),
        fill_retrofitted_equipment=Decimal(str(payload.fill_retrofitted_equipment)),
        new_equipment_full_charge=Decimal(str(payload.new_equipment_full_charge)),
        retrofit_equipment_full_charge=Decimal(str(payload.retrofit_equipment_full_charge)),
        service_amount_net=Decimal(str(payload.service_amount_net)),
        retired_equipment_full_charge=Decimal(str(payload.retired_equipment_full_charge)),
        retrofitted_away_full_charge=Decimal(str(payload.retrofitted_away_full_charge)),
        recovered_from_retiring=Decimal(str(payload.recovered_from_retiring)),
        recovered_from_retrofitted_away=Decimal(str(payload.recovered_from_retrofitted_away)),
    )

    try:
        result = calculate_refrigerant_lifecycle_co2e(entry)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "refrigerant": result.refrigerant,
        "installation_emissions_kg": str(result.installation_emissions_kg),
        "use_emissions_kg": str(result.use_emissions_kg),
        "disposal_emissions_kg": str(result.disposal_emissions_kg),
        "total_emissions_kg": str(result.total_emissions_kg),
        "gwp": str(result.gwp),
        "co2e_tonnes": str(result.co2e_tonnes),
    }
