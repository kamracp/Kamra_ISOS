import { useState, type ChangeEvent } from "react";
import { BTN, BTN2, INPUT, LABEL } from "../../lca/components/ProductForm";
import { useLcaProducts } from "../../lca/hooks/useLca";
import { GOODS_CATEGORIES, type CbamGood, type CbamGoodCreate, type GoodsCategory } from "../api/cbamApi";

interface Props { initial?: CbamGood | null; loading?: boolean; onSubmit: (d: CbamGoodCreate) => void; onCancel: () => void; }

const MASS_FU = ["tonne", "t", "mt", "kg"];

export default function GoodForm({ initial, loading, onSubmit, onCancel }: Props) {
  const { data: products = [] } = useLcaProducts();
  const [f, setF] = useState({
    name: initial?.name ?? "", cn_code: initial?.cn_code ?? "",
    goods_category: (initial?.goods_category ?? "cement") as GoodsCategory,
    production_route: initial?.production_route ?? "",
    reporting_year: String(initial?.reporting_year ?? new Date().getFullYear()),
    production_qty_tonne: initial ? String(initial.production_qty_tonne) : "",
    carbon_price_paid_per_tco2e: initial?.carbon_price_paid_per_tco2e != null ? String(initial.carbon_price_paid_per_tco2e) : "",
    lca_product_id: initial?.lca_product_id ? String(initial.lca_product_id) : "",
    remarks: initial?.remarks ?? "",
  });
  const set = (k: keyof typeof f) => (e: ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) =>
    setF({ ...f, [k]: e.target.value } as typeof f);
  const valid = f.name.trim() !== "" && /^\d{4,8}$/.test(f.cn_code.replace(/\s/g, "")) && f.reporting_year !== "" && f.production_qty_tonne !== "" && Number(f.production_qty_tonne) > 0;
  const submit = () => onSubmit({
    name: f.name.trim(), cn_code: f.cn_code.trim(), goods_category: f.goods_category,
    production_route: f.production_route.trim() || null, reporting_year: Number(f.reporting_year),
    production_qty_tonne: Number(f.production_qty_tonne),
    carbon_price_paid_per_tco2e: f.carbon_price_paid_per_tco2e === "" ? null : Number(f.carbon_price_paid_per_tco2e),
    lca_product_id: f.lca_product_id ? Number(f.lca_product_id) : null, remarks: f.remarks.trim() || null,
  });
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-5 space-y-3">
      <h3 className="font-semibold text-gray-800">{initial ? "Edit CBAM good" : "New CBAM good"}</h3>
      <div className="grid gap-3 md:grid-cols-3">
        <div><label className={LABEL}>Good name *</label><input className={INPUT} value={f.name} onChange={set("name")} /></div>
        <div><label className={LABEL}>CN code * (e.g. 2523 29 00)</label><input className={INPUT} value={f.cn_code} onChange={set("cn_code")} /></div>
        <div><label className={LABEL}>CBAM category</label><select className={INPUT} value={f.goods_category} onChange={set("goods_category")}>
          {GOODS_CATEGORIES.map((c) => <option key={c.value} value={c.value}>{c.label}</option>)}</select></div>
        <div><label className={LABEL}>Production route</label><input className={INPUT} placeholder="dry kiln, BF-BOF, DRI-EAF..." value={f.production_route} onChange={set("production_route")} /></div>
        <div><label className={LABEL}>Reporting year *</label><input className={INPUT} type="number" value={f.reporting_year} onChange={set("reporting_year")} /></div>
        <div><label className={LABEL}>Production in year (tonne) *</label><input className={INPUT} type="number" min={0} value={f.production_qty_tonne} onChange={set("production_qty_tonne")} /></div>
        <div className="md:col-span-2"><label className={LABEL}>LCA product (SEE source; functional unit must be tonne or kg)</label>
          <select className={INPUT} value={f.lca_product_id} onChange={set("lca_product_id")}>
            <option value="">Not linked (SEE cannot be calculated)</option>
            {products.map((p) => <option key={p.id} value={p.id}>{p.name} - per {p.functional_unit_qty} {p.functional_unit}{MASS_FU.includes(p.functional_unit.toLowerCase()) ? "" : " (not a mass unit)"}</option>)}
          </select></div>
        <div><label className={LABEL}>Carbon price paid (per tCO2e, optional)</label><input className={INPUT} type="number" min={0} value={f.carbon_price_paid_per_tco2e} onChange={set("carbon_price_paid_per_tco2e")} /></div>
        <div className="md:col-span-3"><label className={LABEL}>Remarks</label><textarea className={INPUT} rows={2} value={f.remarks} onChange={set("remarks")} /></div>
      </div>
      <div className="flex justify-end gap-2">
        <button className={BTN2} onClick={onCancel}>Cancel</button>
        <button className={BTN} disabled={!valid || loading} onClick={submit}>{loading ? "Saving..." : "Save"}</button>
      </div>
    </div>
  );
}
