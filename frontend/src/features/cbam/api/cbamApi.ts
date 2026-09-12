import client from "../../../services/api/client";

export type GoodsCategory = "cement" | "iron_steel" | "aluminium" | "fertilisers" | "hydrogen" | "electricity";
export type CbamStatus = "pending" | "calculated" | "no_lca" | "fu_not_mass" | "lca_unresolved";

export const GOODS_CATEGORIES: { value: GoodsCategory; label: string }[] = [
  { value: "cement", label: "Cement (Annex I)" },
  { value: "iron_steel", label: "Iron & steel (Annex II: indirect not counted)" },
  { value: "aluminium", label: "Aluminium (Annex II: indirect not counted)" },
  { value: "fertilisers", label: "Fertilisers (Annex I)" },
  { value: "hydrogen", label: "Hydrogen (Annex II: indirect not counted)" },
  { value: "electricity", label: "Electricity (Annex I)" },
];

export interface CbamPrecursor {
  item_name: string; precursor_good_id: number; precursor_name: string; cn_code: string;
  tonne_per_fu: number; see_direct_tco2e_per_t: number; see_indirect_tco2e_per_t: number;
  direct_kg_per_fu: number; indirect_kg_per_fu: number;
}

export interface CbamGood {
  id: number; name: string; cn_code: string; goods_category: GoodsCategory;
  production_route?: string | null; reporting_year: number; production_qty_tonne: number;
  carbon_price_paid_per_tco2e?: number | null; lca_product_id?: number | null;
  manufacturing_unit_id?: number | null; remarks?: string | null;
  // engine output (read-only)
  indirect_required: boolean; status: CbamStatus; status_reason: string | null;
  see_direct_tco2e_per_t: number | null; see_indirect_tco2e_per_t: number | null;
  see_total_tco2e_per_t: number | null; total_embedded_tco2e: number | null;
  excluded_items: string[]; precursors: CbamPrecursor[]; factor_sources: string[];
}

export interface CbamGoodCreate {
  name: string; cn_code: string; goods_category: GoodsCategory; production_route?: string | null;
  reporting_year: number; production_qty_tonne: number; carbon_price_paid_per_tco2e?: number | null;
  lca_product_id?: number | null; manufacturing_unit_id?: number | null; remarks?: string | null;
}
export type CbamGoodUpdate = Partial<CbamGoodCreate>;

const base = "/cbam/goods";

export const cbamApi = {
  list: async (year?: number): Promise<CbamGood[]> =>
    (await client.get(`${base}/`, { params: year ? { year } : undefined })).data,
  get: async (id: number): Promise<CbamGood> => (await client.get(`${base}/${id}`)).data,
  create: async (d: CbamGoodCreate): Promise<CbamGood> => (await client.post(`${base}/`, d)).data,
  update: async (id: number, d: CbamGoodUpdate): Promise<CbamGood> => (await client.put(`${base}/${id}`, d)).data,
  remove: async (id: number): Promise<void> => { await client.delete(`${base}/${id}`); },
  // Operator communication template (XLSX) -- endpoint lands later this session.
  downloadTemplate: async (year: number): Promise<Blob> =>
    (await client.get(`/cbam/export/operator-template`, { params: { year }, responseType: "blob" })).data,
};
