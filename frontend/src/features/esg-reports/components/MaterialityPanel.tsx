import { useState } from "react";
import { SASB_MATERIAL_TOPICS } from "../data/sasbMaterialTopics";
import type { PatSector } from "../../manufacturing-units/api/manufacturingUnitApi";

const SECTOR_LABELS: Record<PatSector, string> = {
  aluminium: "Aluminium",
  cement: "Cement",
  chlor_alkali: "Chlor-Alkali",
  fertilizer: "Fertilizer",
  iron_steel: "Iron & Steel",
  pulp_paper: "Pulp & Paper",
  textile: "Textile",
  thermal_power: "Thermal Power",
  refineries: "Refineries",
  railways: "Railways",
  discoms: "DISCOMs",
  petrochemicals: "Petrochemicals",
  other: "Other",
};

const SECTOR_ORDER: PatSector[] = [
  "cement", "aluminium", "iron_steel", "pulp_paper", "chlor_alkali",
  "fertilizer", "petrochemicals", "refineries", "thermal_power",
  "textile", "discoms", "railways", "other",
];

export default function MaterialityPanel() {
  const [sector, setSector] = useState<PatSector>("cement");
  const topics = SASB_MATERIAL_TOPICS[sector];

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h3 className="text-sm font-semibold text-gray-800">
            Materiality Focus by Industry
          </h3>
          <p className="text-xs text-gray-400">
            Informational reference, not a calculation input.
          </p>
        </div>
        <select
          value={sector}
          onChange={(e) => setSector(e.target.value as PatSector)}
          className="rounded-lg border border-gray-300 px-3 py-1.5 text-sm focus:border-blue-500 focus:outline-none"
        >
          {SECTOR_ORDER.map((s) => (
            <option key={s} value={s}>
              {SECTOR_LABELS[s]}
            </option>
          ))}
        </select>
      </div>
      <ul className="mt-3 space-y-1.5">
        {topics.map((t) => (
          <li key={t.topic} className="flex items-center justify-between text-sm">
            <span className="text-gray-700">{t.topic}</span>
            <span
              className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                t.priority === "High"
                  ? "bg-red-50 text-red-700"
                  : "bg-amber-50 text-amber-700"
              }`}
            >
              {t.priority}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
