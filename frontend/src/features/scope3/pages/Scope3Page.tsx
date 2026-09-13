import { useState, type ChangeEvent } from "react";
import { Plus, Trash2 } from "lucide-react";
import { BTN, BTN2, INPUT, LABEL } from "../../lca/components/ProductForm";
import { useEmissionFactorOptions } from "../../lca/hooks/useLca";
import { CATEGORY_FACTOR_PREFIX, type Scope3Category, type Scope3RecordCreate } from "../api/scope3Api";
import { useCreateScope3Record, useDeleteScope3Record, useScope3Records, useScope3Summary } from "../hooks/useScope3";

// Null renders as "-", never 0: a category that cannot be computed must stay visibly not computed.
const fmt = (v: number | null | undefined, d = 3) => (v == null ? "-" : v.toLocaleString(undefined, { maximumFractionDigits: d }));
const STATUS_CLS: Record<string, string> = {
  calculated: "bg-emerald-100 text-emerald-700", partial: "bg-amber-100 text-amber-700",
  not_computed: "bg-red-100 text-red-700", not_tracked: "bg-gray-100 text-gray-500",
};
const YEARS = Array.from({ length: 7 }, (_, i) => new Date().getFullYear() - 4 + i);

function RecordForm({ year, category, onDone }: { year: number; category: number; onDone: () => void }) {
  const { data: factors = [] } = useEmissionFactorOptions();
  const create = useCreateScope3Record();
  const prefixes = CATEGORY_FACTOR_PREFIX[category] ?? [];
  const options = factors.filter((f) => f.is_active && prefixes.some((p) => f.meter_type.startsWith(p)));
  const [f, setF] = useState({ description: "", quantity: "", emission_factor_id: "", data_source: "" });
  const set = (k: keyof typeof f) => (e: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => setF({ ...f, [k]: e.target.value });
  const chosen = options.find((x) => String(x.id) === f.emission_factor_id);
  const valid = f.description.trim() !== "" && f.quantity !== "" && Number(f.quantity) >= 0 && chosen !== undefined;
  const submit = () => {
    const d: Scope3RecordCreate = { year, category, description: f.description.trim(), quantity: Number(f.quantity),
      unit: chosen!.unit, emission_factor_id: chosen!.id, data_source: f.data_source.trim() || null };
    create.mutate(d, { onSuccess: onDone });
  };
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4 space-y-3">
      <h4 className="font-semibold text-gray-800">Add activity record - category {category}, {year}</h4>
      <div className="grid gap-3 md:grid-cols-2">
        <div><label className={LABEL}>Description *</label><input className={INPUT} placeholder="Clay inbound, Bikaner -> Morbi by road" value={f.description} onChange={set("description")} /></div>
        <div><label className={LABEL}>Emission factor * (DEFRA freight, per tonne.km)</label>
          <select className={INPUT} value={f.emission_factor_id} onChange={set("emission_factor_id")}>
            <option value="">Select factor</option>
            {options.map((o) => <option key={o.id} value={o.id}>{o.meter_type.replace(/^(freight_|mat_)/, "").replace(/_/g, " ")} - {o.factor_kgco2e_per_unit} kgCO2e/{o.unit} ({o.source_year})</option>)}
          </select></div>
        <div><label className={LABEL}>Quantity * {chosen ? `(${chosen.unit})` : ""}</label><input className={INPUT} type="number" min={0} value={f.quantity} onChange={set("quantity")} /></div>
        <div><label className={LABEL}>Data source (LR copies, ERP, invoices)</label><input className={INPUT} value={f.data_source} onChange={set("data_source")} /></div>
      </div>
      <div className="flex justify-end gap-2">
        <button className={BTN2} onClick={onDone}>Cancel</button>
        <button className={BTN} disabled={!valid || create.isPending} onClick={submit}>{create.isPending ? "Saving..." : "Save"}</button>
      </div>
    </div>
  );
}

export default function Scope3Page() {
  const [year, setYear] = useState<number>(new Date().getFullYear());
  const [selected, setSelected] = useState<number | null>(null);
  const [adding, setAdding] = useState(false);
  const { data: s, isLoading } = useScope3Summary(year);
  const { data: records = [] } = useScope3Records(year, selected ?? undefined);
  const remove = useDeleteScope3Record();
  const cat: Scope3Category | undefined = s?.categories.find((c) => c.category === selected);
  const entered = cat?.basis === "entered";

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Scope 3 - value chain emissions</h1>
          <p className="text-sm text-gray-500">GHG Protocol categories 1-15. Derived categories read existing fuel, electricity and waste records; entered categories use activity records with cited DEFRA factors. Nothing is estimated.</p>
        </div>
        <select className="rounded-md border border-gray-300 px-3 py-2 text-sm" value={year} onChange={(e) => { setYear(Number(e.target.value)); setSelected(null); }}>
          {YEARS.map((y) => <option key={y} value={y}>{y}</option>)}
        </select>
      </div>

      <div className="grid gap-3 md:grid-cols-3">
        <div className="rounded-lg border border-gray-200 bg-white p-4"><div className="text-xs text-gray-500">Scope 3 total (computed categories)</div><div className="text-2xl font-semibold">{fmt(s?.total_tco2e)}</div><div className="text-xs text-gray-500">tCO2e in {year}</div></div>
        <div className="rounded-lg border border-gray-200 bg-white p-4"><div className="text-xs text-gray-500">Categories computed</div><div className="text-2xl font-semibold">{s ? `${s.computed_categories} / 15` : "-"}</div></div>
        <div className="rounded-lg border border-gray-200 bg-white p-4"><div className="text-xs text-gray-500">Factor sources used</div><div className="text-2xl font-semibold">{s?.factor_sources.length ?? "-"}</div></div>
      </div>

      <div className="grid gap-4 lg:grid-cols-5">
        <div className="lg:col-span-2 overflow-hidden rounded-lg border border-gray-200 bg-white">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-left text-xs text-gray-500"><tr><th className="p-2">#</th><th className="p-2">Category</th><th className="p-2">Basis</th><th className="p-2 text-right">tCO2e</th><th className="p-2">Status</th></tr></thead>
            <tbody>
              {isLoading && <tr><td className="p-3 text-gray-500" colSpan={5}>Loading...</td></tr>}
              {s?.categories.map((c) => (
                <tr key={c.category} onClick={() => { setSelected(c.category); setAdding(false); }}
                  className={`cursor-pointer border-t ${c.category === selected ? "bg-emerald-50" : "hover:bg-gray-50"}`}>
                  <td className="p-2 text-gray-500">{c.category}</td><td className="p-2">{c.name}</td>
                  <td className="p-2 text-xs text-gray-500">{c.basis.replace("_", " ")}</td>
                  <td className="p-2 text-right font-medium">{fmt(c.tco2e)}</td>
                  <td className="p-2"><span className={`rounded px-2 py-0.5 text-xs ${STATUS_CLS[c.status]}`}>{c.status.replace("_", " ")}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="lg:col-span-3 space-y-4">
          {!cat && <div className="rounded-lg border border-gray-200 bg-white p-8 text-center text-gray-500">Select a category to see its lines, gaps and records.</div>}
          {cat && (<>
            <div className="rounded-lg border border-gray-200 bg-white p-5">
              <div className="flex items-start justify-between">
                <div><h2 className="text-lg font-semibold text-gray-900">{cat.category}. {cat.name}</h2>
                  <div className="text-sm text-gray-500">{cat.basis === "derived" ? "Derived from existing records" : cat.basis === "entered" ? "Entered activity records" : "Not tracked on the platform yet"}{cat.status_reason ? ` · ${cat.status_reason}` : ""}</div></div>
                {entered && !adding && <button className={BTN} onClick={() => setAdding(true)}><Plus className="mr-1 inline h-4 w-4" />Add record</button>}
              </div>
              {cat.lines.length > 0 && (
                <table className="mt-3 w-full text-sm"><thead className="text-left text-xs text-gray-500"><tr><th className="px-2">Source</th><th className="px-2 text-right">Quantity</th><th className="px-2">Factor</th><th className="px-2 text-right">tCO2e</th></tr></thead>
                  <tbody>{cat.lines.map((l, i) => <tr key={i} className="border-t align-top"><td className="px-2 py-1">{l.source}{l.period ? <span className="text-xs text-gray-500"> · {l.period}</span> : null}</td><td className="px-2 py-1 text-right">{fmt(l.quantity)} {l.unit}</td><td className="px-2 py-1 text-xs">{l.factor_value} kgCO2e/{l.factor_unit}<br /><span className="text-gray-500">{l.factor_citation}</span></td><td className="px-2 py-1 text-right font-medium">{fmt(l.tco2e)}</td></tr>)}</tbody></table>
              )}
              {cat.gaps.length > 0 && (
                <div className="mt-3 rounded-md border border-amber-200 bg-amber-50 p-3"><div className="text-xs font-semibold text-amber-800">Not computed</div>
                  <ul className="list-disc pl-5 text-xs text-amber-900">{cat.gaps.map((g) => <li key={g}>{g}</li>)}</ul></div>
              )}
            </div>
            {entered && adding && <RecordForm year={year} category={cat.category} onDone={() => setAdding(false)} />}
            {entered && records.length > 0 && (
              <div className="rounded-lg border border-gray-200 bg-white p-5">
                <h3 className="mb-2 font-semibold text-gray-800">Activity records</h3>
                <table className="w-full text-sm"><thead className="text-left text-xs text-gray-500"><tr><th className="px-2">Description</th><th className="px-2 text-right">Quantity</th><th className="px-2">Factor</th><th className="px-2 text-right">tCO2e</th><th className="px-2">Status</th><th className="px-2"></th></tr></thead>
                  <tbody>{records.map((r) => <tr key={r.id} className="border-t"><td className="px-2 py-1">{r.description}{r.data_source ? <span className="text-xs text-gray-500"> · {r.data_source}</span> : null}</td><td className="px-2 py-1 text-right">{fmt(r.quantity)} {r.unit}</td><td className="px-2 py-1 text-xs">{r.factor_value} kgCO2e/{r.factor_unit}</td><td className="px-2 py-1 text-right font-medium">{fmt(r.tco2e)}</td><td className="px-2 py-1"><span className={`rounded px-2 py-0.5 text-xs ${STATUS_CLS[r.status] ?? "bg-gray-100"}`}>{r.status}</span></td>
                    <td className="px-2 py-1 text-right"><button onClick={() => { if (confirm("Delete record?")) remove.mutate(r.id); }}><Trash2 className="h-4 w-4 text-red-600" /></button></td></tr>)}</tbody></table>
              </div>
            )}
          </>)}
        </div>
      </div>
    </div>
  );
}
