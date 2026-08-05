import client from "../../../services/api/client";

export type RiskCategory =
  | "physical_acute"
  | "physical_chronic"
  | "transition_policy_legal"
  | "transition_technology"
  | "transition_market"
  | "transition_reputation";

export type RiskTimeHorizon = "short_term" | "medium_term" | "long_term";

export type RiskLikelihood = "unlikely" | "possible" | "likely" | "almost_certain";

export interface ClimateRisk {
  id: number;
  organization_id: number;
  building_id?: number;
  manufacturing_unit_id?: number;
  risk_name: string;
  category: RiskCategory;
  time_horizon: RiskTimeHorizon;
  likelihood: RiskLikelihood;
  estimated_financial_impact_inr: number;
  mitigation_cost_inr: number;
  mitigation_benefit_inr: number;
  description?: string;
  mitigation_action?: string;
  remarks?: string;
  net_risk_exposure_inr: number;
}

export interface ClimateRiskCreate {
  building_id?: number;
  manufacturing_unit_id?: number;
  risk_name: string;
  category: RiskCategory;
  time_horizon: RiskTimeHorizon;
  likelihood: RiskLikelihood;
  estimated_financial_impact_inr: number;
  mitigation_cost_inr?: number;
  mitigation_benefit_inr?: number;
  description?: string;
  mitigation_action?: string;
  remarks?: string;
}

export interface ClimateRiskSummary {
  total_risks: number;
  total_estimated_financial_impact_inr: number;
  total_mitigation_cost_inr: number;
  total_mitigation_benefit_inr: number;
  total_net_risk_exposure_inr: number;
  net_risk_exposure_by_category_inr: Record<string, number>;
}

export const CATEGORY_LABELS: Record<RiskCategory, string> = {
  physical_acute: "Physical - Acute",
  physical_chronic: "Physical - Chronic",
  transition_policy_legal: "Transition - Policy & Legal",
  transition_technology: "Transition - Technology",
  transition_market: "Transition - Market",
  transition_reputation: "Transition - Reputation",
};

export const climateRiskApi = {
  getAll: async (): Promise<ClimateRisk[]> => {
    const response = await client.get<ClimateRisk[]>("/climate-risks/");
    return response.data;
  },
  create: async (data: ClimateRiskCreate): Promise<ClimateRisk> => {
    const response = await client.post<ClimateRisk>("/climate-risks/", data);
    return response.data;
  },
  remove: async (id: number): Promise<void> => {
    await client.delete(`/climate-risks/${id}`);
  },
  getSummary: async (): Promise<ClimateRiskSummary> => {
    const response = await client.get<ClimateRiskSummary>("/climate-risks/reports/summary");
    return response.data;
  },
};
