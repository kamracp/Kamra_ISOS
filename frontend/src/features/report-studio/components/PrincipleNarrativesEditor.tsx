import { useState } from "react";
import type { SdgLabel } from "../api/reportStudioApi";

export interface PrincipleDraft {
  highlight: string;
  intro: string;
  sdgs: number[];
}
export type PrincipleDrafts = Record<number, PrincipleDraft>;

export const PRINCIPLE_TITLES: Record<number, string> = {
  1: "Ethics & Transparency", 2: "Sustainable Products", 3: "Employee Well-being",
  4: "Stakeholder Responsiveness", 5: "Human Rights", 6: "Environment",
  7: "Policy Advocacy", 8: "Inclusive Growth", 9: "Consumer Responsibility",
};

export function emptyDrafts(): PrincipleDrafts {
  const out: PrincipleDrafts = {};
  for (let n = 1; n <= 9; n++) out[n] = { highlight: "", intro: "", sdgs: [] };
  return out;
}

interface Props {
  value: PrincipleDrafts;
  onChange: (next: PrincipleDrafts) => void;
  sdgs: SdgLabel[];
  written: Record<string, boolean>; // from completeness
}

export default function PrincipleNarrativesEditor({ value, onChange, sdgs, written }: Props) {
  const [active, setActive] = useState(1);
  const draft = value[active];

  const update = (patch: Partial<PrincipleDraft>) =>
    onChange({ ...value, [active]: { ...draft, ...patch } });

  const toggleSdg = (n: number) =>
    update({
      sdgs: draft.sdgs.includes(n)
        ? draft.sdgs.filter((s) => s !== n)
        : [...draft.sdgs, n].sort((a, b) => a - b),
    });

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        {Array.from({ length: 9 }, (_, i) => i + 1).map((n) => (
          <button
            key={n}
            type="button"
            onClick={() => setActive(n)}
            className={`px-3 py-1.5 rounded-md text-sm border ${
              active === n
                ? "bg-emerald-600 text-white border-emerald-600"
                : "bg-white text-gray-700 border-gray-300 hover:bg-gray-50"
            }`}
          >
            P{n}
            <span className={`ml-1 ${written[String(n)] ? "text-emerald-300" : "text-amber-400"}`}>
              {written[String(n)] ? "\u2713" : "\u25CF"}
            </span>
          </button>
        ))}
      </div>

      <h3 className="font-semibold text-gray-800">
        Principle {active} {"\u2014"} {PRINCIPLE_TITLES[active]}
      </h3>

      <label className="block text-sm">
        <span className="text-gray-700">Highlight (one line, shown large under the heading)</span>
        <input
          className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2"
          value={draft.highlight}
          onChange={(e) => update({ highlight: e.target.value })}
          placeholder="e.g. 12% reduction in Scope 2 emissions"
        />
      </label>

      <label className="block text-sm">
        <span className="text-gray-700">Introduction</span>
        <textarea
          className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2"
          rows={5}
          value={draft.intro}
          onChange={(e) => update({ intro: e.target.value })}
        />
      </label>

      <div>
        <span className="text-sm text-gray-700">Linked SDGs</span>
        <div className="mt-2 flex flex-wrap gap-2">
          {sdgs.map((s) => {
            const on = draft.sdgs.includes(s.number);
            return (
              <button
                key={s.number}
                type="button"
                onClick={() => toggleSdg(s.number)}
                title={s.label}
                className={`px-2 py-1 rounded-full text-xs border ${
                  on ? "bg-emerald-100 border-emerald-500 text-emerald-800"
                     : "bg-white border-gray-300 text-gray-600 hover:bg-gray-50"
                }`}
              >
                {s.number}. {s.label}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
