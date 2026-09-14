import { useMemo, useState } from "react";
import { useCarbonSummary } from "../hooks/useCarbonSummary";
import type { CarbonLineItem } from "../api/carbonApi";

// Null renders as "-", never 0: a bill without a factor must stay visibly uncomputed.
const fmt = (v: number | null | undefined, d = 3) =>
  v == null ? "-" : v.toLocaleString(undefined, { maximumFractionDigits: d });
const toT = (kg: number | null | undefined) => (kg == null ? null : kg / 1000);

const SCOPE_LABEL: Record<string, string> = {
  scope1: "Scope 1 (direct)",
  scope_1: "Scope 1 (direct)",
  scope2: "Scope 2 (purchased energy)",
  scope_2: "Scope 2 (purchased energy)",
  renewable: "Renewable (avoided)",
};
const scopeLabel = (s: string) => SCOPE_LABEL[s] ?? s;

const YEARS = Array.from({ length: 7 }, (_, i) => new Date().getFullYear() - 4 + i);
const CARD = "rounded-lg border border-gray-200 bg-white p-4";
const TH = "p-2";
const TD = "p-2";

interface Group {
  key: string;
  label: string;
  sub?: string;
  scope: string;
  consumption: number;
  unit: string;
  co2e_kg: number;
  bills: number;
}

// Group calculated line items by an arbitrary key. Consumption is only summed when every
// bill in the group reports the same unit; a mixed group shows "mixed" rather than a wrong number.
function groupBy(items: CarbonLineItem[], keyOf: (i: CarbonLineItem) => string, label: (i: CarbonLineItem) => string, sub?: (i: CarbonLineItem) => string): Group[] {
  const map = new Map<string, Group & { units: Set<string> }>();
  for (const i of items) {
    if (i.status !== "calculated" || i.co2e_kg == null) continue;
    const k = keyOf(i);
    const g = map.get(k) ?? { key: k, label: label(i), sub: sub?.(i), scope: i.scope, consumption: 0, unit: i.unit, co2e_kg: 0, bills: 0, units: new Set<string>() };
    g.consumption += i.consumption;
    g.co2e_kg += i.co2e_kg;
    g.bills += 1;
    g.units.add(i.unit);
    map.set(k, g);
  }
  return [...map.values()]
    .map(({ units, ...g }) => ({ ...g, unit: units.size === 1 ? g.unit : "mixed" }))
    .sort((a, b) => b.co2e_kg - a.co2e_kg);
}

function GroupTable({ title, rows, subHeader }: { title: string; rows: Group[]; subHeader?: string }) {
  return (
    <div className="overflow-hidden rounded-lg border border-gray-200 bg-white">
      <div className="border-b border-gray-200 px-3 py-2 text-sm font-medium">{title}</div>
      <table className="w-full text-sm">
        <thead className="bg-gray-50 text-left text-xs text-gray-500">
          <tr>
            <th className={TH}>Name</th>
            {subHeader && <th className={TH}>{subHeader}</th>}
            <th className={TH}>Scope</th>
            <th className={`${TH} text-right`}>Consumption</th>
            <th className={TH}>Unit</th>
            <th className={`${TH} text-right`}>tCO2e</th>
            <th className={`${TH} text-right`}>Bills</th>
          </tr>
        </thead>
        <tbody>
          {rows.length === 0 && <tr><td className="p-3 text-gray-500" colSpan={7}>No calculated bills in this period.</td></tr>}
          {rows.map((r) => (
            <tr key={r.key} className="border-t border-gray-100">
              <td className={TD}>{r.label}</td>
              {subHeader && <td className={`${TD} text-gray-500`}>{r.sub ?? "-"}</td>}
              <td className={`${TD} text-gray-500`}>{scopeLabel(r.scope)}</td>
              <td className={`${TD} text-right`}>{fmt(r.unit === "mixed" ? null : r.consumption, 2)}</td>
              <td className={`${TD} text-gray-500`}>{r.unit}</td>
              <td className={`${TD} text-right font-medium`}>{fmt(toT(r.co2e_kg))}</td>
              <td className={`${TD} text-right text-gray-500`}>{r.bills}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function CarbonSummaryPage() {
  // "" = all bills (backend default); a number scopes to that calendar year.
  const [year, setYear] = useState<number | undefined>(undefined);
  const { data: s, isLoading, isError } = useCarbonSummary(year);

  const byUnit = useMemo(() => groupBy(s?.line_items ?? [], (i) => String(i.meter_id), (i) => i.meter_name, (i) => i.meter_code), [s]);
  const byFuel = useMemo(() => groupBy(s?.line_items ?? [], (i) => i.meter_type, (i) => i.meter_type), [s]);
  // Scope 1 and 2 cards always render (0 when no bills) — visible zero, never silently missing.
  // Any additional scope keys the backend returns are appended after them.
  const scopeRows = useMemo(() => {
    const raw = s?.by_scope_kg ?? {};
    const find = (n: string) => Object.entries(raw).find(([k]) => k.replace("_", "") === `scope${n}`);
    const fixed: [string, number][] = [find("1") ?? ["scope1", 0], find("2") ?? ["scope2", 0]];
    const extra = Object.entries(raw).filter(([k]) => !fixed.some(([f]) => f === k));
    return [...fixed, ...extra];
  }, [s]);
  const pending = s?.bills_pending_factor ?? [];
  const periodLabel = year ? String(year) : "all years";

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-semibold">Scope 1 &amp; 2 Summary</h1>
          <p className="text-sm text-gray-500">Organisation-wide emissions by scope, unit and fuel — computed from utility bills and the official factor library.</p>
        </div>
        <select className="rounded-md border border-gray-300 px-3 py-2 text-sm" value={year ?? ""} onChange={(e) => setYear(e.target.value === "" ? undefined : Number(e.target.value))}>
          <option value="">All years</option>
          {YEARS.map((y) => <option key={y} value={y}>{y}</option>)}
        </select>
      </div>

      {isError && <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">Could not load carbon summary.</div>}

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
        <div className={CARD}><div className="text-xs text-gray-500">Total Scope 1 + 2</div><div className="text-2xl font-semibold">{fmt(s?.total_co2e_tonnes)}</div><div className="text-xs text-gray-500">tCO2e, {periodLabel}</div></div>
        {scopeRows.map(([k, kg]) => (
          <div key={k} className={CARD}><div className="text-xs text-gray-500">{scopeLabel(k)}</div><div className="text-2xl font-semibold">{fmt(toT(kg))}</div><div className="text-xs text-gray-500">tCO2e</div></div>
        ))}
        <div className={CARD}><div className="text-xs text-gray-500">Avoided (renewable)</div><div className="text-2xl font-semibold">{fmt(toT(s?.avoided_co2e_kg))}</div><div className="text-xs text-gray-500">tCO2e, not netted from total</div></div>
        <div className={CARD}><div className="text-xs text-gray-500">Bills</div><div className="text-2xl font-semibold">{s ? s.bills_calculated : "-"}<span className="text-sm font-normal text-gray-500"> calculated</span></div><div className={`text-xs ${pending.length ? "text-amber-600" : "text-gray-500"}`}>{s ? `${pending.length} pending factor` : ""}</div></div>
      </div>

      {pending.length > 0 && (
        <div className="rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800">
          <div className="font-medium">{pending.length} bill(s) have no matching emission factor and are excluded from every total above.</div>
          <div className="mt-1 text-xs">Add a factor for: {[...new Set(pending.map((p) => p.meter_type))].join(", ")}</div>
        </div>
      )}

      {isLoading && <div className="text-sm text-gray-500">Loading...</div>}

      <div className="grid gap-4 lg:grid-cols-2">
        <GroupTable title="By unit (meter)" rows={byUnit} subHeader="Code" />
        <GroupTable title="By fuel / energy carrier" rows={byFuel} />
      </div>

      <div className="overflow-hidden rounded-lg border border-gray-200 bg-white">
        <div className="border-b border-gray-200 px-3 py-2 text-sm font-medium">Bill-level audit trail</div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-left text-xs text-gray-500">
              <tr>
                <th className={TH}>Period</th><th className={TH}>Meter</th><th className={TH}>Type</th><th className={TH}>Scope</th>
                <th className={`${TH} text-right`}>Consumption</th><th className={TH}>Unit</th>
                <th className={`${TH} text-right`}>Factor</th><th className={TH}>Source</th>
                <th className={`${TH} text-right`}>tCO2e</th><th className={TH}>Status</th>
              </tr>
            </thead>
            <tbody>
              {(s?.line_items ?? []).length === 0 && !isLoading && <tr><td className="p-3 text-gray-500" colSpan={10}>No bills in this period.</td></tr>}
              {(s?.line_items ?? []).map((i) => (
                <tr key={i.bill_id} className="border-t border-gray-100">
                  <td className={`${TD} whitespace-nowrap text-gray-500`}>{i.period_start} → {i.period_end}</td>
                  <td className={TD}>{i.meter_name} <span className="text-xs text-gray-400">{i.meter_code}</span></td>
                  <td className={TD}>{i.meter_type}</td>
                  <td className={`${TD} text-gray-500`}>{scopeLabel(i.scope)}</td>
                  <td className={`${TD} text-right`}>{fmt(i.consumption, 2)}</td>
                  <td className={`${TD} text-gray-500`}>{i.unit}</td>
                  <td className={`${TD} text-right`}>{fmt(i.factor_value, 5)}</td>
                  <td className={`${TD} max-w-xs truncate text-xs text-gray-500`} title={i.factor_source ?? ""}>{i.factor_source ?? "-"}</td>
                  <td className={`${TD} text-right font-medium`}>{fmt(toT(i.co2e_kg))}</td>
                  <td className={TD}><span className={`rounded px-2 py-0.5 text-xs ${i.status === "calculated" ? "bg-emerald-100 text-emerald-700" : "bg-amber-100 text-amber-700"}`}>{i.status === "calculated" ? "calculated" : "no factor"}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
