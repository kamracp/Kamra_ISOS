import { useState } from "react";
import { useBrsrPrinciple6 } from "./hooks/useEsgReport";
import type { Datapoint } from "./api/esgReportApi";

function DatapointCell({ dp }: { dp?: Datapoint }) {
  if (!dp) return <span className="text-gray-400">—</span>;
  if (dp.status === "not_tracked") {
    return (
      <span className="inline-flex items-center rounded-full bg-amber-50 px-2.5 py-0.5 text-xs font-medium text-amber-700">
        To be collected
      </span>
    );
  }
  return (
    <div>
      <span className="font-semibold text-gray-900">
        {dp.value} {dp.unit}
      </span>
      {dp.source && (
        <div className="mt-0.5 text-xs text-gray-400">{dp.source}</div>
      )}
    </div>
  );
}

export default function ESGReportPage() {
  const [year, setYear] = useState(2024);
  const { data: report, isLoading } = useBrsrPrinciple6(year);

  return (
    <div className="mx-auto max-w-4xl space-y-6 p-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-800">ESG Report</h1>
        <p className="mt-1 text-sm text-gray-500">
          BRSR (Business Responsibility &amp; Sustainability Report) — SEBI
        </p>
      </div>

      <div className="flex items-center gap-3">
        <label className="text-sm font-medium text-gray-700">
          Reporting Year
        </label>
        <select
          value={year}
          onChange={(e) => setYear(Number(e.target.value))}
          className="rounded-lg border border-gray-300 px-3 py-1.5 text-sm focus:border-blue-500 focus:outline-none"
        >
          {[2022, 2023, 2024, 2025, 2026].map((y) => (
            <option key={y} value={y}>
              {y}
            </option>
          ))}
        </select>
      </div>

      {isLoading && <p className="text-gray-500">Loading report…</p>}

      {report && (
        <div className="space-y-6">
          <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
            <h2 className="text-lg font-semibold text-gray-800">
              {report.section}
            </h2>
            <p className="mt-1 text-xs text-gray-500">{report.data_basis}</p>
            <div className="mt-4 rounded-lg bg-blue-50 p-4">
              <div className="text-sm text-gray-600">
                Total Scope 1 + 2 Emissions
              </div>
              <div className="mt-1 text-2xl font-bold text-blue-700">
                {report.totals.scope1_plus_2_tCO2e} tCO₂e
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-gray-200 bg-white shadow-sm">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-gray-50 text-left text-xs uppercase text-gray-500">
                  <th className="px-4 py-3">Indicator</th>
                  <th className="px-4 py-3">Value</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(report.essential_indicators).map(
                  ([key, ind]) => (
                    <tr key={key} className="border-b last:border-0">
                      <td className="px-4 py-3">
                        <div className="font-medium text-gray-800">
                          {ind.label}
                        </div>
                        {ind.note && (
                          <div className="mt-0.5 text-xs text-gray-400">
                            {ind.note}
                          </div>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        {ind.renewable_gj || ind.non_renewable_gj ? (
                          <div className="space-y-1">
                            <div>
                              Renewable: <DatapointCell dp={ind.renewable_gj} />
                            </div>
                            <div>
                              Non-renewable:{" "}
                              <DatapointCell dp={ind.non_renewable_gj} />
                            </div>
                          </div>
                        ) : (
                          <DatapointCell dp={ind.data} />
                        )}
                      </td>
                    </tr>
                  ),
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}