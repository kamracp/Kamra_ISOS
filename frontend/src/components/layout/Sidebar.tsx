import { NavLink } from "react-router-dom";
import {
  Building2,
  Factory,
  Users,
  Gauge,
  Zap,
  TrendingDown,
  Wind,
  Cpu,
  Droplets,
  Leaf,
  BarChart3,
  LayoutDashboard,
  Activity,
  Receipt,
  Layers,
  Boxes,
  ClipboardList,
  Target,
  AlertTriangle,
  FileText,
  ShieldCheck,
  Recycle,
} from "lucide-react";
import { useSegment, type Segment } from "../../context/SegmentContext";

interface MenuItem {
  title: string;
  icon: typeof LayoutDashboard;
  path: string;
  segment?: Segment;
}

const menu: MenuItem[] = [
  { title: "Dashboard", icon: LayoutDashboard, path: "/dashboard" },
  { title: "Organizations", icon: Building2, path: "/organizations" },
  { title: "Departments", icon: Users, path: "/departments" },
  { title: "Buildings", icon: Factory, path: "/buildings", segment: "benas" },
  { title: "Floors", icon: Layers, path: "/floors", segment: "benas" },
  { title: "HVAC", icon: Wind, path: "/hvac", segment: "benas" },
  { title: "Tenant Billing", icon: Receipt, path: "/tenant-billing", segment: "benas" },
  { title: "Electrical", icon: Cpu, path: "/electrical", segment: "benas" },
  { title: "Water", icon: Droplets, path: "/water", segment: "benas" },
  {
    title: "Manufacturing Units",
    icon: Boxes,
    path: "/manufacturing-units",
    segment: "manufacturing",
  },
  {
    title: "Production Records",
    icon: ClipboardList,
    path: "/production-records",
    segment: "manufacturing",
  },
  {
    title: "PAT Energy",
    icon: TrendingDown,
    path: "/pat-energy",
    segment: "manufacturing",
  },
  { title: "Energy Meters", icon: Activity, path: "/energy-meters" },
  { title: "Utility Bills", icon: Receipt, path: "/utility-bills" },
  { title: "Utilities", icon: Gauge, path: "/utilities" },
  { title: "Energy", icon: Zap, path: "/energy" },
  { title: "Carbon", icon: Leaf, path: "/carbon" },
  { title: "Net Zero", icon: Target, path: "/net-zero" },
  { title: "ESG Reports", icon: BarChart3, path: "/esg" },
  { title: "Climate Risk", icon: AlertTriangle, path: "/climate-risk" },
  { title: "BRSR Section A", icon: FileText, path: "/brsr-profile" },
  { title: "BRSR Section B", icon: ShieldCheck, path: "/brsr-policy" },
  { title: "Water & Waste", icon: Recycle, path: "/water-waste" },
];

// If VITE_APP_SEGMENT is set at build time, this deployment is locked to
// one product (Kamra BENAS or Kamra ManufactureOS) and the segment toggle
// is hidden. Unset (dev/default) falls back to the toggle-based combined UI.
const LOCKED_SEGMENT = import.meta.env.VITE_APP_SEGMENT as Segment | undefined;
const APP_TITLE =
  LOCKED_SEGMENT === "benas"
    ? "Kamra BENAS"
    : LOCKED_SEGMENT === "manufacturing"
      ? "Kamra ManufactureOS"
      : "Kamra ClimateOS";

export default function Sidebar() {
  const { segment: contextSegment, setSegment } = useSegment();
  const segment = LOCKED_SEGMENT ?? contextSegment;

  const visibleMenu = menu.filter(
    (item) => !item.segment || item.segment === segment
  );

  return (
    <aside className="w-72 bg-slate-900 text-white flex flex-col">
      <div className="border-b border-slate-700 p-6">
        <h1 className="text-2xl font-bold">{APP_TITLE}</h1>
        <p className="mt-1 text-xs text-slate-400">
          Kamra Engineering Solutions
        </p>
      </div>

      {!LOCKED_SEGMENT && (
      <div className="border-b border-slate-700 p-4">
       <p className="mb-2 inline-block rounded bg-blue-600/20 px-2 py-1 text-sm font-bold uppercase tracking-wider text-blue-300">
          Segment
        </p>

        <div className="flex gap-2">
          <button
            onClick={() => setSegment("benas")}
            className={`flex-1 rounded-lg px-3 py-2 text-sm font-medium transition ${
              segment === "benas"
                ? "bg-blue-600 text-white"
                : "bg-slate-800 text-slate-300 hover:bg-slate-700"
            }`}
          >
            BENAS
          </button>

          <button
            onClick={() => setSegment("manufacturing")}
            className={`flex-1 rounded-lg px-3 py-2 text-sm font-medium transition ${
              segment === "manufacturing"
                ? "bg-blue-600 text-white"
                : "bg-slate-800 text-slate-300 hover:bg-slate-700"
            }`}
          >
            Manufacturing
          </button>
        </div>
      </div>
      )}


      <nav className="flex-1 overflow-y-auto p-4">
        <div className="space-y-2">
          {visibleMenu.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-lg px-4 py-3 transition ${
                    isActive
                      ? "bg-blue-600 text-white"
                      : "text-slate-300 hover:bg-slate-800 hover:text-white"
                  }`
                }
              >
                <Icon size={20} />
                <span>{item.title}</span>
              </NavLink>
            );
          })}
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
