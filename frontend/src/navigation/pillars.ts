import { Gauge, Leaf, Target, BarChart3, Boxes, type LucideIcon } from "lucide-react";
import type { Segment } from "../context/SegmentContext";

/**
 * Single source of truth for the five-pillar navigation. Sidebar, hub pages
 * and (later) the dashboard all read from here. Adding a page to a pillar is
 * one entry; no other file changes. Routes themselves live in router/index.tsx
 * and are unchanged by this map.
 */
export type PillarKey = "energy" | "carbon" | "netzero" | "esg" | "lca";
export type Status = "live" | "planned";

export interface PillarPage {
  title: string;
  path: string;
  description: string;
  status: Status;
  segment?: Segment; // only shown for that segment
}

export interface PillarReport {
  title: string;
  path?: string; // where it is generated today (undefined while planned)
  status: Status;
  formats: string;
}

export interface Pillar {
  key: PillarKey;
  number: number;
  title: string;
  shortTitle: string;
  hubPath: string;
  icon: LucideIcon;
  tagline: string;
  pages: PillarPage[];
  reports: PillarReport[];
}

export const PILLARS: Pillar[] = [
  {
    key: "energy", number: 1, title: "Energy Efficiency (BEE PAT)", shortTitle: "Energy Efficiency",
    hubPath: "/energy-efficiency", icon: Gauge,
    tagline: "Specific energy consumption, PAT cycle targets and the energy data every other pillar builds on.",
    pages: [
      { title: "Manufacturing Units", path: "/manufacturing-units", description: "Units, sectors, countries, PAT baselines.", status: "live", segment: "manufacturing" },
      { title: "Production Records", path: "/production-records", description: "Production quantity per unit per period.", status: "live", segment: "manufacturing" },
      { title: "Electricity (Scope 2)", path: "/manufacturing-electricity", description: "Grid and renewable electricity per unit, country-specific factors.", status: "live", segment: "manufacturing" },
      { title: "Fuels & Combustion", path: "/manufacturing-fuels", description: "Fuel burned per unit and period -- feeds thermal SEC, Scope 1 and P6 energy.", status: "live", segment: "manufacturing" },
      { title: "PAT Energy", path: "/pat-energy", description: "SEC per unit, cycle targets, gap to target.", status: "live", segment: "manufacturing" },
      { title: "Energy Dashboard", path: "/energy-efficiency/dashboard", description: "Organization energy balance, mix and per-unit SEC for a year.", status: "live" },
    ],
    reports: [{ title: "PAT SEC Report", status: "planned", formats: "PDF" }],
  },
  {
    key: "carbon", number: 2, title: "Carbon Accounting", shortTitle: "Carbon Accounting",
    hubPath: "/carbon-accounting", icon: Leaf,
    tagline: "Scope 1, 2 and 3 inventory on IPCC / DEFRA / CEA factors, plus CBAM embedded emissions.",
    pages: [
      { title: "Energy Meters", path: "/energy-meters", description: "Metered electricity, gas and fuel points.", status: "live" },
      { title: "Utility Bills", path: "/utility-bills", description: "Billed consumption per meter and period.", status: "live" },
      { title: "Scope 1 & 2 Summary", path: "/carbon", description: "Organisation-wide emissions by scope, unit and fuel.", status: "planned" },
      { title: "Scope 3", path: "/scope-3", description: "Fifteen GHG Protocol categories with materiality flags.", status: "planned" },
      { title: "CBAM", path: "/cbam", description: "Embedded emissions per tonne for EU CBAM goods.", status: "planned" },
    ],
    reports: [{ title: "GHG Inventory (GHG Protocol)", status: "planned", formats: "PDF" }],
  },
  {
    key: "netzero", number: 3, title: "Net Zero", shortTitle: "Net Zero",
    hubPath: "/net-zero-hub", icon: Target,
    tagline: "Targets, decarbonisation projects, marginal abatement cost and climate risk.",
    pages: [
      { title: "Targets & Projects", path: "/net-zero", description: "Net-zero targets, BAU vs target trajectory, projects and MACC.", status: "live" },
      { title: "Climate Risk (TCFD)", path: "/climate-risk", description: "Physical and transition risks with financial impact.", status: "live" },
    ],
    reports: [{ title: "Net Zero Roadmap", status: "planned", formats: "PDF" }],
  },
  {
    key: "esg", number: 4, title: "ESG Reporting", shortTitle: "ESG Reporting",
    hubPath: "/esg-hub", icon: BarChart3,
    tagline: "BRSR Sections A, B and C, GRI 305, ESRS E1, materiality and the filing validator.",
    pages: [
      { title: "BRSR Section A", path: "/brsr-profile", description: "General disclosures -- entity profile.", status: "live" },
      { title: "BRSR Section B", path: "/brsr-policy", description: "Management and process disclosures -- nine policies.", status: "live" },
      { title: "BRSR Section C", path: "/brsr-section-c", description: "Principle-wise performance -- all nine principles.", status: "live" },
      { title: "Water & Waste", path: "/water-waste", description: "Principle 6 water and waste disclosures.", status: "live" },
      { title: "ESG Reports & Validator", path: "/esg", description: "Framework reports, materiality, filing validator.", status: "live" },
      { title: "Report Studio", path: "/report-studio", description: "Cover, leadership message, milestones and principle narratives for the complete report.", status: "live" },
    ],
    reports: [
      { title: "GRI 305 / ESRS E1 / BRSR P6", path: "/esg", status: "live", formats: "JSON, PDF" },
      { title: "Complete Sustainability Report", path: "/report-studio", status: "live", formats: "PDF" },
    ],
  },
  {
    key: "lca", number: 5, title: "Product LCA", shortTitle: "Product LCA",
    hubPath: "/lca", icon: Boxes,
    tagline: "Cradle-to-gate product carbon footprint, circularity and export to openLCA / ILCD.",
    pages: [
      { title: "Products & BOM", path: "/lca/products", description: "Products, functional units, bills of materials.", status: "planned" },
      { title: "LCI Studio", path: "/lca/studies", description: "Inputs, outputs, allocation, stages.", status: "planned" },
      { title: "Scenarios & Benchmarks", path: "/lca/scenarios", description: "Renewable shift, avoided emissions, virgin benchmarks.", status: "planned" },
      { title: "Circularity (MCI)", path: "/lca/circularity", description: "Material circularity per product.", status: "planned" },
    ],
    reports: [{ title: "Product LCA (PLCA) Report", status: "planned", formats: "PDF, openLCA JSON-LD" }],
  },
];

export interface SettingsPage { title: string; path: string; segment?: Segment }

export const SETTINGS_PAGES: SettingsPage[] = [
  { title: "Organization", path: "/organizations" },
  { title: "Departments", path: "/departments" },
  { title: "Buildings", path: "/buildings", segment: "benas" },
  { title: "Floors", path: "/floors", segment: "benas" },
  { title: "HVAC", path: "/hvac", segment: "benas" },
  { title: "Tenant Billing", path: "/tenant-billing", segment: "benas" },
  { title: "Electrical", path: "/electrical", segment: "benas" },
  { title: "Water", path: "/water", segment: "benas" },
];

/** Which pillar a path belongs to -- used to highlight the pillar while on one of its pages. */
export function pillarForPath(pathname: string): PillarKey | null {
  for (const p of PILLARS) {
    if (pathname === p.hubPath || pathname.startsWith(p.hubPath + "/")) return p.key;
    if (p.pages.some((pg) => pathname === pg.path || pathname.startsWith(pg.path + "/"))) return p.key;
  }
  // Section C principle pages are not listed individually but belong to ESG.
  const esgExtra = ["/ethics", "/sustainable-products", "/employee-wellbeing", "/stakeholder-engagement",
    "/human-rights", "/policy-advocacy", "/csr", "/consumer-responsibility"];
  if (esgExtra.some((p) => pathname.startsWith(p))) return "esg";
  return null;
}
