export interface NestedFieldDef {
  /** Dot path into the block object, e.g. "plants.national". */
  path: string;
  label: string;
  type?: "text" | "number";
}

export type NestedValue = Record<string, unknown>;

interface NestedFieldsGroupProps {
  label: string;
  fields: NestedFieldDef[];
  value: NestedValue;
  onChange: (next: NestedValue) => void;
  columns?: 2 | 3 | 4;
}

function getAtPath(obj: NestedValue, path: string): unknown {
  return path
    .split(".")
    .reduce<unknown>(
      (acc, key) =>
        acc && typeof acc === "object"
          ? (acc as Record<string, unknown>)[key]
          : undefined,
      obj
    );
}

function setAtPath(obj: NestedValue, path: string, next: unknown): NestedValue {
  const [head, ...rest] = path.split(".");
  if (rest.length === 0) {
    return { ...obj, [head]: next };
  }
  const child = obj[head];
  const childObj: NestedValue =
    child && typeof child === "object" ? (child as NestedValue) : {};
  return { ...obj, [head]: setAtPath(childObj, rest.join("."), next) };
}

/**
 * Fixed-shape nested block, for the Section A questions that are not
 * repeating lists but a defined structure: Q16 plants/offices,
 * Q17 markets served, Q18 employee counts, Q19 women participation.
 *
 * Fields are addressed by dot path so one flat field list can describe an
 * arbitrarily nested object - Q18 would otherwise need a dozen separate
 * pieces of state.
 *
 * A cleared field becomes undefined, never 0: "not yet filled" and
 * "genuinely zero" must stay distinguishable, or the completeness figure
 * starts claiming answers that were never given.
 */
export default function NestedFieldsGroup({
  label,
  fields,
  value,
  onChange,
  columns = 3,
}: NestedFieldsGroupProps) {
  const gridClass =
    columns === 2
      ? "md:grid-cols-2"
      : columns === 4
        ? "md:grid-cols-4"
        : "md:grid-cols-3";

  const handleChange = (field: NestedFieldDef, raw: string) => {
    let next: unknown;
    if (raw.trim() === "") {
      next = undefined;
    } else if (field.type === "number") {
      const parsed = Number(raw);
      next = Number.isNaN(parsed) ? undefined : parsed;
    } else {
      next = raw;
    }
    onChange(setAtPath(value, field.path, next));
  };

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-3">
        {label}
      </label>
      <div className={`grid grid-cols-1 ${gridClass} gap-4`}>
        {fields.map((field) => {
          const current = getAtPath(value, field.path);
          return (
            <div key={field.path}>
              <label className="block text-xs text-gray-500 mb-1">
                {field.label}
              </label>
              <input
                type={field.type === "number" ? "number" : "text"}
                value={current === undefined || current === null ? "" : String(current)}
                onChange={(e) => handleChange(field, e.target.value)}
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none"
              />
            </div>
          );
        })}
      </div>
    </div>
  );
}
