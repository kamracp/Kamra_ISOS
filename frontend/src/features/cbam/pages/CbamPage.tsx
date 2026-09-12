import { useState } from "react";
import { Download, Pencil, Plus, Trash2 } from "lucide-react";
import { BTN, BTN2 } from "../../lca/components/ProductForm";
import GoodForm from "../components/GoodForm";
import { GOODS_CATEGORIES, type CbamGood, type CbamGoodCreate } from "../api/cbamApi";
import { useCbamGoods, useCreateGood, useDeleteGood, useDownloadTemplate, useUpdateGood } from "../hooks/useCbam";

// Null renders as "-", never 0: a good whose SEE cannot be computed must stay visibly pending.
const fmt = (v: number | null | undefined, d = 4) => (v == null ? "-" : v.toLocaleString(undefined, { maximumFractionDigits: d }));
const catLabel = (c: string) => GOODS_CATEGORIES.find((x) => x.value === c)?.label.split(" (")[0] ?? c;
const STATUS_CLS: Record<string, string> = {
  calculated: "bg-emerald-100 text-emerald-700", no_lca: "bg-amber-100 text-amber-700",
  fu_not_mass: "bg-red-100 text-red-700", lca_unresolved: "bg-red-100 text-red-700", pending: "bg-gray-100 text-gray-600",
};
const Card = ({ label, value, unit, note }: { label: string; value: string; unit: string; note?: string }) => (
  <div className="rounded-lg border border-gray-200 bg-white p-4">
    <div className="text-xs text-gray-500">{label}</div>
    <div className="text-2xl font-semibold text-gray-900">{value}</div>
    <div className="text-xs text-gray-500">{unit}</div>
    {note && <div className="mt-1 text-xs text-amber-700">{note}</div>}
  </div>
);

export default function CbamPage() {
  const [year, setYear] = useState<string>("");
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [mode, setMode] = useState<"none" | "create" | "edit">("none");
  const { data: goods = [], isLoading } = useCbamGoods(year ? Number(year) : undefined);
  const create = useCreateGood(); const update = useUpdateGood(); const remove = useDeleteGood();
  const download = useDownloadTemplate();
  const good: CbamGood | undefined = goods.find((g) => g.id === selectedId);
  const years = Array.from(new Set(goods.map((g) => g.reporting_year))).sort();

  const submit = (d: CbamGoodCreate) => {
    if (mode === "edit" && good) update.mutate({ id: good.id, data: d }, { onSuccess: () => setMode("none") });
    else create.mutate(d, { onSuccess: (g) => { setSelectedId((g as CbamGood).id); setMode("none"); } });
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">CBAM (EU) - embedded emissions</h1>
          <p className="text-sm text-gray-500">Specific embedded emissions (SEE) per tonne from the LCA inventory: direct (fuel, process, precursors), indirect (electricity). Annex II goods report indirect but do not count it.</p>
        </div>
        <div className="flex gap-2">
          <select className="rounded-md border border-gray-300 px-3 py-2 text-sm" value={year} onChange={(e) => setYear(e.target.value)}>
            <option value="">All years</option>{years.map((y) => <option key={y} value={y}>{y}</option>)}
          </select>
          <button className={BTN2} disabled={!year || download.isPending} onClick={() => download.mutate(Number(year))} title={year ? "" : "Pick a year first"}>
            <Download className="mr-1 inline h-4 w-4" />{download.isPending ? "Building..." : "Operator template (XLSX)"}
          </button>
          <button className={BTN} onClick={() => { setMode("create"); }}><Plus className="mr-1 inline h-4 w-4" />New good</button>
        </div>
      </div>

      {mode === "create" && <GoodForm loading={create.isPending} onSubmit={submit} onCancel={() => setMode("none")} />}
      {mode === "edit" && good && <GoodForm initial={good} loading={update.isPending} onSubmit={submit} onCancel={() => setMode("none")} />}

      <div className="grid gap-4 lg:grid-cols-3">
        <div className="space-y-2">
          {isLoading && <div className="text-sm text-gray-500">Loading...</div>}
          {!isLoading && goods.length === 0 && <div className="rounded-lg border border-dashed border-gray-300 p-6 text-sm text-gray-500">No CBAM goods yet. Create one and link it to an LCA product with a mass functional unit.</div>}
          {goods.map((g) => (
            <button key={g.id} onClick={() => { setSelectedId(g.id); setMode("none"); }}
              className={`w-full rounded-lg border bg-white p-4 text-left ${g.id === selectedId ? "border-emerald-500 ring-1 ring-emerald-500" : "border-gray-200"}`}>
              <div className="flex items-center justify-between">
                <div className="font-medium text-gray-900">{g.name}</div>
                <span className={`rounded px-2 py-0.5 text-xs ${STATUS_CLS[g.status] ?? STATUS_CLS.pending}`}>{g.status}</span>
              </div>
              <div className="text-xs text-gray-500">CN {g.cn_code} · {catLabel(g.goods_category)} · {g.reporting_year}</div>
              <div className="mt-1 text-sm"><span className="font-semibold">{fmt(g.see_total_tco2e_per_t)}</span> tCO2e / t</div>
            </button>
          ))}
        </div>

        <div className="lg:col-span-2 space-y-4">
          {!good && <div className="rounded-lg border border-gray-200 bg-white p-8 text-center text-gray-500">Select a good to see its SEE breakdown.</div>}
          {good && (<>
            <div className="rounded-lg border border-gray-200 bg-white p-5">
              <div className="flex items-start justify-between">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">{good.name}</h2>
                  <div className="text-sm text-gray-500">CN {good.cn_code} · {catLabel(good.goods_category)}{good.production_route ? ` · ${good.production_route}` : ""} · {good.reporting_year} · {fmt(good.production_qty_tonne, 0)} t produced</div>
                  {good.status_reason && <div className={`mt-2 text-sm ${good.status === "calculated" ? "text-amber-700" : "text-red-700"}`}>{good.status_reason}</div>}
                </div>
                <div className="flex gap-2">
                  <button className={BTN2} onClick={() => setMode("edit")}><Pencil className="h-4 w-4" /></button>
                  <button className={BTN2} onClick={() => { if (confirm(`Delete ${good.name}?`)) remove.mutate(good.id, { onSuccess: () => setSelectedId(null) }); }}><Trash2 className="h-4 w-4 text-red-600" /></button>
                </div>
              </div>
              <div className="mt-4 grid gap-3 md:grid-cols-4">
                <Card label="SEE direct" value={fmt(good.see_direct_tco2e_per_t)} unit="tCO2e per tonne" />
                <Card label={good.indirect_required ? "SEE indirect (counted)" : "SEE indirect (reported only)"} value={fmt(good.see_indirect_tco2e_per_t)} unit="tCO2e per tonne"
                  note={good.indirect_required ? undefined : "Annex II good: excluded from total"} />
                <Card label="SEE total" value={fmt(good.see_total_tco2e_per_t)} unit="tCO2e per tonne" />
                <Card label="Total embedded (year)" value={fmt(good.total_embedded_tco2e, 1)} unit="tCO2e for production" />
              </div>
            </div>

            {good.precursors.length > 0 && (
              <div className="rounded-lg border border-gray-200 bg-white p-5">
                <h3 className="mb-2 font-semibold text-gray-800">Precursors counted (Annex IV)</h3>
                <table className="w-full text-sm"><thead className="text-left text-xs text-gray-500"><tr><th>Item</th><th>Precursor good</th><th className="text-right">t / t</th><th className="text-right">SEE direct</th><th className="text-right">SEE indirect</th><th className="text-right">kg direct / t</th></tr></thead>
                  <tbody>{good.precursors.map((p) => <tr key={p.item_name} className="border-t"><td>{p.item_name}</td><td>{p.precursor_name} <span className="text-xs text-gray-500">CN {p.cn_code}</span></td><td className="text-right">{fmt(p.tonne_per_fu)}</td><td className="text-right">{fmt(p.see_direct_tco2e_per_t)}</td><td className="text-right">{fmt(p.see_indirect_tco2e_per_t)}</td><td className="text-right">{fmt(p.direct_kg_per_fu, 2)}</td></tr>)}</tbody></table>
              </div>
            )}

            {good.excluded_items.length > 0 && (
              <div className="rounded-lg border border-amber-200 bg-amber-50 p-5">
                <h3 className="mb-2 font-semibold text-amber-800">Outside CBAM boundary / not counted</h3>
                <ul className="list-disc pl-5 text-sm text-amber-900">{good.excluded_items.map((x) => <li key={x}>{x}</li>)}</ul>
                <p className="mt-2 text-xs text-amber-800">Set the item's CBAM bucket in the LCA inventory to override the default rule or to link a precursor.</p>
              </div>
            )}

            {good.factor_sources.length > 0 && (
              <div className="text-xs text-gray-500">Factor sources: {good.factor_sources.join(" | ")}</div>
            )}
          </>)}
        </div>
      </div>
    </div>
  );
}
