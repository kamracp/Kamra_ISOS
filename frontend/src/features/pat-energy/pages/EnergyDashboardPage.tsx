import { useState } from "react";
import { Link } from "react-router-dom";
import { useOrgEnergy } from "../hooks/usePatEnergy";

const n = (v: number | null | undefined, d = 0) => (v === null || v === undefined ? "--" : v.toLocaleString("en-IN", { maximumFractionDigits: d }));

/** Pillar 1 dashboard: organization energy for a year from the shared
 *  energy balance -- totals, mix, and one row per unit. */
export default function EnergyDashboardPage() {
  const [year, setYear] = useState(new Date().getFullYear());
  const { data, isLoading, isError } = useOrgEnergy(year);

  return (
    <div className="space-y-6 p-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Energy Dashboard</h1>
          <p className="text-gray-500">Organization energy balance from electricity and fuel records. 1 toe = 41.868 GJ.</p>
        </div>
        <input type="number" className="w-28 rounded-lg border border-gray-300 px-3 py-2" value={year} onChange={(e) => setYear(Number(e.target.value))} />
      </div>

      {isLoading && <div className="p-10 text-center text-gray-500">Loading...</div>}
      {isError && <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-red-600">Unable to load energy data.</div>}
      {data && (() => {
        const t = data.totals;
        const mix: [string, number, string][] = [
          ["Grid electricity", t.electrical_gj - t.renewable_kwh * 0.0036, "bg-slate-500"],
          ["Renewable electricity", t.renewable_kwh * 0.0036, "bg-green-500"],
          ["Fossil fuels", t.thermal_gj - t.biomass_gj, "bg-orange-500"],
          ["Biomass fuels", t.biomass_gj, "bg-lime-500"],
        ];
        const pct = (v: number) => (t.total_gj > 0 ? (v / t.total_gj) * 100 : 0);
        return (
          <>
            <div className="grid grid-cols-2 gap-4 md:grid-cols-5">
              {[
                ["Total energy", `${n(t.total_gj)} GJ`, `${n(t.total_toe, 1)} toe`],
                ["Renewable", `${n(t.renewable_gj)} GJ`, t.total_gj > 0 ? `${((t.renewable_gj / t.total_gj) * 100).toFixed(1)}% of total` : ""],
                ["Electricity", `${n(t.electricity_kwh)} kWh`, `${n(t.electrical_gj)} GJ`],
                ["Fuels (thermal)", `${n(t.thermal_gj)} GJ`, `${Object.keys(t.by_fuel_gj).length} fuel types`],
                ["Coverage", `${t.units_with_data} / ${data.units.length} units`, `${t.record_count} records`],
              ].map(([k, v, s]) => (
                <div key={k} className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
                  <p className="text-xs uppercase tracking-wide text-gray-400">{k}</p>
                  <p className="mt-1 text-xl font-semibold text-gray-800">{v}</p>
                  <p className="text-xs text-gray-500">{s}</p>
                </div>
              ))}
            </div>

            <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
              <h2 className="mb-3 font-semibold text-gray-800">Energy mix</h2>
              {t.total_gj > 0 ? (
                <>
                  <div className="flex h-5 w-full overflow-hidden rounded-full bg-gray-100">
                    {mix.map(([k, v, c]) => v > 0 && <div key={k} className={c} style={{ width: `${pct(v)}%` }} title={`${k}: ${n(v)} GJ`} />)}
                  </div>
                  <div className="mt-3 flex flex-wrap gap-4 text-sm">
                    {mix.map(([k, v, c]) => <span key={k} className="flex items-center gap-2"><span className={`h-3 w-3 rounded-sm ${c}`} />{k}: {n(v)} GJ ({pct(v).toFixed(1)}%)</span>)}
                  </div>
                </>
              ) : <p className="text-sm text-gray-500">No records for {year}.</p>}
            </div>

            <div className="overflow-x-auto rounded-xl border bg-white shadow-sm">
              <table className="w-full text-sm">
                <thead><tr className="border-b bg-gray-50 text-left text-gray-500">
                  <th className="px-4 py-3">Unit</th><th className="px-4 py-3">Sector</th><th className="px-4 py-3 text-right">Energy (GJ)</th><th className="px-4 py-3 text-right">toe</th>
                  <th className="px-4 py-3 text-right">Production</th><th className="px-4 py-3 text-right">SEC (GJ/t)</th><th className="px-4 py-3 text-right">Renewable</th><th className="px-4 py-3 text-right">Scope 1 fuel (t)</th><th className="px-4 py-3">PAT DC</th><th className="px-4 py-3">Basis</th>
                </tr></thead>
                <tbody>
                  {data.units.map((u) => (
                    <tr key={u.manufacturing_unit_id} className="border-b">
                      <td className="px-4 py-3 font-medium"><Link to="/pat-energy" className="hover:underline">{u.unit_name}</Link> <span className="text-xs text-gray-400">{u.country_code}</span></td>
                      <td className="px-4 py-3 text-gray-500">{u.sector}</td>
                      <td className="px-4 py-3 text-right">{n(u.total_energy_gj)}</td>
                      <td className="px-4 py-3 text-right">{n(u.total_energy_toe, 1)}</td>
                      <td className="px-4 py-3 text-right">{u.production_quantity ? `${n(u.production_quantity)} ${u.production_unit ?? ""}` : "--"}</td>
                      <td className="px-4 py-3 text-right">{n(u.sec_gj_per_unit, 3)}</td>
                      <td className="px-4 py-3 text-right">{u.renewable_share_percent === null ? "--" : `${u.renewable_share_percent}%`}</td>
                      <td className="px-4 py-3 text-right">{n(u.scope1_combustion_co2e_kg / 1000, 1)}</td>
                      <td className="px-4 py-3">{u.pat_dc_threshold_toe === null ? <span className="text-gray-400">n/a</span> : u.is_designated_consumer_scale ? <span className="rounded bg-amber-100 px-2 py-0.5 text-xs text-amber-800">above {n(u.pat_dc_threshold_toe)} toe</span> : <span className="rounded bg-gray-100 px-2 py-0.5 text-xs text-gray-600">below {n(u.pat_dc_threshold_toe)} toe</span>}</td>
                      <td className="px-4 py-3 text-xs text-gray-500">{u.source_basis}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        );
      })()}
    </div>
  );
}
