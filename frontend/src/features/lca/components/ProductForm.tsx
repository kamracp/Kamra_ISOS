import { useState, type ChangeEvent } from "react";
import type { LcaProductCreate, LcaProductSummary, SystemBoundary } from "../api/lcaApi";
import { useCountryOptions, useBenchmarkOptions } from "../hooks/useLca";

export const INPUT = "w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none";
export const LABEL = "block text-sm font-medium text-gray-700 mb-1";
export const BTN = "rounded-md bg-emerald-600 px-4 py-2 text-sm text-white disabled:opacity-50";
export const BTN2 = "rounded-md border border-gray-300 px-4 py-2 text-sm text-gray-700";

interface Props { initial?: LcaProductSummary | null; loading?: boolean; onSubmit: (d: LcaProductCreate) => void; onCancel: () => void; }

export default function ProductForm({ initial, loading, onSubmit, onCancel }: Props) {
  const { data: countries = [] } = useCountryOptions();
  const { data: benchmarks = [] } = useBenchmarkOptions();
  const [f, setF] = useState({
    name: initial?.name ?? "", product_code: initial?.product_code ?? "", description: initial?.description ?? "",
    functional_unit_qty: String(initial?.functional_unit_qty ?? 1), functional_unit: initial?.functional_unit ?? "",
    system_boundary: (initial?.system_boundary ?? "cradle_to_gate") as SystemBoundary,
    reference_year: String(initial?.reference_year ?? new Date().getFullYear()),
    annual_output_qty: initial?.annual_output_qty != null ? String(initial.annual_output_qty) : "",
    production_country_code: initial?.production_country_code ?? "IN",
    benchmark_key: initial?.benchmark_key ?? "",
    eol_recycling_fraction: initial?.eol_recycling_fraction != null ? String(initial.eol_recycling_fraction) : "",
    eol_reuse_fraction: initial?.eol_reuse_fraction != null ? String(initial.eol_reuse_fraction) : "",
    recycling_efficiency_eol: initial?.recycling_efficiency_eol != null ? String(initial.recycling_efficiency_eol) : "",
    recycling_efficiency_input: initial?.recycling_efficiency_input != null ? String(initial.recycling_efficiency_input) : "",
    lifetime_years: initial?.lifetime_years != null ? String(initial.lifetime_years) : "",
    industry_avg_lifetime_years: initial?.industry_avg_lifetime_years != null ? String(initial.industry_avg_lifetime_years) : "",
  });
  const set = (k: keyof typeof f) => (e: ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) =>
    setF({ ...f, [k]: e.target.value } as typeof f);
  const opt = (s: string) => (s === "" ? null : Number(s));   // blank = not stated, never 0
  const submit = () => onSubmit({
    name: f.name.trim(), product_code: f.product_code.trim() || null, description: f.description.trim() || null,
    functional_unit_qty: Number(f.functional_unit_qty), functional_unit: f.functional_unit.trim(),
    system_boundary: f.system_boundary, reference_year: f.reference_year ? Number(f.reference_year) : null,
    annual_output_qty: f.annual_output_qty ? Number(f.annual_output_qty) : null, production_country_code: f.production_country_code,
    benchmark_key: f.benchmark_key || null, eol_recycling_fraction: opt(f.eol_recycling_fraction), eol_reuse_fraction: opt(f.eol_reuse_fraction), recycling_efficiency_eol: opt(f.recycling_efficiency_eol), recycling_efficiency_input: opt(f.recycling_efficiency_input), lifetime_years: opt(f.lifetime_years), industry_avg_lifetime_years: opt(f.industry_avg_lifetime_years),
  });
  const valid = f.name.trim() !== "" && f.functional_unit.trim() !== "" && Number(f.functional_unit_qty) > 0;
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-5 space-y-3">
      <h3 className="font-semibold text-gray-800">{initial ? "Edit product" : "New product"}</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div><label className={LABEL}>Product name *</label><input className={INPUT} value={f.name} onChange={set("name")} /></div>
        <div><label className={LABEL}>Product code</label><input className={INPUT} value={f.product_code} onChange={set("product_code")} /></div>
        <div><label className={LABEL}>Functional unit qty *</label><input type="number" min="0" step="any" className={INPUT} value={f.functional_unit_qty} onChange={set("functional_unit_qty")} /></div>
        <div><label className={LABEL}>Functional unit (m2, kg, piece) *</label><input className={INPUT} value={f.functional_unit} onChange={set("functional_unit")} /></div>
        <div><label className={LABEL}>System boundary</label>
          <select className={INPUT} value={f.system_boundary} onChange={set("system_boundary")}>
            <option value="cradle_to_gate">Cradle to gate (A1-A3)</option>
            <option value="gate_to_gate">Gate to gate</option>
            <option value="cradle_to_grave">Cradle to grave</option>
          </select></div>
        <div><label className={LABEL}>Production country</label>
          <select className={INPUT} value={f.production_country_code} onChange={set("production_country_code")}>
            {countries.map((c) => <option key={c.code} value={c.code}>{c.name}</option>)}
          </select></div>
        <div><label className={LABEL}>Reference year</label><input type="number" className={INPUT} value={f.reference_year} onChange={set("reference_year")} /></div>
        <div><label className={LABEL}>Annual output (functional units) - needed for annual-total items</label><input type="number" min="0" step="any" className={INPUT} value={f.annual_output_qty} onChange={set("annual_output_qty")} /></div>
      </div>
      <details className="rounded-md border border-gray-100 p-3">
        <summary className="cursor-pointer text-sm font-medium text-gray-700">Circularity (MCI) and plausibility benchmark - optional; a blank field is "not stated", never assumed</summary>
        <div className="mt-3 grid grid-cols-1 md:grid-cols-3 gap-3">
          <div className="md:col-span-3"><label className={LABEL}>Published benchmark (warning only - never changes the result)</label>
            <select className={INPUT} value={f.benchmark_key} onChange={set("benchmark_key")}><option value="">None</option>
              {benchmarks.map((b) => <option key={b.key} value={b.key}>{b.label} - {b.value_kgco2e_per_fu} kgCO2e/{b.functional_unit}</option>)}</select></div>
          <div><label className={LABEL}>EoL collected for recycling (Cr, 0-1)</label><input type="number" min="0" step="any" className={INPUT} value={f.eol_recycling_fraction} onChange={set("eol_recycling_fraction")} /></div>
          <div><label className={LABEL}>EoL collected for reuse (Cu, 0-1)</label><input type="number" min="0" step="any" className={INPUT} value={f.eol_reuse_fraction} onChange={set("eol_reuse_fraction")} /></div>
          <div><label className={LABEL}>Recycling efficiency at EoL (Ec, 0-1)</label><input type="number" min="0" step="any" className={INPUT} value={f.recycling_efficiency_eol} onChange={set("recycling_efficiency_eol")} /></div>
          <div><label className={LABEL}>Recycling efficiency of recycled feedstock (Ef, 0-1)</label><input type="number" min="0" step="any" className={INPUT} value={f.recycling_efficiency_input} onChange={set("recycling_efficiency_input")} /></div>
          <div><label className={LABEL}>Product lifetime (years, L)</label><input type="number" min="0" step="any" className={INPUT} value={f.lifetime_years} onChange={set("lifetime_years")} /></div>
          <div><label className={LABEL}>Industry-average lifetime (years, Lav)</label><input type="number" min="0" step="any" className={INPUT} value={f.industry_avg_lifetime_years} onChange={set("industry_avg_lifetime_years")} /></div>
        </div>
      </details>
      <div><label className={LABEL}>Description</label><textarea className={INPUT} rows={2} value={f.description} onChange={set("description")} /></div>
      <div className="flex gap-2 justify-end">
        <button className={BTN2} onClick={onCancel}>Cancel</button>
        <button disabled={!valid || loading} className={BTN} onClick={submit}>{loading ? "Saving..." : "Save"}</button>
      </div>
    </div>
  );
}
