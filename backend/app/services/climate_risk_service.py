from app.core.exceptions import ResourceNotFoundException
from app.models.climate_risk import ClimateRisk
from app.repositories.climate_risk_repository import ClimateRiskRepository
from app.schemas.climate_risk import (
    ClimateRiskCreate,
    ClimateRiskResponse,
    ClimateRiskUpdate,
)


def _to_response(risk: ClimateRisk) -> ClimateRiskResponse:
    """Attach the derived net risk exposure (TCFD-style financial quantification):
    Net Risk Exposure (Rs) = Estimated Financial Impact - Mitigation Benefit.
    Mitigation cost is tracked separately (it is a spend, not a risk offset)."""
    net_exposure = risk.estimated_financial_impact_inr - risk.mitigation_benefit_inr
    return ClimateRiskResponse(
        id=risk.id,
        organization_id=risk.organization_id,
        building_id=risk.building_id,
        manufacturing_unit_id=risk.manufacturing_unit_id,
        risk_name=risk.risk_name,
        category=risk.category,
        time_horizon=risk.time_horizon,
        likelihood=risk.likelihood,
        estimated_financial_impact_inr=risk.estimated_financial_impact_inr,
        mitigation_cost_inr=risk.mitigation_cost_inr,
        mitigation_benefit_inr=risk.mitigation_benefit_inr,
        description=risk.description,
        mitigation_action=risk.mitigation_action,
        remarks=risk.remarks,
        net_risk_exposure_inr=net_exposure,
    )


class ClimateRiskService:
    def __init__(self, repository: ClimateRiskRepository):
        self.repository = repository

    def get_all(self) -> list[ClimateRiskResponse]:
        return [_to_response(r) for r in self.repository.get_all()]

    def get_by_id(self, risk_id: int) -> ClimateRiskResponse:
        risk = self.repository.get_by_id(risk_id)
        if not risk:
            raise ResourceNotFoundException("Climate Risk", risk_id)
        return _to_response(risk)

    def create(self, data: ClimateRiskCreate) -> ClimateRiskResponse:
        risk = self.repository.create(data)
        return _to_response(risk)

    def update(self, risk_id: int, data: ClimateRiskUpdate) -> ClimateRiskResponse:
        risk = self.repository.get_by_id(risk_id)
        if not risk:
            raise ResourceNotFoundException("Climate Risk", risk_id)
        updated = self.repository.update(risk, data)
        return _to_response(updated)

    def delete(self, risk_id: int) -> None:
        risk = self.repository.get_by_id(risk_id)
        if not risk:
            raise ResourceNotFoundException("Climate Risk", risk_id)
        self.repository.delete(risk)

    def get_summary(self) -> dict:
        """Portfolio-level TCFD risk summary: totals by category and overall exposure."""
        risks = self.repository.get_all()
        total_impact = sum(r.estimated_financial_impact_inr for r in risks)
        total_mitigation_cost = sum(r.mitigation_cost_inr for r in risks)
        total_mitigation_benefit = sum(r.mitigation_benefit_inr for r in risks)
        total_net_exposure = total_impact - total_mitigation_benefit

        by_category: dict[str, float] = {}
        for r in risks:
            key = r.category.value if hasattr(r.category, "value") else r.category
            by_category[key] = by_category.get(key, 0.0) + (
                r.estimated_financial_impact_inr - r.mitigation_benefit_inr
            )

        return {
            "total_risks": len(risks),
            "total_estimated_financial_impact_inr": total_impact,
            "total_mitigation_cost_inr": total_mitigation_cost,
            "total_mitigation_benefit_inr": total_mitigation_benefit,
            "total_net_risk_exposure_inr": total_net_exposure,
            "net_risk_exposure_by_category_inr": by_category,
        }
