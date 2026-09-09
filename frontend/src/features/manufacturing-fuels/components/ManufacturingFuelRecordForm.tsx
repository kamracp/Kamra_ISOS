import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { PURPOSE_LABELS, type FuelLibraryEntry, type FuelPurpose, type ManufacturingFuelRecord, type ManufacturingFuelRecordCreate } from "../api/manufacturingFuelsApi";

interface Props {
  units: { id: number; unit_name: string; unit_code: string }[];
  library: FuelLibraryEntry[];
  initialData?: ManufacturingFuelRecord;
  onSubmit: (data: ManufacturingFuelRecordCreate) => void;
  onCancel?: () => void;
  loading?: boolean;
}

const inputCls = "w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none";

export default function ManufacturingFuelRecordForm({ units, library, initialData, onSubmit, onCancel, loading = false }: Props) {
  const { register, handleSubmit, reset, watch, formState: { errors } } = useForm<ManufacturingFuelRecordCreate>();
  const fuelKey = watch("fuel_key");
  const tonnes = watch("quantity_tonnes");
  const fuel = library.find((f) => f.key === fuelKey);
  // Live preview so the user sees GJ / CO2e before saving (same maths as backend).
  const previewGj = fuel?.lhv_tj_per_gg != null && tonnes > 0 ? tonnes * fuel.lhv_tj_per_gg : null;
  const previewCo2e = fuel?.co2e_kg_per_tonne != null && tonnes > 0 ? tonnes * fuel.co2e_kg_per_tonne : null;

  useEffect(() => {
    reset(initialData ? {
      manufacturing_unit_id: initialData.manufacturing_unit_id,
      period_start: initialData.period_start, period_end: initialData.period_end,
      fuel_key: initialData.fuel_key, quantity_tonnes: initialData.quantity_tonnes,
      purpose: initialData.purpose, source: initialData.source ?? "", remarks: initialData.remarks ?? "",
    } : {
      manufacturing_unit_id: units[0]?.id, period_start: "", period_end: "",
      fuel_key: library[0]?.key ?? "", quantity_tonnes: 0, purpose: "process_heat", source: "", remarks: "",
    });
  }, [initialData, reset, units, library]);

  // Group the 54 fuels by IPCC category for a usable dropdown.
  const groups = library.reduce<Record<string, FuelLibraryEntry[]>>((acc, f) => { (acc[f.category] ??= []).push(f); return acc; }, {});

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6 rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
      <div>
        <h2 className="text-xl font-semibold text-gray-800">{initialData ? "Edit Fuel Record" : "Add Fuel Record"}</h2>
        <p className="mt-1 text-sm text-gray-500">Fuel burned at a unit in a period. Enter tonnes -- convert volumes with a stated density and note it in remarks.</p>
      </div>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Manufacturing Unit *</label>
          <select {...register("manufacturing_unit_id", { required: "Required", valueAsNumber: true })} className={inputCls} disabled={Boolean(initialData)}>
            {units.map((u) => <option key={u.id} value={u.id}>{u.unit_code} -- {u.unit_name}</option>)}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Purpose *</label>
          <select {...register("purpose", { required: true })} className={inputCls}>
            {(Object.keys(PURPOSE_LABELS) as FuelPurpose[]).map((p) => <option key={p} value={p}>{PURPOSE_LABELS[p]}</option>)}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Period Start *</label>
          <input type="date" {...register("period_start", { required: "Required" })} className={inputCls} />
          {errors.period_start && <p className="mt-1 text-sm text-red-600">{errors.period_start.message}</p>}
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Period End *</label>
          <input type="date" {...register("period_end", { required: "Required" })} className={inputCls} />
          {errors.period_end && <p className="mt-1 text-sm text-red-600">{errors.period_end.message}</p>}
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Fuel (IPCC library) *</label>
          <select {...register("fuel_key", { required: "Required" })} className={inputCls}>
            {Object.entries(groups).map(([cat, fuels]) => (
              <optgroup key={cat} label={cat}>
                {fuels.map((f) => <option key={f.key} value={f.key}>{f.name}{f.is_biogenic ? " (biogenic)" : ""}</option>)}
              </optgroup>
            ))}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Quantity (tonnes) *</label>
          <input type="number" step="0.001" min={0} {...register("quantity_tonnes", { required: "Required", valueAsNumber: true, min: { value: 0, message: "Must be >= 0" } })} className={inputCls} />
          {errors.quantity_tonnes && <p className="mt-1 text-sm text-red-600">{errors.quantity_tonnes.message}</p>}
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Source (invoice, weighbridge, density used)</label>
          <input type="text" maxLength={100} {...register("source")} className={inputCls} />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Remarks</label>
          <input type="text" {...register("remarks")} className={inputCls} />
        </div>
      </div>

      {fuel && (
        <div className="rounded-lg bg-blue-50 p-4 text-sm text-blue-900">
          <span className="font-semibold">{fuel.name}</span>: LHV {fuel.lhv_tj_per_gg ?? "n/a"} GJ/t · {fuel.co2e_kg_per_tonne != null ? `${fuel.co2e_kg_per_tonne.toFixed(0)} kgCO₂e/t` : "no factor"}
          {previewGj != null && <> · this entry ≈ <span className="font-semibold">{previewGj.toLocaleString("en-IN", { maximumFractionDigits: 0 })} GJ</span> ({(previewGj / 41.868).toFixed(1)} toe)</>}
          {previewCo2e != null && <> · ≈ <span className="font-semibold">{(previewCo2e / 1000).toLocaleString("en-IN", { maximumFractionDigits: 1 })} tCO₂e</span>{fuel.is_biogenic ? " (biogenic CO₂ reported separately)" : ""}</>}
        </div>
      )}

      <div className="flex justify-end gap-3 border-t border-gray-200 pt-6">
        {onCancel && <button type="button" onClick={onCancel} disabled={loading} className="rounded-lg border border-gray-300 px-5 py-2 font-medium text-gray-700 hover:bg-gray-100 disabled:opacity-50">Cancel</button>}
        <button type="submit" disabled={loading} className="rounded-lg bg-blue-600 px-5 py-2 font-medium text-white hover:bg-blue-700 disabled:opacity-50">
          {loading ? "Saving..." : initialData ? "Update Record" : "Add Record"}
        </button>
      </div>
    </form>
  );
}
