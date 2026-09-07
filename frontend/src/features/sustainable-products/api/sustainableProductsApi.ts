import client from "../../../services/api/client";

// Must match ReclaimCategory Literal in the backend schema and the DB CHECK.
export type ReclaimCategory = "plastics" | "e_waste" | "hazardous" | "other";

export const RECLAIM_CATEGORY_LABELS: Record<ReclaimCategory, string> = {
  plastics: "Plastics (including packaging)",
  e_waste: "E-waste",
  hazardous: "Hazardous waste",
  other: "Other waste",
};

export interface ReclaimedMaterial {
  id: number;
  sustainable_product_record_id: number;
  material_category: ReclaimCategory;
  reused_mt?: number | null;
  recycled_mt?: number | null;
  disposed_mt?: number | null;
  remarks?: string | null;
  created_at: string;
  updated_at?: string | null;
}

export interface ReclaimedMaterialCreate {
  material_category: ReclaimCategory;
  reused_mt?: number | null;
  recycled_mt?: number | null;
  disposed_mt?: number | null;
  remarks?: string | null;
}

export type ReclaimedMaterialUpdate = Partial<ReclaimedMaterialCreate>;

// Scalar disclosure fields shared by create / update / response.
export interface SustainableProductFields {
  rnd_sustainable_percent_current?: number | null;
  rnd_sustainable_percent_previous?: number | null;
  capex_sustainable_percent_current?: number | null;
  capex_sustainable_percent_previous?: number | null;
  rnd_capex_details?: string | null;
  has_sustainable_sourcing_procedure?: boolean | null;
  sustainable_sourcing_percent?: number | null;
  sustainable_sourcing_details?: string | null;
  reclaim_process_plastics?: string | null;
  reclaim_process_e_waste?: string | null;
  reclaim_process_hazardous?: string | null;
  reclaim_process_other?: string | null;
  epr_applicable?: boolean | null;
  epr_plan_in_line?: boolean | null;
  epr_details?: string | null;
  has_conducted_lca?: boolean | null;
  lca_details?: string | null;
  recycled_input_percent?: number | null;
  reclaimed_products_percent_details?: string | null;
  remarks?: string | null;
}

export interface SustainableProductRecord extends SustainableProductFields {
  id: number;
  organization_id: number;
  reporting_year: number;
  reclaimed_materials: ReclaimedMaterial[];
  // Derived by the backend from the child rows; null = nothing disclosed.
  total_reused_mt?: number | null;
  total_recycled_mt?: number | null;
  total_disposed_mt?: number | null;
  created_at: string;
  updated_at?: string | null;
}

export interface SustainableProductRecordCreate extends SustainableProductFields {
  reporting_year: number;
}

export interface SustainableProductRecordUpdate extends SustainableProductFields {
  reporting_year?: number;
}

const BASE = "/sustainable-product-records";

export const sustainableProductsApi = {
  getAll: async (): Promise<SustainableProductRecord[]> => {
    const response = await client.get<SustainableProductRecord[]>(`${BASE}/`);
    return response.data;
  },
  getById: async (id: number): Promise<SustainableProductRecord> => {
    const response = await client.get<SustainableProductRecord>(`${BASE}/${id}`);
    return response.data;
  },
  create: async (data: SustainableProductRecordCreate): Promise<SustainableProductRecord> => {
    const response = await client.post<SustainableProductRecord>(`${BASE}/`, data);
    return response.data;
  },
  update: async (id: number, data: SustainableProductRecordUpdate): Promise<SustainableProductRecord> => {
    const response = await client.put<SustainableProductRecord>(`${BASE}/${id}`, data);
    return response.data;
  },
  remove: async (id: number): Promise<void> => {
    await client.delete(`${BASE}/${id}`);
  },
  createMaterial: async (recordId: number, data: ReclaimedMaterialCreate): Promise<ReclaimedMaterial> => {
    const response = await client.post<ReclaimedMaterial>(`${BASE}/${recordId}/materials`, data);
    return response.data;
  },
  updateMaterial: async (materialId: number, data: ReclaimedMaterialUpdate): Promise<ReclaimedMaterial> => {
    const response = await client.put<ReclaimedMaterial>(`${BASE}/materials/${materialId}`, data);
    return response.data;
  },
  removeMaterial: async (materialId: number): Promise<void> => {
    await client.delete(`${BASE}/materials/${materialId}`);
  },
};

export default sustainableProductsApi;
