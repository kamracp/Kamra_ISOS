import { Plus, X } from "lucide-react";

export interface ObjectFieldDef {
  name: string;
  label: string;
  type?: "text" | "number";
}

export type ObjectRow = Record<string, string | number>;

interface ObjectListFieldProps {
  label: string;
  fields: ObjectFieldDef[];
  value: ObjectRow[];
  onChange: (next: ObjectRow[]) => void;
}

/**
 * Editable list of objects, for the BRSR Section A repeating disclosure
 * blocks that carry several columns per row (Q14, Q15, Q20, Q21, Q23).
 *
 * The column definitions arrive as props: this component knows nothing
 * about any particular question, which is what lets one component serve
 * all five blocks.
 *
 * Blank-row filtering is deliberately NOT done here - which field makes a
 * row "blank" differs per block (description for Q14, stakeholder_group
 * for Q23), so the page decides that before saving.
 */
export default function ObjectListField({
  label,
  fields,
  value,
  onChange,
}: ObjectListFieldProps) {
  const emptyRow = (): ObjectRow =>
    Object.fromEntries(fields.map((f) => [f.name, ""]));

  const rows = value.length > 0 ? value : [emptyRow()];

  const updateCell = (index: number, name: string, raw: string) => {
    const field = fields.find((f) => f.name === name);
    const parsed =
      field?.type === "number" && raw.trim() !== "" ? Number(raw) : raw;
    const copy = rows.map((row, i) =>
      i === index ? { ...row, [name]: parsed } : row
    );
    onChange(copy);
  };

  const addRow = () => onChange([...rows, emptyRow()]);

  const removeRow = (index: number) =>
    onChange(rows.filter((_, i) => i !== index));

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-2">
        {label}
      </label>
      <div className="space-y-3">
        {rows.map((row, index) => (
          <div
            key={index}
            className="flex items-start gap-2 rounded-md border border-gray-200 p-3"
          >
            <div className="flex-1 grid grid-cols-1 md:grid-cols-3 gap-3">
              {fields.map((field) => (
                <div key={field.name}>
                  <label className="block text-xs text-gray-500 mb-1">
                    {field.label}
                  </label>
                  <input
                    type={field.type === "number" ? "number" : "text"}
                    value={row[field.name] ?? ""}
                    onChange={(e) => updateCell(index, field.name, e.target.value)}
                    className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none"
                  />
                </div>
              ))}
            </div>
            <button
              type="button"
              onClick={() => removeRow(index)}
              disabled={rows.length === 1}
              className="mt-6 rounded-md p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-600 disabled:opacity-30 disabled:hover:bg-transparent"
              aria-label="Remove row"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        ))}
      </div>
      <button
        type="button"
        onClick={addRow}
        className="mt-2 inline-flex items-center gap-1 text-sm font-medium text-emerald-600 hover:text-emerald-700"
      >
        <Plus className="h-4 w-4" />
        Add row
      </button>
    </div>
  );
}
