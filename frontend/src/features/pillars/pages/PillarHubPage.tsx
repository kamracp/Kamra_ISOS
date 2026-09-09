import { Link } from "react-router-dom";
import { Download, Lock } from "lucide-react";
import { PILLARS, type PillarKey } from "../../../navigation/pillars";
import { useSegment, type Segment } from "../../../context/SegmentContext";

const LOCKED_SEGMENT = import.meta.env.VITE_APP_SEGMENT as Segment | undefined;

/** One component renders all five pillar hubs from the PILLARS map. */
export default function PillarHubPage({ pillar: key }: { pillar: PillarKey }) {
  const pillar = PILLARS.find((p) => p.key === key)!;
  const { segment: contextSegment } = useSegment();
  const segment = LOCKED_SEGMENT ?? contextSegment;
  const pages = pillar.pages.filter((p) => !p.segment || p.segment === segment);
  const Icon = pillar.icon;

  return (
    <div className="space-y-8 p-8">
      <div className="flex items-start gap-4">
        <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-blue-600 text-white"><Icon size={24} /></span>
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-gray-400">Pillar {pillar.number}</p>
          <h1 className="text-3xl font-bold">{pillar.title}</h1>
          <p className="mt-1 text-gray-500">{pillar.tagline}</p>
        </div>
      </div>

      <section>
        <h2 className="mb-3 text-lg font-semibold text-gray-800">Data</h2>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {pages.map((pg) =>
            pg.status === "live" ? (
              <Link key={pg.path} to={pg.path}
                className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm transition hover:border-blue-400 hover:shadow-md">
                <h3 className="font-semibold text-gray-800">{pg.title}</h3>
                <p className="mt-1 text-sm text-gray-500">{pg.description}</p>
              </Link>
            ) : (
              <div key={pg.path} className="rounded-xl border border-dashed border-gray-300 bg-gray-50 p-5">
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold text-gray-500">{pg.title}</h3>
                  <span className="flex items-center gap-1 rounded bg-gray-200 px-2 py-0.5 text-xs font-medium text-gray-600"><Lock size={12} /> Planned</span>
                </div>
                <p className="mt-1 text-sm text-gray-400">{pg.description}</p>
              </div>
            ),
          )}
        </div>
      </section>

      <section>
        <h2 className="mb-3 text-lg font-semibold text-gray-800">Reports</h2>
        <div className="divide-y rounded-xl border border-gray-200 bg-white">
          {pillar.reports.map((r) => (
            <div key={r.title} className="flex items-center justify-between px-5 py-4">
              <div>
                <p className={`font-medium ${r.status === "live" ? "text-gray-800" : "text-gray-500"}`}>{r.title}</p>
                <p className="text-xs text-gray-400">{r.formats}</p>
              </div>
              {r.status === "live" && r.path ? (
                <Link to={r.path} className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700">
                  <Download size={16} /> Open
                </Link>
              ) : (
                <span className="rounded bg-gray-200 px-2 py-0.5 text-xs font-medium text-gray-600">Planned</span>
              )}
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
