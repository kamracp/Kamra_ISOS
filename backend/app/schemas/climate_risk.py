from pydantic import BaseModel, ConfigDict, Field

from app.models.climate_risk import RiskCategory, RiskTimeHorizon, RiskLikelihood


class ClimateRiskBase(BaseModel):
    building_id: int | None = None
    manufacturing_unit_id: int | None = None
    risk_name: str = Field(..., min_length=1, max_length=200)
    category: RiskCategory
    time_horizon: RiskTimeHorizon
    likelihood: RiskLikelihood
    estimated_financial_impact_inr: float = Field(..., ge=0)
    mitigation_cost_inr: float = 0.0
    mitigation_benefit_inr: float = 0.0
    description: str | None = None
    mitigation_action: str | None = None
    remarks: str | None = None


class ClimateRiskCreate(ClimateRiskBase):
    pass


class ClimateRiskUpdate(BaseModel):
    building_id: int | None = None
    manufacturing_unit_id: int | None = None
    risk_name: str | None = Field(default=None, min_length=1, max_length=200)
    category: RiskCategory | None = None
    time_horizon: RiskTimeHorizon | None = None
    likelihood: RiskLikelihood | None = None
    estimated_financial_impact_inr: float | None = Field(default=None, ge=0)
    mitigation_cost_inr: float | None = None
    mitigation_benefit_inr: float | None = None
    description: str | None = None
    mitigation_action: str | None = None
    remarks: str | None = None


class ClimateRiskResponse(ClimateRiskBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    organization_id: int
    net_risk_exposure_inr: float
