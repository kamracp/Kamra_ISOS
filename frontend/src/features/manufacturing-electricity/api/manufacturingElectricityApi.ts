import client from "../../../services/api/client";

export interface ManufacturingElectricityRecord {
  id: number;
  organization_id: number;
  manufacturing_unit_id: number;
  period_start: string;
  period_end: string;
  electricity_consumed_kwh: number;
  renewable_kwh: number;
  source?: string;
  remarks?: string;
  scope2_co2e_kg?: number | null;
  grid_factor_kgco2e_per_kwh?: number | null;
  grid_factor_source?: string | null;
  created_at: string;
  updated_at: string;
}

export interface ManufacturingElectricityRecordCreate {
  manufacturing_unit_id: number;
  period_start: string;
  period_end: string;
  electricity_consumed_kwh: number;
  renewable_kwh?: number;
  source?: string;
  remarks?: string;
}

export interface ManufacturingElectricityRecordUpdate {
  period_start?: string;
  period_end?: string;
  electricity_consumed_kwh?: number;
  renewable_kwh?: number;
  source?: string;
  remarks?: string;
}

export const manufacturingElectricityApi = {
  getAll: async (year?: number): Promise<ManufacturingElectricityRecord[]> => {
    const response = await client.get<ManufacturingElectricityRecord[]>(
      "/manufacturing-electricity-records/",
      { params: year ? { year } : undefined }
    );
    return response.data;
  },
  getByUnit: async (unitId: number, year?: number): Promise<ManufacturingElectricityRecord[]> => {
    const response = await client.get<ManufacturingElectricityRecord[]>(
      `/manufacturing-electricity-records/by-unit/${unitId}`,
      { params: year ? { year } : undefined }
    );
    return response.data;
  },
  getById: async (id: number): Promise<ManufacturingElectricityRecord> => {
    const response = await client.get<ManufacturingElectricityRecord>(`/manufacturing-electricity-records/${id}`);
    return response.data;
  },
  create: async (data: ManufacturingElectricityRecordCreate): Promise<ManufacturingElectricityRecord> => {
    const response = await client.post<ManufacturingElectricityRecord>("/manufacturing-electricity-records/", data);
    return response.data;
  },
  update: async (id: number, data: ManufacturingElectricityRecordUpdate): Promise<ManufacturingElectricityRecord> => {
    const response = await client.put<ManufacturingElectricityRecord>(`/manufacturing-electricity-records/${id}`, data);
    return response.data;
  },
  remove: async (id: number): Promise<void> => {
    await client.delete(`/manufacturing-electricity-records/${id}`);
  },
};

export default manufacturingElectricityApi;
