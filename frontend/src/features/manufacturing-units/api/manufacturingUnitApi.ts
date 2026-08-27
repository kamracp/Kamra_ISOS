import client from "../../../services/api/client";

export type PatSector =
  | "aluminium"
  | "cement"
  | "chlor_alkali"
  | "fertilizer"
  | "iron_steel"
  | "pulp_paper"
  | "textile"
  | "thermal_power"
  | "refineries"
  | "railways"
  | "discoms"
  | "petrochemicals"
  | "other";

export interface ManufacturingUnit {
  id: number;
  organization_id: number;
  building_id?: number;
  unit_code: string;
  unit_name: string;
  sector: PatSector;
  baseline_year: number;
  standards_applicable?: string;
  // ISO country code (e.g. "IN", "GB", "AE") -- selects this unit's
  // Scope 2 grid factor + applicable standards via /countries. Backend
  // defaults to "IN" if omitted.
  country_code?: string;
  category_id?: number;
  remarks?: string;
  is_active: boolean;
}

export interface ManufacturingUnitCreate {
  building_id?: number;
  unit_code: string;
  unit_name: string;
  sector: PatSector;
  baseline_year: number;
  standards_applicable?: string;
  country_code?: string;
  category_id?: number;
  remarks?: string;
}

export interface ManufacturingUnitUpdate {
  building_id?: number;
  unit_code?: string;
  unit_name?: string;
  sector?: PatSector;
  baseline_year?: number;
  standards_applicable?: string;
  country_code?: string;
  category_id?: number;
  remarks?: string;
  is_active?: boolean;
}

export interface SecPeriodResult {
  status: string;
  manufacturing_unit_id: number;
  period_start?: string;
  period_end?: string;
  total_energy_gj?: number;
  production_quantity?: number;
  production_unit?: string;
  sec_gj_per_unit?: number;
  bills_pending_energy_content?: { bill_id: number; meter_code: string; meter_type: string }[];
  pct_change_vs_baseline?: number | null;
}

export interface SecSummary {
  status: string;
  manufacturing_unit_id: number;
  sector?: string;
  baseline_year?: number;
  baseline_sec_gj_per_unit?: number | null;
  standards_applicable?: string;
  periods: SecPeriodResult[];
}

export const manufacturingUnitApi = {
  getAll: async (): Promise<ManufacturingUnit[]> => {
    const response = await client.get<ManufacturingUnit[]>("/manufacturing-units/");
    return response.data;
  },
  getById: async (id: number): Promise<ManufacturingUnit> => {
    const response = await client.get<ManufacturingUnit>(`/manufacturing-units/${id}`);
    return response.data;
  },
  create: async (data: ManufacturingUnitCreate): Promise<ManufacturingUnit> => {
    const response = await client.post<ManufacturingUnit>("/manufacturing-units/", data);
    return response.data;
  },
  update: async (id: number, data: ManufacturingUnitUpdate): Promise<ManufacturingUnit> => {
    const response = await client.put<ManufacturingUnit>(`/manufacturing-units/${id}`, data);
    return response.data;
  },
  remove: async (id: number): Promise<void> => {
    await client.delete(`/manufacturing-units/${id}`);
  },
  getSecSummary: async (id: number): Promise<SecSummary> => {
    const response = await client.get<SecSummary>(`/manufacturing-units/${id}/sec-summary`);
    return response.data;
  },
};

export default manufacturingUnitApi;
