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

// ---- Energy balance (ISO 50001 energy review, PAT split) ----
export interface FuelRow { fuel_key: string; fuel_name: string | null; is_biogenic: boolean; tonnes: number; energy_gj: number; scope1_co2e_kg: number; biogenic_co2_kg: number }
export interface EnergyPeriod {
  status: string;
  period_start: string; period_end: string;
  production_quantity: number; production_unit: string;
  total_energy_gj?: number; total_energy_toe?: number;
  sec_gj_per_unit?: number | null; sec_toe_per_unit?: number | null;
  thermal_sec_gcal_per_unit?: number | null; electrical_sec_kwh_per_unit?: number | null;
  renewable_share_percent?: number | null; source_basis?: string;
  by_fuel?: FuelRow[]; scope1_combustion_co2e_kg?: number;
  excluded_overlapping?: { kind: string; id: number; period_start: string; period_end: string }[];
  hint?: string;
}
export interface EnergyBalance {
  manufacturing_unit_id: number; year: number;
  periods: EnergyPeriod[];
  year_totals: {
    production_quantity: number; total_energy_gj: number; total_energy_toe: number; thermal_gj: number; electricity_kwh: number;
    sec_gj_per_unit: number | null; sec_toe_per_unit: number | null; thermal_sec_gcal_per_unit: number | null; electrical_sec_kwh_per_unit: number | null;
    scope1_combustion_co2e_kg: number; pat_dc_threshold_toe: number | null; is_designated_consumer_scale: boolean | null;
  };
  periods_without_energy_data: string[];
}
export const getEnergyBalance = async (unitId: number, year: number): Promise<EnergyBalance> =>
  (await client.get<EnergyBalance>(`/pat-energy/energy-balance/${unitId}`, { params: { year } })).data;

// ---- Org energy dashboard ----
export interface OrgEnergyUnitRow {
  manufacturing_unit_id: number; unit_code: string; unit_name: string; sector: string; country_code: string;
  total_energy_gj: number; total_energy_toe: number; electrical_gj: number; thermal_gj: number;
  renewable_share_percent: number | null; production_quantity: number; production_unit: string | null;
  sec_gj_per_unit: number | null; scope1_combustion_co2e_kg: number; source_basis: string;
  pat_dc_threshold_toe: number | null; is_designated_consumer_scale: boolean | null;
}
export interface OrgEnergy {
  year: number;
  totals: { total_gj: number; total_toe: number; renewable_gj: number; non_renewable_gj: number; electrical_gj: number; electricity_kwh: number; renewable_kwh: number; thermal_gj: number; biomass_gj: number; by_fuel_gj: Record<string, number>; units_with_data: number; record_count: number };
  units: OrgEnergyUnitRow[];
}
export const getOrgEnergy = async (year: number): Promise<OrgEnergy> =>
  (await client.get<OrgEnergy>("/pat-energy/org-energy", { params: { year } })).data;
