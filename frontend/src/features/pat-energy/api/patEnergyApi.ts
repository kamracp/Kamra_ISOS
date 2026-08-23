import client from "../../../services/api/client";

export interface PatCycleTarget {
  id: number;
  organization_id: number;
  manufacturing_unit_id: number;
  cycle_number: number;
  cycle_start_year: number;
  cycle_end_year: number;
  baseline_production_qty: number;
  production_unit: string;
  baseline_energy_gj: number;
  mandated_reduction_percent: number;
  baseline_sec_gj_per_unit: number;
  target_sec_gj_per_unit: number;
  created_at: string;
  updated_at: string;
}

export interface PatCycleTargetCreate {
  cycle_number: number;
  cycle_start_year: number;
  cycle_end_year: number;
  baseline_production_qty: number;
  production_unit: string;
  baseline_energy_gj: number;
  mandated_reduction_percent: number;
}

export interface PatCycleTargetUpdate {
  cycle_start_year?: number;
  cycle_end_year?: number;
  baseline_production_qty?: number;
  production_unit?: string;
  baseline_energy_gj?: number;
  mandated_reduction_percent?: number;
}

export interface PatSummary {
  manufacturing_unit_id: number;
  year: number;
  actual_energy_gj: number | null;
  actual_production_qty: number | null;
  actual_sec_gj_per_unit: number | null;
  target: PatCycleTarget | null;
  on_track: boolean | null;
  message: string | null;
}

export const patEnergyApi = {
  getTargets: async (unitId: number): Promise<PatCycleTarget[]> => {
    const response = await client.get<PatCycleTarget[]>(`/pat-energy/targets/${unitId}`);
    return response.data;
  },
  createTarget: async (unitId: number, data: PatCycleTargetCreate): Promise<PatCycleTarget> => {
    const response = await client.post<PatCycleTarget>(`/pat-energy/targets/${unitId}`, data);
    return response.data;
  },
  updateTarget: async (targetId: number, data: PatCycleTargetUpdate): Promise<PatCycleTarget> => {
    const response = await client.put<PatCycleTarget>(`/pat-energy/targets/${targetId}`, data);
    return response.data;
  },
  deleteTarget: async (targetId: number): Promise<void> => {
    await client.delete(`/pat-energy/targets/${targetId}`);
  },

  getPatSummary: async (unitId: number, year: number): Promise<PatSummary> => {
    const response = await client.get<PatSummary>(`/pat-energy/pat-summary/${unitId}`, {
      params: { year },
    });
    return response.data;
  },
};

export default patEnergyApi;
