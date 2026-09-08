import { useEffect } from "react";
import { useForm } from "react-hook-form";

/**
 * Generic BRSR disclosure form: one record per reporting year, fields
 * declared as data (sections -> fields -> kind). Shared by the Section C
 * principle pages so each principle only declares its SECTIONS.
 *
 * Normalisation rule (from P6/P2): on create, blanks are omitted; on edit,
 * blanks are sent as null so a cleared field is actually cleared under the
 * backend's exclude_unset PUT. Yes/no fields are three-option selects so a
 * nullable boolean stays "not stated" until the user answers.
 */
export type FieldKind = "pct" | "int" | "num" | "text" | "textarea" | "yesno" | "select";

export interface FieldDef<K extends string = string> {
  name: K;
  label: string;
  kind: FieldKind;
  hint?: string;
  options?: { value: string; label: string }[]; // for kind "select"
}

export interface SectionDef<K extends string = string> {
  title: string;
  subtitle?: string;
  fields: FieldDef<K>[];
}

type FormValues = { reporting_year: number } & Record<string, unknown>;

interface Props<T extends Record<string, unknown>> {
  title: string;
  subtitle?: string;
  sections: SectionDef[];
  initialData?: (T & { reporting_year: number }) | null;
  onSubmit: (data: Record<string, unknown>) => void;
  onCancel?: () => void;
  loading?: boolean;
}

const inputCls = "w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none";

function toFormValue(def: FieldDef, value: unknown): unknown {
  if (value === null || value === undefined) return "";
  if (def.kind === "yesno") return value ? "true" : "false";
  return value;
}

export function normaliseDisclosure(values: Record<string, unknown>, fields: FieldDef[], isEdit: boolean) {
  const out: Record<string, unknown> = {};
  if (values.reporting_year !== undefined) out.reporting_year = values.reporting_year;
  for (const def of fields) {
    const raw = values[def.name];
    let v: unknown;
    if (def.kind === "yesno") v = raw === "" || raw === undefined ? null : raw === "true";
    else if (def.kind === "pct" || def.kind === "int" || def.kind === "num") v = raw === "" || raw === undefined || Number.isNaN(raw) ? null : Number(raw);
    else if (def.kind === "select") v = raw === "" || raw === undefined ? null : raw;
    else v = typeof raw === "string" && raw.trim() === "" ? null : raw;
    if (v === null && !isEdit) continue;
    out[def.name] = v;
  }
  return out;
}

export default function DisclosureForm<T extends Record<string, unknown>>({
  title, subtitle, sections, initialData, onSubmit, onCancel, loading = false,
}: Props<T>) {
  const fields = sections.flatMap((s) => s.fields);
  const isEdit = Boolean(initialData);
  const { register, handleSubmit, reset, formState: { errors } } = useForm<FormValues>();

  useEffect(() => {
    const base: Record<string, unknown> = { reporting_year: initialData?.reporting_year ?? new Date().getFullYear() };
    for (const def of fields) base[def.name] = toFormValue(def, initialData ? initialData[def.name] : undefined);
    reset(base as FormValues);
  }, [initialData, reset]); // eslint-disable-line react-hooks/exhaustive-deps

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
      return <input type="number" step="0.01" min={0} max={100} placeholder="0 - 100" {...register(def.name, { valueAsNumber: true })} className={inputCls} />;
    }
    if (def.kind === "select") {
      return (
        <select {...register(def.name)} className={inputCls}>
          <option value="">Not stated</option>
          {(def.options ?? []).map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
        </select>
      );
    }
    if (def.kind === "num") {
      return <input type="number" step="0.001" min={0} placeholder="Not disclosed" {...register(def.name, { valueAsNumber: true })} className={inputCls} />;
    }
    if (def.kind === "int") {
      return <input type="number" step="1" min={0} placeholder="Not disclosed" {...register(def.name, { valueAsNumber: true })} className={inputCls} />;
    }
    if (def.kind === "textarea") return <textarea rows={2} {...register(def.name)} className={inputCls} />;
    return <input type="text" {...register(def.name)} className={inputCls} />;
  };

  return (
    <form
      onSubmit={handleSubmit((values) => onSubmit(normaliseDisclosure(values, fields, isEdit)))}
      className="space-y-8 rounded-xl border border-gray-200 bg-white p-6 shadow-sm"
    >
      <div>
        <h2 className="text-xl font-semibold text-gray-800">{isEdit ? `Edit ${title}` : `Add ${title}`}</h2>
        {subtitle && <p className="mt-1 text-sm text-gray-500">{subtitle}</p>}
      </div>

      <div className="md:w-1/3">
        <label className="mb-1 block text-sm font-medium text-gray-700">Reporting Year *</label>
        <input
          type="number"
          {...register("reporting_year", {
            required: "Required", valueAsNumber: true,
            min: { value: 2000, message: "Must be 2000 or later" },
            max: { value: 2100, message: "Must be 2100 or earlier" },
          })}
          className={inputCls}
        />
        {errors.reporting_year && <p className="mt-1 text-sm text-red-600">{String(errors.reporting_year.message)}</p>}
      </div>

      {sections.map((section) => (
        <fieldset key={section.title} className="space-y-4 border-t border-gray-200 pt-6">
          <legend className="sr-only">{section.title}</legend>
          <div>
            <h3 className="text-base font-semibold text-gray-800">{section.title}</h3>
            {section.subtitle && <p className="text-sm text-gray-500">{section.subtitle}</p>}
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
          <button type="button" onClick={onCancel} disabled={loading}
            className="rounded-lg border border-gray-300 px-5 py-2 font-medium text-gray-700 transition hover:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-50">
            Cancel
          </button>
        )}
        <button type="submit" disabled={loading}
          className="rounded-lg bg-blue-600 px-5 py-2 font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50">
          {loading ? "Saving..." : isEdit ? "Update Record" : "Add Record"}
        </button>
      </div>
    </form>
  );
}
