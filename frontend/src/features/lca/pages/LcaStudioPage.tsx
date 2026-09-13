import { useState } from "react";
import { Download, Pencil, Plus, Trash2 } from "lucide-react";
import ProductForm, { BTN, BTN2 } from "../components/ProductForm";
import ItemForm from "../components/ItemForm";
import { LCA_STAGES, type LcaItem, type LcaItemCreate, type LcaProductCreate } from "../api/lcaApi";
import { useAddItem, useCreateProduct, useDeleteItem, useDeleteProduct, useDownloadOpenLca, useDownloadPdf,
  useLcaProduct, useLcaProducts, useUpdateItem, useUpdateProduct, useLcaCompare } from "../hooks/useLca";

// Null renders as "-", never 0: an unresolved item must stay visibly unresolved.
const fmt = (v: number | null | undefined, d = 3) => (v == null ? "-" : v.toLocaleString(undefined, { maximumFractionDigits: d }));
const stageLabel = (s: string) => LCA_STAGES.find((x) => x.value === s)?.label ?? s;
const STATUS_CLS: Record<string, string> = {
  calculated: "bg-emerald-100 text-emerald-700", no_factor: "bg-red-100 text-red-700",
  unit_mismatch: "bg-amber-100 text-amber-700", no_annual_output: "bg-amber-100 text-amber-700",
};

export default function LcaStudioPage() {
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [productMode, setProductMode] = useState<"none" | "create" | "edit">("none");
  const [itemMode, setItemMode] = useState<"none" | "create" | LcaItem>("none");
  // Scenario comparison: 2-4 products picked from the list, fetched side by side.
  const [compareIds, setCompareIds] = useState<number[]>([]);
  const toggleCompare = (id: number) => setCompareIds((c) => (c.includes(id) ? c.filter((x) => x !== id) : c.length >= 4 ? c : [...c, id]));
  const { data: products = [], isLoading } = useLcaProducts();
  const { data: cmp } = useLcaCompare(compareIds);
  const { data: product } = useLcaProduct(selectedId);
  const createP = useCreateProduct(); const updateP = useUpdateProduct(); const deleteP = useDeleteProduct();
  const addI = useAddItem(); const updateI = useUpdateItem(); const deleteI = useDeleteItem(); const exportZip = useDownloadOpenLca(); const exportPdf = useDownloadPdf();

  const saveProduct = (d: LcaProductCreate) => {
    if (productMode === "edit" && product) updateP.mutate({ id: product.id, data: d }, { onSuccess: () => setProductMode("none") });
    else createP.mutate(d, { onSuccess: (p) => { setSelectedId(p.id); setProductMode("none"); } });
  };
  const saveItem = (d: LcaItemCreate) => {
    if (!product) return;
    if (itemMode !== "none" && itemMode !== "create") updateI.mutate({ pid: product.id, itemId: itemMode.id, data: d }, { onSuccess: () => setItemMode("none") });
    else addI.mutate({ pid: product.id, data: d }, { onSuccess: () => setItemMode("none") });
  };
  const removeProduct = () => {
    if (product && window.confirm(`Delete "${product.name}" and all its items?`)) deleteP.mutate(product.id, { onSuccess: () => setSelectedId(null) });
  };
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-gray-800">LCA / PCF Studio</h1>
          <p className="text-sm text-gray-500">Cradle-to-gate product carbon footprint. Factors resolved at read time from IPCC / CEA / DEFRA - never typed by hand.</p>
        </div>
        <button className={BTN} onClick={() => { setProductMode("create"); setItemMode("none"); }}><Plus className="inline h-4 w-4 mr-1" />New product</button>
      </div>
      {productMode === "create" && <ProductForm loading={createP.isPending} onSubmit={saveProduct} onCancel={() => setProductMode("none")} />}
      {compareIds.length >= 2 && cmp && cmp.products.length >= 2 && (
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <div className="flex items-center justify-between"><h3 className="font-semibold text-gray-800">Scenario comparison</h3><button className={BTN2} onClick={() => setCompareIds([])}>Clear</button></div>
          <table className="mt-3 w-full text-sm">
            <thead className="bg-gray-50 text-left text-gray-600"><tr><th className="px-3 py-2 font-medium">Metric</th>
              {cmp.products.map((p) => <th key={p.id} className="px-3 py-2 font-medium">{p.name}<div className="text-xs font-normal text-gray-500">per {p.functional_unit_qty} {p.functional_unit}</div></th>)}</tr></thead>
            <tbody>
              <tr className="border-t border-gray-100"><td className="px-3 py-2">GWP (fossil), kgCO2e/FU</td>{cmp.products.map((p) => <td key={p.id} className="px-3 py-2"><span className="font-semibold">{fmt(p.gwp_kgco2e_per_fu)}</span></td>)}</tr>
              <tr className="border-t border-gray-100"><td className="px-3 py-2">Biogenic CO2, kg/FU</td>{cmp.products.map((p) => <td key={p.id} className="px-3 py-2">{fmt(p.biogenic_co2_kg_per_fu)}</td>)}</tr>
              {cmp.products[0].by_stage.map((s) => <tr key={s.stage} className="border-t border-gray-100"><td className="px-3 py-2 text-gray-600">{stageLabel(s.stage)}</td>
                {cmp.products.map((p) => { const st = p.by_stage.find((b) => b.stage === s.stage); return <td key={p.id} className="px-3 py-2">{fmt(st?.co2e_kg_per_fu ?? null)} <span className="text-gray-400">({fmt(st?.share_percent ?? null, 1)}%)</span></td>; })}</tr>)}
              <tr className="border-t border-gray-100"><td className="px-3 py-2">Material Circularity Indicator</td>{cmp.products.map((p) => <td key={p.id} className="px-3 py-2">{p.mci.status === "calculated" ? fmt(p.mci.mci ?? null, 3) : <span className="text-xs text-gray-500">{p.mci.reason}</span>}</td>)}</tr>
              <tr className="border-t border-gray-100"><td className="px-3 py-2">vs published benchmark</td>{cmp.products.map((p) => <td key={p.id} className="px-3 py-2">{p.benchmark?.status === "calculated" ? `${p.benchmark.ratio}x - ${p.benchmark.label}` : <span className="text-xs text-gray-500">{p.benchmark?.reason ?? "no benchmark selected"}</span>}</td>)}</tr>
            </tbody>
          </table>
          {cmp.missing.length > 0 && <p className="mt-2 text-xs text-amber-700">Not found in this organisation: {cmp.missing.join(", ")}</p>}
        </div>)}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="space-y-2">
          {isLoading && <p className="p-5 text-gray-500">Loading...</p>}
          {!isLoading && products.length === 0 && <p className="p-5 text-gray-500 rounded-lg border border-gray-200 bg-white">No products yet. Create one to start an inventory.</p>}
          {products.map((p) => (
            <button key={p.id} onClick={() => { setSelectedId(p.id); setProductMode("none"); setItemMode("none"); }}
              className={`w-full text-left rounded-lg border bg-white p-4 ${p.id === selectedId ? "border-emerald-500 ring-1 ring-emerald-500" : "border-gray-200"}`}>
              <div className="font-medium text-gray-800">{p.name}</div>
              <div className="text-xs text-gray-500">{p.product_code ? `${p.product_code} · ` : ""}per {p.functional_unit_qty} {p.functional_unit} · {p.production_country_code}</div>
              <div className="mt-1 text-sm"><span className="font-semibold">{fmt(p.gwp_kgco2e_per_fu)}</span> kgCO2e/FU
                {p.unresolved_count > 0 && <span className="ml-2 rounded bg-amber-100 px-1.5 text-xs text-amber-700">{p.unresolved_count} unresolved</span>}</div>
              <span className={`mt-1 inline-block text-xs ${compareIds.includes(p.id) ? "text-emerald-700 font-medium" : "text-gray-400"}`}
                onClick={(e) => { e.stopPropagation(); toggleCompare(p.id); }}>{compareIds.includes(p.id) ? "[x] compare" : "[ ] compare"}</span>
            </button>))}
        </div>
        <div className="lg:col-span-2 space-y-4">
          {!product && <p className="p-5 text-gray-500 rounded-lg border border-gray-200 bg-white">Select a product to see its inventory and GWP breakdown.</p>}
          {product && productMode === "edit" && <ProductForm initial={product} loading={updateP.isPending} onSubmit={saveProduct} onCancel={() => setProductMode("none")} />}
          {product && productMode !== "edit" && (<>
            <div className="rounded-lg border border-gray-200 bg-white p-5">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h2 className="text-lg font-semibold text-gray-800">{product.name}</h2>
                  <p className="text-sm text-gray-500">{product.system_boundary.replace(/_/g, " ")} · FU {product.functional_unit_qty} {product.functional_unit} · {product.production_country_code} · {product.reference_year ?? "-"}{product.annual_output_qty ? ` · annual output ${fmt(product.annual_output_qty, 0)} ${product.functional_unit}` : ""}</p>
                </div>
                <div className="flex gap-2 shrink-0">
                  <button className={BTN2} title="Edit product" onClick={() => setProductMode("edit")}><Pencil className="h-4 w-4" /></button>
                  <button className={BTN2} title="Delete product" onClick={removeProduct}><Trash2 className="h-4 w-4 text-red-600" /></button>
                  <button className={BTN2} disabled={exportPdf.isPending} onClick={() => exportPdf.mutate({ pid: product.id, name: product.name })}><Download className="inline h-4 w-4 mr-1" />PLCA PDF</button>
                  <button className={BTN} disabled={exportZip.isPending || product.gwp_kgco2e_per_fu == null} onClick={() => exportZip.mutate({ pid: product.id, name: product.name })}><Download className="inline h-4 w-4 mr-1" />openLCA JSON-LD</button>
                </div>
              </div>
              <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                <div className="rounded-md bg-emerald-50 p-3"><div className="text-xs text-gray-500">GWP (fossil)</div><div className="text-xl font-semibold text-emerald-700">{fmt(product.gwp_kgco2e_per_fu)}</div><div className="text-xs text-gray-500">kgCO2e per {product.functional_unit_qty} {product.functional_unit}</div></div>
                <div className="rounded-md bg-gray-50 p-3"><div className="text-xs text-gray-500">Biogenic CO2 (separate)</div><div className="text-xl font-semibold">{fmt(product.biogenic_co2_kg_per_fu)}</div></div>
                <div className="rounded-md bg-gray-50 p-3"><div className="text-xs text-gray-500">Items</div><div className="text-xl font-semibold">{product.item_count}</div></div>
                <div className="rounded-md bg-gray-50 p-3"><div className="text-xs text-gray-500">Unresolved</div><div className={`text-xl font-semibold ${product.unresolved_count ? "text-amber-600" : ""}`}>{product.unresolved_count}</div></div>
              </div>
              {product.benchmark && (
                <div className={`mt-3 rounded-md p-3 text-sm ${product.benchmark.status !== "calculated" ? "bg-gray-50 text-gray-600" : product.benchmark.warning ? "bg-amber-50 text-amber-800" : "bg-emerald-50 text-emerald-800"}`}>
                  <span className="font-medium">Benchmark:</span> {product.benchmark.label} = {product.benchmark.value_kgco2e_per_fu} kgCO2e/{product.benchmark.functional_unit}
                  {product.benchmark.status === "calculated" ? <> - this product is {product.benchmark.ratio}x. {product.benchmark.warning ?? "Within the 0.5x-2x plausibility band."}</> : <> - not compared: {product.benchmark.reason}</>}
                  <div className="mt-1 text-xs text-gray-500">{product.benchmark.source}{product.benchmark.boundary ? ` | boundary: ${product.benchmark.boundary}` : ""}</div>
                </div>)}
              <div className="mt-3 rounded-md border border-gray-100 p-3 text-sm">
                <div className="flex items-baseline justify-between"><span className="font-medium text-gray-700">Material Circularity Indicator (Ellen MacArthur, mass basis)</span>
                  <span className={`text-xl font-semibold ${product.mci.status === "calculated" ? "text-emerald-700" : "text-gray-400"}`}>{product.mci.status === "calculated" ? fmt(product.mci.mci ?? null, 3) : "-"}</span></div>
                {product.mci.status === "calculated"
                  ? <div className="mt-1 text-xs text-gray-600">M {fmt(product.mci.mass_kg_per_fu)} kg/FU | Fr {product.mci.fr} | Fu {product.mci.fu} | Cr {product.mci.cr} | Cu {product.mci.cu} | LFI {product.mci.lfi} | {product.mci.utility_note}</div>
                  : <div className="mt-1 text-xs text-gray-600">Not computed: {product.mci.reason}</div>}
                {product.mci.items_excluded.length > 0 && <div className="mt-1 text-xs text-gray-500">Excluded from product mass: {product.mci.items_excluded.join("; ")}</div>}
              </div>
              <div className="mt-4 space-y-1">
                {product.by_stage.filter((s) => s.item_count > 0).map((s) => (
                  <div key={s.stage} className="flex items-center gap-2 text-sm">
                    <div className="w-44 text-gray-600">{stageLabel(s.stage)}</div>
                    <div className="flex-1 h-3 rounded bg-gray-100"><div className="h-3 rounded bg-emerald-500" style={{ width: `${s.share_percent ?? 0}%` }} /></div>
                    <div className="w-36 text-right text-gray-700">{fmt(s.co2e_kg_per_fu)} <span className="text-gray-400">({fmt(s.share_percent, 1)}%)</span></div>
                  </div>))}
              </div>
              {product.factor_sources.length > 0 && <p className="mt-3 text-xs text-gray-500">Factor sources: {product.factor_sources.join(" | ")}</p>}
            </div>
            <div className="rounded-lg border border-gray-200 bg-white">
              <div className="flex items-center justify-between p-4 border-b border-gray-100">
                <h3 className="font-semibold text-gray-800">Inventory items</h3>
                <button className={BTN} onClick={() => setItemMode("create")}><Plus className="inline h-4 w-4 mr-1" />Add item</button>
              </div>
              {itemMode !== "none" && <div className="p-4"><ItemForm initial={itemMode === "create" ? null : itemMode} loading={addI.isPending || updateI.isPending} onSubmit={saveItem} onCancel={() => setItemMode("none")} /></div>}
              {product.items.length === 0 ? <p className="p-5 text-gray-500">No items yet.</p> : (
                <table className="w-full text-sm">
                  <thead className="bg-gray-50 text-left text-gray-600"><tr>
                    <th className="px-4 py-3 font-medium">Item</th><th className="px-4 py-3 font-medium">Stage</th><th className="px-4 py-3 font-medium">Qty / FU</th>
                    <th className="px-4 py-3 font-medium">Factor</th><th className="px-4 py-3 font-medium text-right">kgCO2e / FU</th><th className="px-4 py-3 font-medium">Status</th><th className="px-4 py-3" /></tr></thead>
                  <tbody>{product.items.map((i) => (
                    <tr key={i.id} className="border-t border-gray-100">
                      <td className="px-4 py-3"><div className="font-medium text-gray-800">{i.name}</div><div className="text-xs text-gray-500">{i.basis === "annual_total" ? `annual ${fmt(i.quantity, 3)} ${i.unit}` : ""}{i.data_source ? ` · ${i.data_source}` : ""}</div></td>
                      <td className="px-4 py-3">{stageLabel(i.stage)}</td>
                      <td className="px-4 py-3">{fmt(i.quantity_per_fu, 6)} {i.unit}</td>
                      <td className="px-4 py-3"><div>{fmt(i.factor_value, 5)} {i.factor_unit ? `kgCO2e/${i.factor_unit}` : ""}</div><div className="text-xs text-gray-500 max-w-xs truncate" title={i.factor_citation ?? ""}>{i.factor_citation}</div></td>
                      <td className="px-4 py-3 text-right font-medium">{fmt(i.co2e_kg_per_fu, 4)}</td>
                      <td className="px-4 py-3"><span className={`rounded px-1.5 py-0.5 text-xs ${STATUS_CLS[i.status] ?? "bg-gray-100 text-gray-600"}`}>{i.status}</span></td>
                      <td className="px-4 py-3 text-right whitespace-nowrap">
                        <button className="mr-2 text-gray-400 hover:text-emerald-600" onClick={() => setItemMode(i)}><Pencil className="h-4 w-4" /></button>
                        <button className="text-gray-400 hover:text-red-600" onClick={() => deleteI.mutate({ pid: product.id, itemId: i.id })}><Trash2 className="h-4 w-4" /></button>
                      </td>
                    </tr>))}</tbody>
                </table>)}
            </div>
          </>)}
        </div>
      </div>
    </div>
  );
}
