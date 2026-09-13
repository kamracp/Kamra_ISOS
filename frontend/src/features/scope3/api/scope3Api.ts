import client from "../../../services/api/client";

export type CategoryBasis = "derived" | "entered" | "not_tracked";

export interface Scope3Line {
  source: string; period?: string; quantity: number; unit: string;
  factor_value: number; factor_unit: string; factor_citation: string; tco2e: number;
}
export interface Scope3Category {
  category: number; name: string; basis: CategoryBasis;
  status: "calculated" | "partial" | "not_computed" | "not_tracked";
  status_reason: string | null; tco2e: number | null; lines: Scope3Line[]; gaps: string[];
}
export interface Scope3Summary {
  year: number; total_tco2e: number | null; computed_categories: number;
  categories: Scope3Category[]; factor_sources: string[];
}
export interface Scope3Record {
  id: number; manufacturing_unit_id?: number | null; year: number; category: number; description: string;
  quantity: number; unit: string; emission_factor_id: number; data_source?: string | null; remarks?: string | null;
  status: string; status_reason: string | null; factor_value: number | null; factor_unit: string | null;
  factor_citation: string | null; tco2e: number | null;
}
export interface Scope3RecordCreate {
  manufacturing_unit_id?: number | null; year: number; category: number; description: string;
  quantity: number; unit: string; emission_factor_id: number; data_source?: string | null; remarks?: string | null;
}
export type Scope3RecordUpdate = Partial<Scope3RecordCreate>;

// Which emission_factors meter_type prefixes an entered category may use (session 1: cat 4).
export const CATEGORY_FACTOR_PREFIX: Record<number, string[]> = { 1: ["mat_"], 4: ["freight_"], 9: ["freight_"] };

export const scope3Api = {
  summary: async (year: number): Promise<Scope3Summary> => (await client.get("/scope3/summary", { params: { year } })).data,
  records: async (year?: number, category?: number): Promise<Scope3Record[]> =>
    (await client.get("/scope3/records/", { params: { year, category } })).data,
  create: async (d: Scope3RecordCreate): Promise<Scope3Record> => (await client.post("/scope3/records/", d)).data,
  update: async (id: number, d: Scope3RecordUpdate): Promise<Scope3Record> => (await client.put(`/scope3/records/${id}`, d)).data,
  remove: async (id: number): Promise<void> => { await client.delete(`/scope3/records/${id}`); },
};
