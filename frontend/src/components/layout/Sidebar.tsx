import { useState } from "react";
import { NavLink, useLocation } from "react-router-dom";
import { LayoutDashboard, Settings, ChevronDown, ChevronRight } from "lucide-react";
import { useSegment, type Segment } from "../../context/SegmentContext";
import { PILLARS, SETTINGS_PAGES, pillarForPath } from "../../navigation/pillars";

// If VITE_APP_SEGMENT is set at build time, this deployment is locked to
// one product (Kamra BENAS or Kamra ManufactureOS) and the segment toggle
// is hidden. Unset (dev/default) falls back to the toggle-based combined UI.
const LOCKED_SEGMENT = import.meta.env.VITE_APP_SEGMENT as Segment | undefined;
const APP_TITLE =
  LOCKED_SEGMENT === "benas" ? "Kamra BENAS"
  : LOCKED_SEGMENT === "manufacturing" ? "Kamra ManufactureOS"
  : "Kamra ClimateOS";

const linkCls = (active: boolean) =>
  `flex items-center gap-3 rounded-lg px-4 py-3 transition ${active ? "bg-blue-600 text-white" : "text-slate-300 hover:bg-slate-800 hover:text-white"}`;

export default function Sidebar() {
  const { segment: contextSegment, setSegment } = useSegment();
  const segment = LOCKED_SEGMENT ?? contextSegment;
  const { pathname } = useLocation();
  const activePillar = pillarForPath(pathname);

  const settingsPages = SETTINGS_PAGES.filter((p) => !p.segment || p.segment === segment);
  const onSettingsPage = settingsPages.some((p) => pathname.startsWith(p.path));
  const [settingsOpen, setSettingsOpen] = useState(onSettingsPage);

  return (
    <aside className="w-72 bg-slate-900 text-white flex flex-col">
      <div className="border-b border-slate-700 p-6">
        <h1 className="text-2xl font-bold">{APP_TITLE}</h1>
        <p className="mt-1 text-xs text-slate-400">Kamra Engineering Solutions</p>
      </div>

      {!LOCKED_SEGMENT && (
        <div className="border-b border-slate-700 p-4">
          <p className="mb-2 inline-block rounded bg-blue-600/20 px-2 py-1 text-sm font-bold uppercase tracking-wider text-blue-300">Segment</p>
          <div className="flex gap-2">
            {(["benas", "manufacturing"] as Segment[]).map((s) => (
              <button key={s} onClick={() => setSegment(s)}
                className={`flex-1 rounded-lg px-3 py-2 text-sm font-medium transition ${segment === s ? "bg-blue-600 text-white" : "bg-slate-800 text-slate-300 hover:bg-slate-700"}`}>
                {s === "benas" ? "BENAS" : "Manufacturing"}
              </button>
            ))}
          </div>
        </div>
      )}

      <nav className="flex-1 overflow-y-auto p-4">
        <div className="space-y-2">
          <NavLink to="/dashboard" className={({ isActive }) => linkCls(isActive)}>
            <LayoutDashboard size={20} /><span>Dashboard</span>
          </NavLink>

          <p className="px-4 pb-1 pt-4 text-xs font-semibold uppercase tracking-wider text-slate-500">Pillars</p>
          {PILLARS.map((p) => {
            const Icon = p.icon;
            // Active while on the hub OR any of the pillar's pages.
            const active = activePillar === p.key;
            return (
              <NavLink key={p.key} to={p.hubPath} className={linkCls(active)}>
                <Icon size={20} />
                <span className="flex-1">{p.shortTitle}</span>
                <span className="text-xs text-slate-500">{p.number}</span>
              </NavLink>
            );
          })}

          <button onClick={() => setSettingsOpen((o) => !o)}
            className={`mt-4 flex w-full items-center gap-3 rounded-lg px-4 py-3 text-left transition ${onSettingsPage ? "text-white" : "text-slate-300"} hover:bg-slate-800 hover:text-white`}>
            <Settings size={20} /><span className="flex-1">Settings</span>
            {settingsOpen ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
          </button>
          {settingsOpen && (
            <div className="ml-6 space-y-1 border-l border-slate-700 pl-3">
              {settingsPages.map((p) => (
                <NavLink key={p.path} to={p.path}
                  className={({ isActive }) => `block rounded px-3 py-2 text-sm transition ${isActive ? "bg-blue-600 text-white" : "text-slate-400 hover:bg-slate-800 hover:text-white"}`}>
                  {p.title}
                </NavLink>
              ))}
            </div>
          )}
        </div>
      </nav>

      <div className="border-t border-slate-700 p-5">
        <div className="rounded-lg bg-slate-800 p-4">
          <p className="text-sm font-semibold">Version</p>
          <p className="mt-1 text-xs text-slate-400">Kamra ClimateOS v0.1</p>
        </div>
      </div>
    </aside>
  );
}
