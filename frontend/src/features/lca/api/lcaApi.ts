import client from "../../../services/api/client";

export type LcaStage = "raw_materials" | "inbound_transport" | "manufacturing" | "packaging" | "outbound_transport";
export type FactorSource = "fuel" | "electricity" | "factor";
export type QuantityBasis = "per_functional_unit" | "annual_total";
export type SystemBoundary = "cradle_to_gate" | "gate_to_gate" | "cradle_to_grave";

export const LCA_STAGES: { value: LcaStage; label: string }[] = [
  { value: "raw_materials", label: "Raw materials (A1)" },
  { value: "inbound_transport", label: "Inbound transport (A2)" },
  { value: "manufacturing", label: "Manufacturing (A3)" },
  { value: "packaging", label: "Packaging" },
  { value: "outbound_transport", label: "Outbound transport (A4)" },
];

export interface LcaItem {
  id: number; product_id: number; organization_id: number;
  name: string; stage: LcaStage; factor_source: FactorSource;
  fuel_key?: string | null; country_code?: string | null; emission_factor_id?: number | null;
  quantity: number; unit: string; basis: QuantityBasis;
  data_source?: string | null; remarks?: string | null;
  // Computed server-side at read time - never sent back.
  status: string; quantity_per_fu?: number | null; factor_value?: number | null;
  factor_unit?: string | null; factor_citation?: string | null; is_biogenic: boolean;
  co2e_kg_per_fu?: number | null; biogenic_co2_kg_per_fu?: number | null;
}
export interface LcaItemCreate {
  name: string; stage: LcaStage; factor_source: FactorSource;
  fuel_key?: string | null; country_code?: string | null; emission_factor_id?: number | null;
  quantity: number; unit: string; basis: QuantityBasis; data_source?: string | null; remarks?: string | null;
}
export type LcaItemUpdate = Partial<LcaItemCreate>;

export interface LcaStageTotal { stage: LcaStage; item_count: number; co2e_kg_per_fu: number | null; share_percent: number | null; }

export interface LcaProductSummary {
  id: number; organization_id: number; manufacturing_unit_id?: number | null;
  name: string; product_code?: string | null; description?: string | null;
  functional_unit_qty: number; functional_unit: string; system_boundary: SystemBoundary;
  reference_year?: number | null; annual_output_qty?: number | null; production_country_code: string;
  remarks?: string | null; item_count: number; unresolved_count: number; gwp_kgco2e_per_fu: number | null;
}
export interface LcaProduct extends LcaProductSummary {
  items: LcaItem[]; by_stage: LcaStageTotal[]; biogenic_co2_kg_per_fu: number | null; factor_sources: string[];
}
export interface LcaProductCreate {
  name: string; product_code?: string | null; description?: string | null;
  functional_unit_qty: number; functional_unit: string; system_boundary: SystemBoundary;
  reference_year?: number | null; annual_output_qty?: number | null; production_country_code: string;
  manufacturing_unit_id?: number | null; remarks?: string | null;
}
export type LcaProductUpdate = Partial<LcaProductCreate>;

export interface FuelLibraryEntry { key: string; name: string; [k: string]: unknown; }
export interface EmissionFactorOption {
  id: number; meter_type: string; unit: string; factor_kgco2e_per_unit: number;
  region: string; source: string; source_year: number; is_active: boolean;
}

export const lcaApi = {
  list: async (): Promise<LcaProductSummary[]> => (await client.get<LcaProductSummary[]>("/lca-products/")).data,
  get: async (id: number): Promise<LcaProduct> => (await client.get<LcaProduct>(`/lca-products/${id}`)).data,
  create: async (data: LcaProductCreate): Promise<LcaProduct> => (await client.post<LcaProduct>("/lca-products/", data)).data,
  update: async (id: number, data: LcaProductUpdate): Promise<LcaProduct> => (await client.put<LcaProduct>(`/lca-products/${id}`, data)).data,
  remove: async (id: number): Promise<void> => { await client.delete(`/lca-products/${id}`); },
  addItem: async (pid: number, data: LcaItemCreate): Promise<LcaProduct> => (await client.post<LcaProduct>(`/lca-products/${pid}/items`, data)).data,
  updateItem: async (pid: number, itemId: number, data: LcaItemUpdate): Promise<LcaProduct> => (await client.put<LcaProduct>(`/lca-products/${pid}/items/${itemId}`, data)).data,
  removeItem: async (pid: number, itemId: number): Promise<void> => { await client.delete(`/lca-products/${pid}/items/${itemId}`); },
  fuelLibrary: async (): Promise<FuelLibraryEntry[]> => (await client.get<FuelLibraryEntry[]>("/manufacturing-fuel-records/library")).data,
  emissionFactors: async (): Promise<EmissionFactorOption[]> => (await client.get<EmissionFactorOption[]>("/emission-factors/")).data,
  downloadOpenLca: async (pid: number, name: string): Promise<void> => {
    const response = await client.get(`/lca-products/${pid}/export/openlca`, { responseType: "blob" });
    const url = window.URL.createObjectURL(new Blob([response.data], { type: "application/zip" }));
    const link = document.createElement("a");
    link.href = url;
    link.download = `${name.replace(/[^a-z0-9]+/gi, "_")}_openlca_jsonld.zip`;
    document.body.appendChild(link); link.click(); link.remove();
    window.URL.revokeObjectURL(url);
  },
};
