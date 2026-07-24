import client from "../../../services/api/client";

export interface NetZeroTarget {
  id: number;
  organization_id: number;
  building_id?: number;
  manufacturing_unit_id?: number;
  target_name: string;
  baseline_year: number;
  baseline_co2e_tonnes: number;
  target_year: number;
  reduction_percentage: number;
  target_type: "near_term" | "long_term";
  scope_coverage: string;
  remarks?: string;
}

export interface NetZeroTargetCreate {
  building_id?: number;
  manufacturing_unit_id?: number;
  target_name: string;
  baseline_year: number;
  baseline_co2e_tonnes: number;
  target_year: number;
  reduction_percentage: number;
  target_type?: "near_term" | "long_term";
  scope_coverage?: string;
  remarks?: string;
}

export type ProjectCategory =
  | "energy_efficiency"
  | "renewable_generation"
  | "fuel_switching"
  | "waste_heat_recovery"
  | "electrification"
  | "ccus"
  | "other";

export type ProjectStatus = "proposed" | "approved" | "in_progress" | "completed";

export interface DecarbonizationProject {
  id: number;
  organization_id: number;
  building_id?: number;
  manufacturing_unit_id?: number;
  project_name: string;
  category: ProjectCategory;
  status: ProjectStatus;
  capex: number;
  annual_opex_delta: number;
  lifespan_years: number;
  annual_co2e_abated_tonnes: number;
  remarks?: string;
}

export interface DecarbonizationProjectCreate {
  building_id?: number;
  manufacturing_unit_id?: number;
  project_name: string;
  category: ProjectCategory;
  status?: ProjectStatus;
  capex: number;
  annual_opex_delta?: number;
  lifespan_years: number;
  annual_co2e_abated_tonnes: number;
  remarks?: string;
}

export interface MaccEntry {
  id: number;
  project_name: string;
  category: ProjectCategory;
  status: ProjectStatus;
  capex: number;
  annual_opex_delta: number;
  lifespan_years: number;
  annual_co2e_abated_tonnes: number;
  annualized_capex: number;
  marginal_abatement_cost: number | null;
}

export interface NetZeroSummary {
  status: string;
  target_id?: number;
  target_name?: string;
  baseline_year?: number;
  baseline_co2e_tonnes?: number;
  target_year?: number;
  target_co2e_tonnes?: number;
  reduction_percentage?: number;
  current_year?: number;
  current_actual_co2e_tonnes?: number;
  expected_co2e_tonnes_on_trajectory?: number;
  gap_tonnes?: number;
  on_track?: boolean;
  macc: MaccEntry[];
}

export const netZeroTargetApi = {
  getAll: async (): Promise<NetZeroTarget[]> => {
    const response = await client.get<NetZeroTarget[]>("/net-zero-targets/");
    return response.data;
  },
  create: async (data: NetZeroTargetCreate): Promise<NetZeroTarget> => {
    const response = await client.post<NetZeroTarget>("/net-zero-targets/", data);
    return response.data;
  },
  remove: async (id: number): Promise<void> => {
    await client.delete(`/net-zero-targets/${id}`);
  },
  getSummary: async (id: number): Promise<NetZeroSummary> => {
    const response = await client.get<NetZeroSummary>(`/net-zero-targets/${id}/summary`);
    return response.data;
  },
};

export const decarbonizationProjectApi = {
  getAll: async (): Promise<DecarbonizationProject[]> => {
    const response = await client.get<DecarbonizationProject[]>("/decarbonization-projects/");
    return response.data;
  },
  create: async (data: DecarbonizationProjectCreate): Promise<DecarbonizationProject> => {
    const response = await client.post<DecarbonizationProject>(
      "/decarbonization-projects/",
      data
    );
    return response.data;
  },
  remove: async (id: number): Promise<void> => {
    await client.delete(`/decarbonization-projects/${id}`);
  },
};
