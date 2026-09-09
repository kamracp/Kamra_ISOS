import { useEnergyBalance } from "../hooks/usePatEnergy";

const n = (v: number | null | undefined, d = 2) => (v === null || v === undefined ? "--" : v.toLocaleString("en-IN", { maximumFractionDigits: d }));

/** ISO 50001 energy review for one unit-year, in BEE PAT's own split:
 *  thermal SEC (Gcal/t), electrical SEC (kWh/t), overall (GJ/t, toe/t). */
export default function EnergyBalancePanel({ unitId, year }: { unitId: number; year: number }) {
  const { data, isLoading, isError } = useEnergyBalance(unitId, year);
  if (isLoading) return <div className="rounded-xl border bg-white p-6 text-gray-500">Loading energy balance...</div>;
  if (isError || !data) return <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-red-600">Unable to load energy balance.</div>;
  const t = data.year_totals;
  const calc = data.periods.filter((p) => p.status === "calculated");
  const fuels = new Map<string, { name: string; biogenic: boolean; tonnes: number; gj: number; co2e: number }>();
  for (const p of calc) for (const f of p.by_fuel ?? []) {
    const row = fuels.get(f.fuel_key) ?? { name: f.fuel_name ?? f.fuel_key, biogenic: f.is_biogenic, tonnes: 0, gj: 0, co2e: 0 };
    row.tonnes += f.tonnes; row.gj += f.energy_gj; row.co2e += f.scope1_co2e_kg; fuels.set(f.fuel_key, row);
  }
  const elecGj = t.electricity_kwh * 0.0036;
  const share = (gj: number) => (t.total_energy_gj > 0 ? `${((gj / t.total_energy_gj) * 100).toFixed(1)}%` : "--");

  return (
    <div className="space-y-5 rounded-xl border bg-white p-6 shadow-sm">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-800">{year} Energy Balance (ISO 50001 energy review)</h2>
          <p className="text-sm text-gray-500">Electricity + fuel records; utility bills only as fallback. 1 toe = 41.868 GJ.</p>
        </div>
        {t.pat_dc_threshold_toe !== null && (
          <span className={`rounded-full px-3 py-1 text-sm font-medium ${t.is_designated_consumer_scale ? "bg-amber-100 text-amber-800" : "bg-gray-100 text-gray-600"}`}>
            {t.is_designated_consumer_scale ? "Above" : "Below"} PAT DC threshold ({n(t.pat_dc_threshold_toe, 0)} toe/yr)
          </span>
        )}
      </div>

      {calc.length === 0 ? (
        <p className="text-sm text-gray-500">No energy data for any {year} production period. Add electricity and fuel records for this unit.</p>
      ) : (
        <>
          <div className="grid grid-cols-2 gap-4 md:grid-cols-5">
            {[
              ["Total energy", `${n(t.total_energy_gj, 0)} GJ`, `${n(t.total_energy_toe, 1)} toe`],
              ["Overall SEC", `${n(t.sec_gj_per_unit, 4)} GJ/t`, `${n(t.sec_toe_per_unit, 5)} toe/t`],
              ["Thermal SEC", `${n(t.thermal_sec_gcal_per_unit, 4)} Gcal/t`, `${n(t.thermal_gj, 0)} GJ · ${share(t.thermal_gj)}`],
              ["Electrical SEC", `${n(t.electrical_sec_kwh_per_unit, 2)} kWh/t`, `${n(elecGj, 0)} GJ · ${share(elecGj)}`],
              ["Scope 1 combustion", `${n(t.scope1_combustion_co2e_kg / 1000, 1)} tCO₂e`, "IPCC 2006, AR5"],
            ].map(([k, v, s]) => (
              <div key={k} className="rounded-lg bg-gray-50 p-4">
                <p className="text-xs uppercase tracking-wide text-gray-400">{k}</p>
                <p className="mt-1 text-lg font-semibold text-gray-800">{v}</p>
                <p className="text-xs text-gray-500">{s}</p>
              </div>
            ))}
          </div>

          <table className="w-full text-sm">
            <thead><tr className="border-b text-left text-gray-500">
              <th className="py-2">Energy source</th><th className="py-2 text-right">Quantity</th><th className="py-2 text-right">Energy (GJ)</th><th className="py-2 text-right">Share</th><th className="py-2 text-right">Scope 1 (tCO₂e)</th>
            </tr></thead>
            <tbody>
              <tr className="border-b"><td className="py-2">Electricity{t.electricity_kwh > 0 && <span className="ml-1 text-xs text-gray-400">(Scope 2, see Electricity page)</span>}</td>
                <td className="py-2 text-right">{n(t.electricity_kwh, 0)} kWh</td><td className="py-2 text-right">{n(elecGj, 0)}</td><td className="py-2 text-right">{share(elecGj)}</td><td className="py-2 text-right text-gray-400">--</td></tr>
              {[...fuels.values()].map((f) => (
                <tr key={f.name} className="border-b"><td className="py-2">{f.name}{f.biogenic && <span className="ml-1 rounded bg-green-100 px-1.5 py-0.5 text-xs text-green-700">biogenic</span>}</td>
                  <td className="py-2 text-right">{n(f.tonnes, 2)} t</td><td className="py-2 text-right">{n(f.gj, 0)}</td><td className="py-2 text-right">{share(f.gj)}</td><td className="py-2 text-right">{n(f.co2e / 1000, 2)}</td></tr>
              ))}
              <tr className="bg-gray-50 font-semibold"><td className="py-2">Total</td><td /><td className="py-2 text-right">{n(t.total_energy_gj, 0)}</td><td className="py-2 text-right">100%</td><td className="py-2 text-right">{n(t.scope1_combustion_co2e_kg / 1000, 2)}</td></tr>
            </tbody>
          </table>

          {calc.length > 1 && (
            <p className="text-xs text-gray-500">{calc.length} production periods aggregated; per-period SEC available in the API (/pat-energy/energy-balance).</p>
          )}
        </>
      )}
      {data.periods_without_energy_data.length > 0 && (
        <p className="text-xs text-amber-700">Periods without energy data: {data.periods_without_energy_data.join(", ")}</p>
      )}
    </div>
  );
}
