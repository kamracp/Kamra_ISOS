import { useState } from "react";
import toast from "react-hot-toast";
import { useEsgReport, useEsgTrend } from "./hooks/useEsgReport";
import esgReportApi, {
  type Datapoint,
  type ReportFramework,
  REPORT_FRAMEWORK_LABELS,
} from "./api/esgReportApi";
import { useCountries } from "../countries/hooks/useCountries";
import CountrySelector from "../countries/components/CountrySelector";
import MaterialityPanel from "./components/MaterialityPanel";

const FRAMEWORK_ORDER: ReportFramework[] = ["gri-305", "esrs-e1", "brsr"];

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
  const [framework, setFramework] = useState<ReportFramework>("gri-305");
  const [year, setYear] = useState(2024);
  const [countryCode, setCountryCode] = useState("IN");
  const [downloading, setDownloading] = useState(false);

  const { data: report, isLoading } = useEsgReport(framework, year);
  const { data: countries } = useCountries();
  const { data: trendReport } = useEsgTrend([2022, 2023, 2024]);

  const selectedCountry = countries?.find((c) => c.code === countryCode);

  const handleDownloadPdf = async () => {
    setDownloading(true);
    try {
      await esgReportApi.downloadReportPdf(framework, year);
    } catch {
      toast.error("Could not download the PDF. Please try again.");
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className="mx-auto max-w-4xl space-y-6 p-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-800">ESG Report</h1>
        <p className="mt-1 text-sm text-gray-500">
          Sustainability and emissions reporting, built from your own
          tracked utility-bill data.
        </p>
      </div>

      <div className="flex items-center gap-3">
        <label className="text-sm font-medium text-gray-700">
          Reporting Framework
        </label>
        <select
          value={framework}
          onChange={(e) => setFramework(e.target.value as ReportFramework)}
          className="rounded-lg border border-gray-300 px-3 py-1.5 text-sm focus:border-blue-500 focus:outline-none"
        >
          {FRAMEWORK_ORDER.map((fw) => (
            <option key={fw} value={fw}>
              {REPORT_FRAMEWORK_LABELS[fw]}
            </option>
          ))}
        </select>
      </div>

      <div className="flex flex-wrap items-end gap-6">
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

        <CountrySelector
          value={countryCode}
          onChange={setCountryCode}
          label="Reporting Jurisdiction"
        />

        <button
          onClick={handleDownloadPdf}
          disabled={downloading || !report}
          className="rounded-lg bg-blue-600 px-4 py-1.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {downloading ? "Preparing PDF…" : "Download PDF"}
        </button>
      </div>

<MaterialityPanel />

            {selectedCountry && (
        <div className="rounded-lg border border-gray-200 bg-gray-50 p-3 text-xs text-gray-600">
          <span className="font-medium text-gray-700">
            {selectedCountry.name}
          </span>{" "}
          — Applicable standards: {selectedCountry.applicable_standards}
          {selectedCountry.grid_factor_kgco2e_per_kwh != null ? (
            <>
              {" "}
              · Grid factor: {selectedCountry.grid_factor_kgco2e_per_kwh}{" "}
              kgCO₂e/kWh ({selectedCountry.grid_factor_source})
            </>
          ) : (
            <span className="text-amber-700">
              {" "}
              · Grid factor not yet verified for this country
            </span>
          )}
          <div className="mt-1 italic text-gray-400">
            Note: the emissions below are calculated from your recorded
            utility bills and the platform's global factor library, not
            re-calculated using this country's grid factor. This selector
            currently sets display context (applicable standards) only.
          </div>
        </div>
      )}

      {isLoading && <p className="text-gray-500">Loading report…</p>}

      {report && (
        <div className="space-y-6">
          <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
            <h2 className="text-lg font-semibold text-gray-800">
              {report.framework} — {report.section}
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

          {trendReport && (
            <div className="rounded-xl border border-gray-200 bg-white shadow-sm">
              <div className="border-b px-4 py-3">
                <h3 className="text-sm font-semibold text-gray-800">
                  Multi-Year Emissions Trend
                </h3>
              </div>
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b bg-gray-50 text-left text-xs uppercase text-gray-500">
                    <th className="px-4 py-3">Year</th>
                    <th className="px-4 py-3">Scope 1 (tCO2e)</th>
                    <th className="px-4 py-3">Scope 2 (tCO2e)</th>
                    <th className="px-4 py-3">Scope 1+2 (tCO2e)</th>
                  </tr>
                </thead>
                <tbody>
                  {trendReport.trend.map((entry) => (
                    <tr key={entry.year} className="border-b last:border-0">
                      <td className="px-4 py-3 font-medium text-gray-800">
                        {entry.year}
                      </td>
                      <td className="px-4 py-3">
                        {entry.scope1_tco2e ?? (
                          <span className="text-gray-400">—</span>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        {entry.scope2_tco2e ?? (
                          <span className="text-gray-400">—</span>
                        )}
                      </td>
                      <td className="px-4 py-3 font-semibold text-blue-700">
                        {entry.scope1_plus_2_tco2e ?? (
                          <span className="text-gray-400">—</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}