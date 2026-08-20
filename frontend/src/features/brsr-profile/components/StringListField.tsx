import { Plus, X } from "lucide-react";

interface StringListFieldProps {
  label: string;
  value: string[];
  onChange: (next: string[]) => void;
  placeholder?: string;
}

/**
 * Editable list of plain strings, e.g. BRSR Section A Q10
 * (stock exchanges where the entity is listed).
 *
 * Rows are addressed by index rather than by a generated id: the list is
 * short, order carries no meaning, and every edit replaces the whole array
 * anyway, so an id would add bookkeeping without buying anything.
 */
export default function StringListField({
  label,
  value,
  onChange,
  placeholder,
}: StringListFieldProps) {
  const rows = value.length > 0 ? value : [""];

  const updateRow = (index: number, next: string) => {
    const copy = [...rows];
    copy[index] = next;
    onChange(copy);
  };

  const addRow = () => onChange([...rows, ""]);

  const removeRow = (index: number) => {
    const copy = rows.filter((_, i) => i !== index);
    onChange(copy);
  };

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-2">
        {label}
      </label>
      <div className="space-y-2">
        {rows.map((row, index) => (
          <div key={index} className="flex items-center gap-2">
            <input
              type="text"
              value={row}
              placeholder={placeholder}
              onChange={(e) => updateRow(index, e.target.value)}
              className="flex-1 rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none"
            />
            <button
              type="button"
              onClick={() => removeRow(index)}
              disabled={rows.length === 1 && row === ""}
              className="rounded-md p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-600 disabled:opacity-30 disabled:hover:bg-transparent"
              aria-label="Remove"
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
        Add
      </button>
    </div>
  );
}
