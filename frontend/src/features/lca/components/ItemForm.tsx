import { useState, type ChangeEvent } from "react";
import { LCA_STAGES, type FactorSource, type LcaItem, type LcaItemCreate, type LcaStage, type QuantityBasis } from "../api/lcaApi";
import { useCountryOptions, useEmissionFactorOptions, useFuelLibrary } from "../hooks/useLca";
import { BTN, BTN2, INPUT, LABEL } from "./ProductForm";

interface Props { initial?: LcaItem | null; loading?: boolean; onSubmit: (d: LcaItemCreate) => void; onCancel: () => void; }

export default function ItemForm({ initial, loading, onSubmit, onCancel }: Props) {
  const { data: fuels = [] } = useFuelLibrary();
  const { data: countries = [] } = useCountryOptions();
  const { data: factors = [] } = useEmissionFactorOptions();
  const [f, setF] = useState({
    name: initial?.name ?? "", stage: (initial?.stage ?? "raw_materials") as LcaStage,
    factor_source: (initial?.factor_source ?? "factor") as FactorSource,
    fuel_key: initial?.fuel_key ?? "", country_code: initial?.country_code ?? "IN",
    emission_factor_id: initial?.emission_factor_id ? String(initial.emission_factor_id) : "",
    quantity: initial ? String(initial.quantity) : "", basis: (initial?.basis ?? "per_functional_unit") as QuantityBasis,
    data_source: initial?.data_source ?? "",
  });
  const set = (k: keyof typeof f) => (e: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => setF({ ...f, [k]: e.target.value } as typeof f);
  const activeFactors = factors.filter((x) => x.is_active);
  const chosen = activeFactors.find((x) => String(x.id) === f.emission_factor_id);
  // Unit is dictated by the factor, never typed: fuel -> tonne, grid -> kWh, factor -> its own unit.
  const unit = f.factor_source === "fuel" ? "tonne" : f.factor_source === "electricity" ? "kWh" : (chosen?.unit ?? "");
  const refOk = f.factor_source === "fuel" ? f.fuel_key !== "" : f.factor_source === "electricity" ? f.country_code !== "" : chosen !== undefined;
  const valid = f.name.trim() !== "" && refOk && f.quantity !== "" && Number(f.quantity) >= 0;
  const submit = () => onSubmit({
    name: f.name.trim(), stage: f.stage, factor_source: f.factor_source,
    fuel_key: f.factor_source === "fuel" ? f.fuel_key : null,
    country_code: f.factor_source === "electricity" ? f.country_code : null,
    emission_factor_id: f.factor_source === "factor" ? Number(f.emission_factor_id) : null,
    quantity: Number(f.quantity), unit, basis: f.basis, data_source: f.data_source.trim() || null,
  });
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-5 space-y-3">
      <h3 className="font-semibold text-gray-800">{initial ? "Edit inventory item" : "Add inventory item"}</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div><label className={LABEL}>Item name *</label><input className={INPUT} value={f.name} onChange={set("name")} /></div>
        <div><label className={LABEL}>Life-cycle stage</label><select className={INPUT} value={f.stage} onChange={set("stage")}>
          {LCA_STAGES.map((s) => <option key={s.value} value={s.value}>{s.label}</option>)}</select></div>
        <div><label className={LABEL}>Factor source</label><select className={INPUT} value={f.factor_source} onChange={set("factor_source")}>
          <option value="fuel">Fuel (IPCC combustion)</option><option value="electricity">Grid electricity (country)</option><option value="factor">Material / other factor (DEFRA, IPCC)</option></select></div>
        {f.factor_source === "fuel" && <div className="md:col-span-3"><label className={LABEL}>Fuel *</label>
          <select className={INPUT} value={f.fuel_key} onChange={set("fuel_key")}><option value="">Select fuel</option>
            {fuels.map((x) => <option key={x.key} value={x.key}>{x.name}</option>)}</select></div>}
        {f.factor_source === "electricity" && <div className="md:col-span-3"><label className={LABEL}>Grid country *</label>
          <select className={INPUT} value={f.country_code} onChange={set("country_code")}>
            {countries.map((c) => <option key={c.code} value={c.code}>{c.name}{c.grid_factor_kgco2e_per_kwh != null ? ` - ${c.grid_factor_kgco2e_per_kwh} kgCO2e/kWh` : " (no verified factor)"}</option>)}</select></div>}
        {f.factor_source === "factor" && <div className="md:col-span-3"><label className={LABEL}>Emission factor *</label>
          <select className={INPUT} value={f.emission_factor_id} onChange={set("emission_factor_id")}><option value="">Select factor</option>
            {activeFactors.map((x) => <option key={x.id} value={x.id}>{x.meter_type} - {x.factor_kgco2e_per_unit} kgCO2e/{x.unit} ({x.source_year}, {x.region})</option>)}</select></div>}
        <div><label className={LABEL}>Quantity * <span className="text-gray-400">({unit || "unit follows the factor"})</span></label>
          <input type="number" min="0" step="any" className={INPUT} value={f.quantity} onChange={set("quantity")} /></div>
        <div><label className={LABEL}>Basis</label><select className={INPUT} value={f.basis} onChange={set("basis")}>
          <option value="per_functional_unit">Per functional unit</option><option value="annual_total">Annual total (allocated by annual output)</option></select></div>
        <div><label className={LABEL}>Data source (invoice, weighbridge, ERP)</label><input className={INPUT} value={f.data_source} onChange={set("data_source")} /></div>
      </div>
      <div className="flex gap-2 justify-end">
        <button className={BTN2} onClick={onCancel}>Cancel</button>
        <button disabled={!valid || loading} className={BTN} onClick={submit}>{loading ? "Saving..." : "Save"}</button>
      </div>
    </div>
  );
}
