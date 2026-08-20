import { useState } from "react";
import { Pencil, Plus, Trash2 } from "lucide-react";
import {
  useWaterWasteSummary,
  useWaterRecords,
  useWasteRecords,
  useCreateWaterRecord,
  useUpdateWaterRecord,
  useDeleteWaterRecord,
  useCreateWasteRecord,
  useUpdateWasteRecord,
  useDeleteWasteRecord,
} from "../hooks/useWaterWaste";

type Tab = "water" | "waste";
type FormState = Record<string, string>;

const WATER_FIELDS: { name: string; label: string }[] = [
  { name: "withdrawal_surface_water", label: "Surface water" },
  { name: "withdrawal_groundwater", label: "Groundwater" },
  { name: "withdrawal_third_party", label: "Third party water" },
  { name: "withdrawal_seawater_desalinated", label: "Seawater / desalinated" },
  { name: "withdrawal_others", label: "Other sources" },
];

const DISCHARGE_FIELDS: { name: string; label: string }[] = [
  { name: "discharge_surface_water", label: "To surface water" },
  { name: "discharge_groundwater", label: "To groundwater" },
  { name: "discharge_seawater", label: "To seawater" },
  { name: "discharge_third_party", label: "To third parties" },
  { name: "discharge_others", label: "To other destinations" },
];

const WASTE_FIELDS: { name: string; label: string }[] = [
  { name: "plastic_waste", label: "Plastic (A)" },
  { name: "e_waste", label: "E-waste (B)" },
  { name: "bio_medical_waste", label: "Bio-medical (C) - hazardous" },
  { name: "construction_demolition_waste", label: "Construction & demolition (D)" },
  { name: "battery_waste", label: "Battery (E) - hazardous" },
  { name: "radioactive_waste", label: "Radioactive (F) - hazardous" },
  { name: "other_hazardous_waste", label: "Other HAZARDOUS (G)" },
  { name: "other_non_hazardous_waste", label: "Other NON-hazardous (H)" },
];

const RECOVERY_FIELDS: { name: string; label: string }[] = [
  { name: "recycled", label: "Recycled" },
  { name: "reused", label: "Re-used" },
  { name: "other_recovery", label: "Other recovery" },
];

const DISPOSAL_FIELDS: { name: string; label: string }[] = [
  { name: "incineration", label: "Incineration" },
  { name: "landfilling", label: "Landfilling" },
  { name: "other_disposal", label: "Other disposal" },
];

/** Null means nothing was disclosed - it must never render as a zero. */
const fmt = (value: string | null | undefined, unit: string) =>
  value === null || value === undefined
    ? "Not tracked"
    : `${Number(value).toLocaleString()} ${unit}`;

export default function WaterWastePage() {
  const currentYear = new Date().getFullYear();
  const [year, setYear] = useState<number>(currentYear);
  const [tab, setTab] = useState<Tab>("water");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState<FormState>({});

  const { data: summary } = useWaterWasteSummary(year);
  const { data: waterRecords, isLoading: waterLoading } = useWaterRecords(year);
  const { data: wasteRecords, isLoading: wasteLoading } = useWasteRecords(year);

  const [editingId, setEditingId] = useState<number | null>(null);

  const createWater = useCreateWaterRecord();
  const updateWater = useUpdateWaterRecord();
  const updateWaste = useUpdateWasteRecord();
  const deleteWater = useDeleteWaterRecord();
  const createWaste = useCreateWasteRecord();
  const deleteWaste = useDeleteWasteRecord();

  const numericFields =
    tab === "water"
      ? [...WATER_FIELDS, ...DISCHARGE_FIELDS]
      : [...WASTE_FIELDS, ...RECOVERY_FIELDS, ...DISPOSAL_FIELDS];

  const handleChange = (name: string, value: string) =>
    setForm((prev) => ({ ...prev, [name]: value }));

  const resetForm = () => {
    setForm({});
    setEditingId(null);
    setShowForm(false);
  };

  /**
   * Load an existing record into the same form the create flow uses.
   * Nulls become empty strings rather than "0", so an undisclosed figure
   * stays undisclosed when the record is saved again.
   */
  const startEdit = (record: Record<string, unknown>) => {
    const next: FormState = {};
    Object.entries(record).forEach(([key, value]) => {
      if (value === null || value === undefined) return;
      if (typeof value === "boolean") {
        next[key] = value ? "true" : "false";
        return;
      }
      next[key] = String(value);
    });
    setForm(next);
    setEditingId(record.id as number);
    setShowForm(true);
  };

  const handleSubmit = () => {
    if (!form.period_start || !form.period_end) return;

    // Blank fields are omitted rather than sent as 0 - the backend keeps
    // "not disclosed" and "genuinely zero" apart, and the form must not
    // collapse them on the way in.
    const payload: Record<string, unknown> = {
      period_start: form.period_start,
      period_end: form.period_end,
    };
    numericFields.forEach(({ name }) => {
      const raw = form[name];
      const filled = raw !== undefined && raw.trim() !== "";
      if (filled) {
        payload[name] = Number(raw);
      } else if (editingId !== null) {
        // On edit, a cleared field means "remove this figure". Omitting it
        // would leave the old value in place, since the backend applies
        // exclude_unset - so clearing has to be sent explicitly as null.
        payload[name] = null;
      }
    });

    if (tab === "water") {
      payload.is_water_stressed_area = form.is_water_stressed_area === "true";
      if (form.discharge_treatment_level?.trim())
        payload.discharge_treatment_level = form.discharge_treatment_level.trim();
      if (editingId !== null) {
        updateWater.mutate(
          { id: editingId, data: payload as never },
          { onSuccess: resetForm }
        );
      } else {
        createWater.mutate(payload as never, { onSuccess: resetForm });
      }
    } else {
      if (form.waste_management_practices?.trim())
        payload.waste_management_practices = form.waste_management_practices.trim();
      if (editingId !== null) {
        updateWaste.mutate(
          { id: editingId, data: payload as never },
          { onSuccess: resetForm }
        );
      } else {
        createWaste.mutate(payload as never, { onSuccess: resetForm });
      }
    }
  };

  const years = [currentYear, currentYear - 1, currentYear - 2, currentYear - 3];

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">
            Water and Waste
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            BRSR Principle 6, questions 3 and 9. Both are BRSR Core indicators
            requiring assurance.
          </p>
        </div>
        <select
          value={year}
          onChange={(e) => setYear(Number(e.target.value))}
          className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none"
        >
          {years.map((y) => (
            <option key={y} value={y}>
              {y}
            </option>
          ))}
        </select>
      </div>

      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {[
            { label: "Water withdrawn", value: fmt(summary.water.total_withdrawal_kl, "KL") },
            { label: "Water discharged", value: fmt(summary.water.total_discharge_kl, "KL") },
            { label: "Water consumed", value: fmt(summary.water.total_consumption_kl, "KL") },
            { label: "Waste generated", value: fmt(summary.waste.total_generated_mt, "MT") },
            { label: "Waste recovered", value: fmt(summary.waste.total_recovered_mt, "MT") },
          ].map((card) => (
            <div
              key={card.label}
              className="bg-white rounded-lg border border-gray-200 p-4"
            >
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                {card.label}
              </p>
              <p className="mt-1 text-lg font-semibold text-gray-900">
                {card.value}
              </p>
            </div>
          ))}
        </div>
      )}

      <div className="flex items-center justify-between">
        <div className="flex gap-2">
          {(["water", "waste"] as Tab[]).map((t) => (
            <button
              key={t}
              onClick={() => {
                setTab(t);
                resetForm();
              }}
              className={`rounded-md px-4 py-2 text-sm font-medium border capitalize ${
                tab === t
                  ? "border-emerald-500 bg-emerald-50 text-emerald-800"
                  : "border-gray-200 bg-white text-gray-600 hover:bg-gray-50"
              }`}
            >
              {t}
            </button>
          ))}
        </div>
        <button
          onClick={() => setShowForm((v) => !v)}
          className="inline-flex items-center gap-2 rounded-md bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700"
        >
          <Plus className="h-4 w-4" />
          {showForm ? "Close form" : `Add ${tab} record`}
        </button>
      </div>

      {showForm && (
        <div className="bg-white rounded-lg border border-gray-200 p-5 space-y-5">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Period start
              </label>
              <input
                type="date"
                value={form.period_start ?? ""}
                onChange={(e) => handleChange("period_start", e.target.value)}
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Period end
              </label>
              <input
                type="date"
                value={form.period_end ?? ""}
                onChange={(e) => handleChange("period_end", e.target.value)}
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none"
              />
            </div>
            {tab === "water" && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  In a water-stressed area?
                </label>
                <select
                  value={form.is_water_stressed_area ?? "false"}
                  onChange={(e) =>
                    handleChange("is_water_stressed_area", e.target.value)
                  }
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none"
                >
                  <option value="false">No</option>
                  <option value="true">Yes</option>
                </select>
              </div>
            )}
          </div>

          {tab === "water" ? (
            <>
              <FieldGroup
                title="Water withdrawal by source (KL)"
                fields={WATER_FIELDS}
                form={form}
                onChange={handleChange}
              />
              <FieldGroup
                title="Water discharge by destination (KL)"
                fields={DISCHARGE_FIELDS}
                form={form}
                onChange={handleChange}
              />
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Treatment level before discharge
                </label>
                <input
                  type="text"
                  value={form.discharge_treatment_level ?? ""}
                  onChange={(e) =>
                    handleChange("discharge_treatment_level", e.target.value)
                  }
                  placeholder="e.g. Secondary treatment"
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none"
                />
              </div>
            </>
          ) : (
            <>
              <FieldGroup
                title="Waste generated by category (MT)"
                fields={WASTE_FIELDS}
                form={form}
                onChange={handleChange}
              />
              <FieldGroup
                title="Recovered / diverted from disposal (MT)"
                fields={RECOVERY_FIELDS}
                form={form}
                onChange={handleChange}
              />
              <FieldGroup
                title="Disposed (MT)"
                fields={DISPOSAL_FIELDS}
                form={form}
                onChange={handleChange}
              />
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Waste management practices
                </label>
                <textarea
                  rows={2}
                  value={form.waste_management_practices ?? ""}
                  onChange={(e) =>
                    handleChange("waste_management_practices", e.target.value)
                  }
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none"
                />
              </div>
            </>
          )}

          <div className="flex justify-end gap-2">
            <button
              onClick={resetForm}
              className="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              onClick={handleSubmit}
              disabled={createWater.isPending || createWaste.isPending}
              className="rounded-md bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700 disabled:opacity-50"
            >
              {editingId !== null ? "Update record" : "Save record"}
            </button>
          </div>
        </div>
      )}

      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        {tab === "water" ? (
          waterLoading ? (
            <p className="p-5 text-gray-500">Loading water records...</p>
          ) : (waterRecords ?? []).length === 0 ? (
            <p className="p-5 text-gray-500">
              No water records for {year}. Add one to start tracking BRSR P6
              question 3.
            </p>
          ) : (
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-left text-gray-600">
                <tr>
                  <th className="px-4 py-3 font-medium">Period</th>
                  <th className="px-4 py-3 font-medium">Withdrawn</th>
                  <th className="px-4 py-3 font-medium">Discharged</th>
                  <th className="px-4 py-3 font-medium">Consumed</th>
                  <th className="px-4 py-3 font-medium">Stressed area</th>
                  <th className="px-4 py-3" />
                </tr>
              </thead>
              <tbody>
                {(waterRecords ?? []).map((r) => (
                  <tr key={r.id} className="border-t border-gray-100">
                    <td className="px-4 py-3">
                      {r.period_start} to {r.period_end}
                    </td>
                    <td className="px-4 py-3">{fmt(r.total_withdrawal, "KL")}</td>
                    <td className="px-4 py-3">{fmt(r.total_discharge, "KL")}</td>
                    <td className="px-4 py-3">{fmt(r.total_consumption, "KL")}</td>
                    <td className="px-4 py-3">
                      {r.is_water_stressed_area ? "Yes" : "No"}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <button
                        onClick={() => startEdit(r as never)}
                        className="mr-2 text-gray-400 hover:text-emerald-600"
                        aria-label="Edit"
                      >
                        <Pencil className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => deleteWater.mutate(r.id)}
                        className="text-gray-400 hover:text-red-600"
                        aria-label="Delete"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )
        ) : wasteLoading ? (
          <p className="p-5 text-gray-500">Loading waste records...</p>
        ) : (wasteRecords ?? []).length === 0 ? (
          <p className="p-5 text-gray-500">
            No waste records for {year}. Add one to start tracking BRSR P6
            question 9.
          </p>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-left text-gray-600">
              <tr>
                <th className="px-4 py-3 font-medium">Period</th>
                <th className="px-4 py-3 font-medium">Generated</th>
                <th className="px-4 py-3 font-medium">Hazardous</th>
                <th className="px-4 py-3 font-medium">Recovered</th>
                <th className="px-4 py-3 font-medium">Disposed</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody>
              {(wasteRecords ?? []).map((r) => (
                <tr key={r.id} className="border-t border-gray-100">
                  <td className="px-4 py-3">
                    {r.period_start} to {r.period_end}
                  </td>
                  <td className="px-4 py-3">{fmt(r.total_generated, "MT")}</td>
                  <td className="px-4 py-3">{fmt(r.hazardous_generated, "MT")}</td>
                  <td className="px-4 py-3">{fmt(r.total_recovered, "MT")}</td>
                  <td className="px-4 py-3">{fmt(r.total_disposed, "MT")}</td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={() => startEdit(r as never)}
                      className="mr-2 text-gray-400 hover:text-emerald-600"
                      aria-label="Edit"
                    >
                      <Pencil className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => deleteWaste.mutate(r.id)}
                      className="text-gray-400 hover:text-red-600"
                      aria-label="Delete"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

function FieldGroup({
  title,
  fields,
  form,
  onChange,
}: {
  title: string;
  fields: { name: string; label: string }[];
  form: FormState;
  onChange: (name: string, value: string) => void;
}) {
  return (
    <div>
      <p className="text-sm font-medium text-gray-700 mb-2">{title}</p>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
        {fields.map((field) => (
          <div key={field.name}>
            <label className="block text-xs text-gray-500 mb-1">
              {field.label}
            </label>
            <input
              type="number"
              step="any"
              min="0"
              value={form[field.name] ?? ""}
              onChange={(e) => onChange(field.name, e.target.value)}
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none"
            />
          </div>
        ))}
      </div>
    </div>
  );
}
