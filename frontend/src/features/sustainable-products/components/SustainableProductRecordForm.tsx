import { useEffect } from "react";
import { useForm } from "react-hook-form";

import type {
  SustainableProductFields,
  SustainableProductRecord,
  SustainableProductRecordCreate,
  SustainableProductRecordUpdate,
} from "../api/sustainableProductsApi";

type FieldKind = "pct" | "text" | "textarea" | "yesno";

interface FieldDef {
  name: keyof SustainableProductFields;
  label: string;
  kind: FieldKind;
  hint?: string;
}

interface SectionDef {
  title: string;
  subtitle: string;
  fields: FieldDef[];
}

// One source of truth for the form: SEBI section -> fields. Adding a
// disclosure later means one entry here, not a new block of JSX.
const SECTIONS: SectionDef[] = [
  {
    title: "EI 1 -- R&D and Capex on Sustainable Technologies",
    subtitle: "Percentage of total R&D and capital expenditure, current FY vs previous FY.",
    fields: [
      { name: "rnd_sustainable_percent_current", label: "R&D % (current FY)", kind: "pct" },
      { name: "rnd_sustainable_percent_previous", label: "R&D % (previous FY)", kind: "pct" },
      { name: "capex_sustainable_percent_current", label: "Capex % (current FY)", kind: "pct" },
      { name: "capex_sustainable_percent_previous", label: "Capex % (previous FY)", kind: "pct" },
      { name: "rnd_capex_details", label: "Details of improvements", kind: "textarea" },
    ],
  },
  {
    title: "EI 2 -- Sustainable Sourcing",
    subtitle: "Procedures for sustainable sourcing and the share of inputs sourced sustainably.",
    fields: [
      { name: "has_sustainable_sourcing_procedure", label: "Sustainable sourcing procedure in place?", kind: "yesno" },
      { name: "sustainable_sourcing_percent", label: "% of inputs sourced sustainably", kind: "pct" },
      { name: "sustainable_sourcing_details", label: "Procedure details", kind: "textarea" },
    ],
  },
  {
    title: "EI 3 -- Reclaiming Products at End of Life",
    subtitle: "Processes to safely reclaim products for reuse, recycling or disposal, per material.",
    fields: [
      { name: "reclaim_process_plastics", label: "Plastics (incl. packaging)", kind: "textarea" },
      { name: "reclaim_process_e_waste", label: "E-waste", kind: "textarea" },
      { name: "reclaim_process_hazardous", label: "Hazardous waste", kind: "textarea" },
      { name: "reclaim_process_other", label: "Other waste", kind: "textarea" },
    ],
  },
  {
    title: "EI 4 -- Extended Producer Responsibility",
    subtitle: "Whether EPR applies and whether the waste collection plan is in line with it.",
    fields: [
      { name: "epr_applicable", label: "EPR applicable to the entity?", kind: "yesno" },
      { name: "epr_plan_in_line", label: "Waste collection plan in line with EPR?", kind: "yesno" },
      { name: "epr_details", label: "EPR details / steps taken", kind: "textarea" },
    ],
  },
  {
    title: "Leadership Indicators",
    subtitle: "Optional disclosures beyond the essential set.",
    fields: [
      { name: "has_conducted_lca", label: "Life Cycle Assessment conducted?", kind: "yesno" },
      { name: "lca_details", label: "LCA details (products, boundary, results)", kind: "textarea" },
      { name: "recycled_input_percent", label: "% recycled or reused input material", kind: "pct" },
      { name: "reclaimed_products_percent_details", label: "Reclaimed products as % of products sold", kind: "textarea" },
      { name: "remarks", label: "Remarks", kind: "textarea" },
    ],
  },
];

// Form state holds strings for selects and NaN/number for numeric inputs;
// this is the shape react-hook-form works with before normalisation.
type FormValues = { reporting_year: number } & Record<keyof SustainableProductFields, unknown>;

interface Props {
  initialData?: SustainableProductRecord;
  onSubmit: (data: SustainableProductRecordCreate | SustainableProductRecordUpdate) => void;
  onCancel?: () => void;
  loading?: boolean;
}

const ALL_FIELDS = SECTIONS.flatMap((s) => s.fields);

function toFormValue(def: FieldDef, value: unknown): unknown {
  if (value === null || value === undefined) return def.kind === "yesno" ? "" : "";
  if (def.kind === "yesno") return value ? "true" : "false";
  return value;
}

// Create: drop blanks (backend would store "" while still counting the
// question unanswered). Edit: send blanks as null so a cleared field is
// actually cleared -- exclude_unset on the backend keeps omitted keys.
function normalise(values: FormValues, isEdit: boolean) {
  const out: Record<string, unknown> = { reporting_year: values.reporting_year };
  for (const def of ALL_FIELDS) {
    const raw = values[def.name];
    let v: unknown;
    if (def.kind === "yesno") v = raw === "" || raw === undefined ? null : raw === "true";
    else if (def.kind === "pct") v = raw === "" || raw === undefined || Number.isNaN(raw) ? null : Number(raw);
    else v = typeof raw === "string" && raw.trim() === "" ? null : raw;
    if (v === null && !isEdit) continue;
    out[def.name] = v;
  }
  return out as SustainableProductRecordCreate | SustainableProductRecordUpdate;
}

const inputCls =
  "w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none";

export default function SustainableProductRecordForm({ initialData, onSubmit, onCancel, loading = false }: Props) {
  const { register, handleSubmit, reset, formState: { errors } } = useForm<FormValues>();

  useEffect(() => {
    const base: Record<string, unknown> = {
      reporting_year: initialData?.reporting_year ?? new Date().getFullYear(),
    };
    for (const def of ALL_FIELDS) {
      base[def.name] = toFormValue(def, initialData ? initialData[def.name] : undefined);
    }
    reset(base as FormValues);
  }, [initialData, reset]);

  const renderField = (def: FieldDef) => {
    if (def.kind === "yesno") {
      return (
        <select {...register(def.name)} className={inputCls}>
          <option value="">Not stated</option>
          <option value="false">No</option>
          <option value="true">Yes</option>
        </select>
      );
    }
    if (def.kind === "pct") {
      return (
        <input
          type="number"
          step="0.01"
          min={0}
          max={100}
          {...register(def.name, { valueAsNumber: true })}
          className={inputCls}
          placeholder="0 - 100"
        />
      );
    }
    if (def.kind === "textarea") {
      return <textarea rows={2} {...register(def.name)} className={inputCls} />;
    }
    return <input type="text" {...register(def.name)} className={inputCls} />;
  };

  return (
    <form
      onSubmit={handleSubmit((values) => onSubmit(normalise(values, Boolean(initialData))))}
      className="space-y-8 rounded-xl border border-gray-200 bg-white p-6 shadow-sm"
    >
      <div>
        <h2 className="text-xl font-semibold text-gray-800">
          {initialData ? "Edit Principle 2 Record" : "Add Principle 2 Record"}
        </h2>
        <p className="mt-1 text-sm text-gray-500">
          BRSR Principle 2 -- sustainable and safe goods and services. One record per reporting year.
        </p>
      </div>

      <div className="md:w-1/3">
        <label className="mb-1 block text-sm font-medium text-gray-700">Reporting Year *</label>
        <input
          type="number"
          {...register("reporting_year", {
            required: "Required",
            valueAsNumber: true,
            min: { value: 2000, message: "Must be 2000 or later" },
            max: { value: 2100, message: "Must be 2100 or earlier" },
          })}
          className={inputCls}
        />
        {errors.reporting_year && (
          <p className="mt-1 text-sm text-red-600">{String(errors.reporting_year.message)}</p>
        )}
      </div>

      {SECTIONS.map((section) => (
        <fieldset key={section.title} className="space-y-4 border-t border-gray-200 pt-6">
          <legend className="sr-only">{section.title}</legend>
          <div>
            <h3 className="text-base font-semibold text-gray-800">{section.title}</h3>
            <p className="text-sm text-gray-500">{section.subtitle}</p>
          </div>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            {section.fields.map((def) => (
              <div key={def.name} className={def.kind === "textarea" ? "md:col-span-2" : ""}>
                <label className="mb-1 block text-sm font-medium text-gray-700">{def.label}</label>
                {renderField(def)}
                {def.hint && <p className="mt-1 text-xs text-gray-500">{def.hint}</p>}
              </div>
            ))}
          </div>
        </fieldset>
      ))}

      <div className="flex justify-end gap-3 border-t border-gray-200 pt-6">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            disabled={loading}
            className="rounded-lg border border-gray-300 px-5 py-2 font-medium text-gray-700 transition hover:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Cancel
          </button>
        )}
        <button
          type="submit"
          disabled={loading}
          className="rounded-lg bg-blue-600 px-5 py-2 font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? "Saving..." : initialData ? "Update Record" : "Add Record"}
        </button>
      </div>
    </form>
  );
}
