import client from "../../../services/api/client";

/** Volumes in kilolitres (KL). */
export interface WaterRecord {
  id: number;
  organization_id: number;
  manufacturing_unit_id?: number | null;
  building_id?: number | null;
  period_start: string;
  period_end: string;
  is_water_stressed_area: boolean;

  withdrawal_surface_water?: string | null;
  withdrawal_groundwater?: string | null;
  withdrawal_third_party?: string | null;
  withdrawal_seawater_desalinated?: string | null;
  withdrawal_others?: string | null;

  discharge_surface_water?: string | null;
  discharge_groundwater?: string | null;
  discharge_seawater?: string | null;
  discharge_third_party?: string | null;
  discharge_others?: string | null;

  discharge_treatment_level?: string | null;
  has_zero_liquid_discharge?: boolean | null;
  remarks?: string | null;

  // Derived server-side from withdrawal minus discharge - never sent.
  total_withdrawal?: string | null;
  total_discharge?: string | null;
  total_consumption?: string | null;
}

/** Quantities in metric tonnes (MT). */
export interface WasteRecord {
  id: number;
  organization_id: number;
  manufacturing_unit_id?: number | null;
  building_id?: number | null;
  period_start: string;
  period_end: string;

  plastic_waste?: string | null;
  e_waste?: string | null;
  bio_medical_waste?: string | null;
  construction_demolition_waste?: string | null;
  battery_waste?: string | null;
  radioactive_waste?: string | null;
  other_hazardous_waste?: string | null;
  other_non_hazardous_waste?: string | null;

  recycled?: string | null;
  reused?: string | null;
  other_recovery?: string | null;

  incineration?: string | null;
  landfilling?: string | null;
  other_disposal?: string | null;

  waste_management_practices?: string | null;
  remarks?: string | null;

  // Derived server-side - never sent.
  total_generated?: string | null;
  total_recovered?: string | null;
  total_disposed?: string | null;
  hazardous_generated?: string | null;
}

const WATER_DERIVED = ["id", "organization_id", "total_withdrawal", "total_discharge", "total_consumption"] as const;
const WASTE_DERIVED = ["id", "organization_id", "total_generated", "total_recovered", "total_disposed", "hazardous_generated"] as const;

export type WaterRecordCreate = Omit<WaterRecord, (typeof WATER_DERIVED)[number]>;
export type WasteRecordCreate = Omit<WasteRecord, (typeof WASTE_DERIVED)[number]>;

// Edits send only what changed; the backend applies exclude_unset.
export type WaterRecordUpdate = Partial<WaterRecordCreate>;
export type WasteRecordUpdate = Partial<WasteRecordCreate>;

export interface WaterWasteSummary {
  organization_id: number;
  year: number | null;
  water: {
    record_count: number;
    total_withdrawal_kl: string | null;
    total_discharge_kl: string | null;
    total_consumption_kl: string | null;
    water_stressed_records: number;
  };
  waste: {
    record_count: number;
    total_generated_mt: string | null;
    hazardous_generated_mt: string | null;
    total_recovered_mt: string | null;
    total_disposed_mt: string | null;
  };
}

export const waterWasteApi = {
  getSummary: async (year?: number): Promise<WaterWasteSummary> => {
    const response = await client.get<WaterWasteSummary>("/water-waste/summary", {
      params: year ? { year } : undefined,
    });
    return response.data;
  },
  getWater: async (year?: number): Promise<WaterRecord[]> => {
    const response = await client.get<WaterRecord[]>("/water-waste/water", {
      params: year ? { year } : undefined,
    });
    return response.data;
  },
  createWater: async (data: WaterRecordCreate): Promise<WaterRecord> => {
    const response = await client.post<WaterRecord>("/water-waste/water", data);
    return response.data;
  },
  updateWater: async (
    id: number,
    data: WaterRecordUpdate
  ): Promise<WaterRecord> => {
    const response = await client.put<WaterRecord>(
      `/water-waste/water/${id}`,
      data
    );
    return response.data;
  },
  removeWater: async (id: number): Promise<void> => {
    await client.delete(`/water-waste/water/${id}`);
  },
  getWaste: async (year?: number): Promise<WasteRecord[]> => {
    const response = await client.get<WasteRecord[]>("/water-waste/waste", {
      params: year ? { year } : undefined,
    });
    return response.data;
  },
  createWaste: async (data: WasteRecordCreate): Promise<WasteRecord> => {
    const response = await client.post<WasteRecord>("/water-waste/waste", data);
    return response.data;
  },
  updateWaste: async (
    id: number,
    data: WasteRecordUpdate
  ): Promise<WasteRecord> => {
    const response = await client.put<WasteRecord>(
      `/water-waste/waste/${id}`,
      data
    );
    return response.data;
  },
  removeWaste: async (id: number): Promise<void> => {
    await client.delete(`/water-waste/waste/${id}`);
  },
};
