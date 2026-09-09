import client from "../../../services/api/client";

export type FuelPurpose = "process_heat" | "captive_power" | "steam_boiler" | "transport" | "other";
export const PURPOSE_LABELS: Record<FuelPurpose, string> = {
  process_heat: "Process heat (kiln / furnace)",
  captive_power: "Captive power",
  steam_boiler: "Steam boiler",
  transport: "Transport",
  other: "Other",
};

export interface FuelLibraryEntry {
  key: string;
  name: string;
  category: string;
  lhv_tj_per_gg: number | null; // == GJ per tonne
  co2e_kg_per_tonne: number | null;
  is_biogenic: boolean;
}

export interface ManufacturingFuelRecord {
  id: number;
  organization_id: number;
  manufacturing_unit_id: number;
  period_start: string;
  period_end: string;
  fuel_key: string;
  quantity_tonnes: number;
  purpose: FuelPurpose;
  source?: string | null;
  remarks?: string | null;
  fuel_name?: string | null;
  fuel_category?: string | null;
  is_biogenic?: boolean | null;
  // derived by backend
  lhv_gj_per_tonne?: number | null;
  energy_gj?: number | null;
  energy_toe?: number | null;
  scope1_co2e_kg?: number | null;
  biogenic_co2_kg?: number | null;
  factor_source?: string;
  created_at: string;
  updated_at: string;
}

export interface ManufacturingFuelRecordCreate {
  manufacturing_unit_id: number;
  period_start: string;
  period_end: string;
  fuel_key: string;
  quantity_tonnes: number;
  purpose: FuelPurpose;
  source?: string;
  remarks?: string;
}
export type ManufacturingFuelRecordUpdate = Partial<Omit<ManufacturingFuelRecordCreate, "manufacturing_unit_id">>;

const BASE = "/manufacturing-fuel-records";

export const manufacturingFuelsApi = {
  library: async (): Promise<FuelLibraryEntry[]> => (await client.get<FuelLibraryEntry[]>(`${BASE}/library`)).data,
  getAll: async (year?: number): Promise<ManufacturingFuelRecord[]> =>
    (await client.get<ManufacturingFuelRecord[]>(`${BASE}/`, { params: year ? { year } : undefined })).data,
  create: async (data: ManufacturingFuelRecordCreate) => (await client.post<ManufacturingFuelRecord>(`${BASE}/`, data)).data,
  update: async (id: number, data: ManufacturingFuelRecordUpdate) => (await client.put<ManufacturingFuelRecord>(`${BASE}/${id}`, data)).data,
  remove: async (id: number) => { await client.delete(`${BASE}/${id}`); },
};
export default manufacturingFuelsApi;
