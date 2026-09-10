import { useEffect, useMemo, useState } from "react";
import ObjectListField, { type ObjectRow } from "../../brsr-profile/components/ObjectListField";
import PrincipleNarrativesEditor, {
  emptyDrafts, type PrincipleDrafts,
} from "../components/PrincipleNarrativesEditor";
import {
  useDownloadCompletePdf, useNarrativeCompleteness, useNarrativeYears,
  useReportNarrative, useSaveNarrative, useSdgLabels,
} from "../hooks/useReportStudio";
import type { ReportNarrativeUpdate } from "../api/reportStudioApi";

type Tab = "cover" | "leadership" | "about" | "principles";
type Scalars = {
  cover_title: string; cover_subtitle: string; theme_colour: string;
  about_company: string; leadership_message: string;
  leadership_name: string; leadership_designation: string;
};
const EMPTY: Scalars = {
  cover_title: "", cover_subtitle: "", theme_colour: "#1A7F37", about_company: "",
  leadership_message: "", leadership_name: "", leadership_designation: "",
};
const MILESTONE_FIELDS = [
  { name: "year", label: "Year", type: "number" as const },
  { name: "title", label: "Milestone" },
  { name: "description", label: "Detail" },
];
const orNull = (s: string) => (s.trim() === "" ? null : s.trim());

export default function ReportStudioPage() {
  // UI default only (the API itself has no default year on purpose).
  const [year, setYear] = useState<number>(new Date().getFullYear());
  const [tab, setTab] = useState<Tab>("cover");
  const [form, setForm] = useState<Scalars>(EMPTY);
  const [milestones, setMilestones] = useState<ObjectRow[]>([]);
  const [principles, setPrinciples] = useState<PrincipleDrafts>(emptyDrafts());

  const narrative = useReportNarrative(year);
  const completeness = useNarrativeCompleteness(year);
  const years = useNarrativeYears();
  const sdgs = useSdgLabels();
  const save = useSaveNarrative(year);
  const download = useDownloadCompletePdf();

  // Hydrate local state whenever the year's narrative arrives (or is null).
  useEffect(() => {
    if (narrative.isLoading) return;
    const n = narrative.data;
    setForm({
      cover_title: n?.cover_title ?? "", cover_subtitle: n?.cover_subtitle ?? "",
      theme_colour: n?.theme_colour ?? "#1A7F37", about_company: n?.about_company ?? "",
      leadership_message: n?.leadership_message ?? "", leadership_name: n?.leadership_name ?? "",
      leadership_designation: n?.leadership_designation ?? "",
    });
    setMilestones((n?.milestones ?? []).map((m) => ({
      year: m.year, title: m.title, description: m.description ?? "",
    })));
    const drafts = emptyDrafts();
    for (const p of n?.principle_narratives ?? []) {
      drafts[p.principle] = { highlight: p.highlight ?? "", intro: p.intro ?? "", sdgs: p.sdgs ?? [] };
    }
    setPrinciples(drafts);
  }, [narrative.data, narrative.isLoading, year]);

  const yearOptions = useMemo(() => {
    const now = new Date().getFullYear();
    const set = new Set<number>([...(years.data ?? []), year]);
    for (let y = now - 4; y <= now + 1; y++) set.add(y);
    return Array.from(set).sort((a, b) => b - a);
  }, [years.data, year]);

  const set = (k: keyof Scalars) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
    setForm((f) => ({ ...f, [k]: e.target.value }));

  const handleSave = () => {
    const payload: ReportNarrativeUpdate = {
      cover_title: orNull(form.cover_title), cover_subtitle: orNull(form.cover_subtitle),
      theme_colour: orNull(form.theme_colour), about_company: orNull(form.about_company),
      leadership_message: orNull(form.leadership_message),
      leadership_name: orNull(form.leadership_name),
      leadership_designation: orNull(form.leadership_designation),
      milestones: milestones
        .filter((m) => String(m.title ?? "").trim() !== "")
        .map((m) => ({ year: Number(m.year), title: String(m.title), description: orNull(String(m.description ?? "")) })),
      principle_narratives: Object.entries(principles).map(([n, d]) => ({
        principle: Number(n), highlight: orNull(d.highlight), intro: orNull(d.intro), sdgs: d.sdgs,
      })),
    };
    save.mutate(payload);
  };

  const c = completeness.data;
  const input = "mt-1 w-full rounded-md border border-gray-300 px-3 py-2";
  const tabBtn = (t: Tab, label: string) => (
    <button type="button" onClick={() => setTab(t)}
      className={`px-4 py-2 text-sm border-b-2 ${tab === t ? "border-emerald-600 text-emerald-700 font-medium" : "border-transparent text-gray-500 hover:text-gray-700"}`}>
      {label}
    </button>
  );

  return (
    <div className="p-6 space-y-6 max-w-5xl">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Report Studio</h1>
          <p className="text-sm text-gray-500">Narratives for the complete sustainability report. Numbers come from the platform; words come from here.</p>
        </div>
        <div className="flex items-center gap-3">
          <label className="text-sm text-gray-700">Year
            <select className="ml-2 rounded-md border border-gray-300 px-2 py-1.5" value={year}
              onChange={(e) => setYear(Number(e.target.value))}>
              {yearOptions.map((y) => <option key={y} value={y}>{y}</option>)}
            </select>
          </label>
          <button type="button" onClick={() => download.mutate(year)} disabled={download.isPending}
            className="px-4 py-2 rounded-md bg-gray-800 text-white text-sm hover:bg-gray-700 disabled:opacity-50">
            {download.isPending ? "Preparing PDF\u2026" : "Download PDF"}
          </button>
          <button type="button" onClick={handleSave} disabled={save.isPending}
            className="px-4 py-2 rounded-md bg-emerald-600 text-white text-sm hover:bg-emerald-700 disabled:opacity-50">
            {save.isPending ? "Saving\u2026" : "Save"}
          </button>
        </div>
      </div>

      {c && (
        <div className="rounded-lg border border-gray-200 p-4 bg-white">
          <div className="flex justify-between text-sm text-gray-700">
            <span>Narrative completeness</span><span>{c.answered} / {c.total} ({c.percent}%)</span>
          </div>
          <div className="mt-2 h-2 rounded bg-gray-100">
            <div className="h-2 rounded bg-emerald-500" style={{ width: `${c.percent}%` }} />
          </div>
          {c.missing.length > 0 && (
            <p className="mt-2 text-xs text-gray-500">Still to write: {c.missing.join(", ")}</p>
          )}
        </div>
      )}

      <div className="border-b border-gray-200 flex">
        {tabBtn("cover", "Cover & theme")}{tabBtn("leadership", "Leadership")}
        {tabBtn("about", "About & milestones")}{tabBtn("principles", "Principles 1\u20139")}
      </div>

      <div className="rounded-lg border border-gray-200 p-5 bg-white">
        {tab === "cover" && (
          <div className="space-y-4">
            <label className="block text-sm"><span className="text-gray-700">Cover title</span>
              <input className={input} value={form.cover_title} onChange={set("cover_title")} placeholder={`Sustainability Report ${year}`} /></label>
            <label className="block text-sm"><span className="text-gray-700">Cover subtitle</span>
              <input className={input} value={form.cover_subtitle} onChange={set("cover_subtitle")} /></label>
            <label className="block text-sm"><span className="text-gray-700">Theme colour</span>
              <div className="mt-1 flex items-center gap-3">
                <input type="color" value={form.theme_colour || "#1A7F37"} onChange={set("theme_colour")} className="h-10 w-14 rounded border border-gray-300" />
                <input className="rounded-md border border-gray-300 px-3 py-2 w-32" value={form.theme_colour} onChange={set("theme_colour")} placeholder="#RRGGBB" />
              </div></label>
          </div>
        )}
        {tab === "leadership" && (
          <div className="space-y-4">
            <label className="block text-sm"><span className="text-gray-700">Message from leadership</span>
              <textarea className={input} rows={10} value={form.leadership_message} onChange={set("leadership_message")} /></label>
            <div className="grid md:grid-cols-2 gap-4">
              <label className="block text-sm"><span className="text-gray-700">Name</span>
                <input className={input} value={form.leadership_name} onChange={set("leadership_name")} /></label>
              <label className="block text-sm"><span className="text-gray-700">Designation</span>
                <input className={input} value={form.leadership_designation} onChange={set("leadership_designation")} /></label>
            </div>
          </div>
        )}
        {tab === "about" && (
          <div className="space-y-6">
            <label className="block text-sm"><span className="text-gray-700">About the company</span>
              <textarea className={input} rows={8} value={form.about_company} onChange={set("about_company")} /></label>
            <ObjectListField label="Milestones" fields={MILESTONE_FIELDS} value={milestones} onChange={setMilestones} />
          </div>
        )}
        {tab === "principles" && (
          <PrincipleNarrativesEditor value={principles} onChange={setPrinciples}
            sdgs={sdgs.data ?? []} written={c?.principles ?? {}} />
        )}
      </div>
    </div>
  );
}
