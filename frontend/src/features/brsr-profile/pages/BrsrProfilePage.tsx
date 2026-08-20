import { useEffect, useState } from "react";
import { ChevronDown, ChevronRight, Save } from "lucide-react";
import {
  useBrsrProfile,
  useBrsrCompleteness,
  useSaveBrsrProfile,
} from "../hooks/useBrsrProfile";
import type { BrsrProfileUpdate } from "../api/brsrProfileApi";
import StringListField from "../components/StringListField";
import ObjectListField, { type ObjectRow } from "../components/ObjectListField";
import NestedFieldsGroup, { type NestedValue } from "../components/NestedFieldsGroup";

type FormState = Record<string, string>;

/**
 * Section A is grouped by its own SEBI sub-sections rather than shown as
 * one 24-question scroll, which is unusable for a client filling it in.
 *
 * v1 covers scalar fields only. The repeating disclosure blocks
 * (products, employees, group companies, grievances) need an add/remove
 * row UI and land in a second iteration.
 */
const SECTIONS: {
  key: string;
  title: string;
  fields: { name: string; label: string; type?: string; options?: string[] }[];
}[] = [
  {
    key: "a1",
    title: "A.I  Details of the listed entity",
    fields: [
      { name: "cin", label: "Corporate Identity Number (CIN)" },
      { name: "year_of_incorporation", label: "Year of incorporation", type: "number" },
      { name: "registered_office_address", label: "Registered office address", type: "textarea" },
      { name: "corporate_address", label: "Corporate address", type: "textarea" },
      { name: "contact_email", label: "E-mail" },
      { name: "contact_telephone", label: "Telephone" },
      { name: "website", label: "Website" },
      { name: "financial_year_reported", label: "Financial year reported (e.g. 2025-26)" },
      { name: "paid_up_capital_inr", label: "Paid-up capital (Rs)", type: "number" },
      {
        name: "reporting_boundary",
        label: "Reporting boundary",
        type: "select",
        options: ["standalone", "consolidated"],
      },
    ],
  },
  {
    key: "a1b",
    title: "A.I  BRSR contact person",
    fields: [
      { name: "brsr_contact_name", label: "Name" },
      { name: "brsr_contact_phone", label: "Telephone" },
      { name: "brsr_contact_email", label: "E-mail" },
    ],
  },
  {
    key: "a6",
    title: "A.VI  CSR details",
    fields: [
      { name: "csr_turnover_inr", label: "Turnover (Rs)", type: "number" },
      { name: "csr_net_worth_inr", label: "Net worth (Rs)", type: "number" },
    ],
  },
  {
    key: "a8",
    title: "A.VIII  Assurance",
    fields: [
      { name: "assurance_provider_name", label: "Assurance provider" },
      { name: "assurance_type", label: "Type of assurance obtained" },
    ],
  },
];

const NUMERIC_FIELDS = new Set([
  "year_of_incorporation",
  "paid_up_capital_inr",
  "csr_turnover_inr",
  "csr_net_worth_inr",
]);

export default function BrsrProfilePage() {
  const { data: profile, isLoading } = useBrsrProfile();
  const { data: completeness } = useBrsrCompleteness();
  const saveProfile = useSaveBrsrProfile();

  const [form, setForm] = useState<FormState>({});
  // Repeating blocks keep their own state: FormState is Record<string, string>
  // and cannot hold an array without stringifying it.
  const [stockExchanges, setStockExchanges] = useState<string[]>([]);
  const [businessActivities, setBusinessActivities] = useState<ObjectRow[]>([]);
  const [productsSold, setProductsSold] = useState<ObjectRow[]>([]);
  const [turnoverRates, setTurnoverRates] = useState<ObjectRow[]>([]);
  const [groupCompanies, setGroupCompanies] = useState<ObjectRow[]>([]);
  const [grievances, setGrievances] = useState<ObjectRow[]>([]);
  const [locationCounts, setLocationCounts] = useState<NestedValue>({});
  const [marketsServed, setMarketsServed] = useState<NestedValue>({});
  const [employeeCounts, setEmployeeCounts] = useState<NestedValue>({});
  const [womenParticipation, setWomenParticipation] = useState<NestedValue>({});
  const [openSections, setOpenSections] = useState<Record<string, boolean>>({ a1: true });

  useEffect(() => {
    if (!profile) return;
    const next: FormState = {};
    SECTIONS.forEach((section) =>
      section.fields.forEach((field) => {
        const value = (profile as Record<string, unknown>)[field.name];
        next[field.name] = value === null || value === undefined ? "" : String(value);
      })
    );
    setForm(next);
    setStockExchanges(profile.stock_exchanges_listed ?? []);
    setBusinessActivities((profile.business_activities as ObjectRow[]) ?? []);
    setProductsSold((profile.products_sold as ObjectRow[]) ?? []);
    setTurnoverRates((profile.turnover_rates as ObjectRow[]) ?? []);
    setGroupCompanies((profile.group_companies as ObjectRow[]) ?? []);
    setGrievances((profile.grievance_redressal as ObjectRow[]) ?? []);
    setLocationCounts((profile.location_counts as NestedValue) ?? {});
    setMarketsServed((profile.markets_served as NestedValue) ?? {});
    setEmployeeCounts((profile.employee_worker_counts as NestedValue) ?? {});
    setWomenParticipation((profile.women_participation as NestedValue) ?? {});
  }, [profile]);

  const handleChange = (name: string, value: string) =>
    setForm((prev) => ({ ...prev, [name]: value }));

  const handleSave = () => {
    // Empty strings are dropped rather than sent: the backend would store
    // "" while still counting the question as unanswered, leaving the row
    // dirty for no gain. Omitted keys are left untouched (exclude_unset).
    const payload: BrsrProfileUpdate = {};
    Object.entries(form).forEach(([name, value]) => {
      if (value.trim() === "") return;
      if (NUMERIC_FIELDS.has(name)) {
        const parsed = Number(value);
        if (!Number.isNaN(parsed)) {
          (payload as Record<string, unknown>)[name] = parsed;
        }
        return;
      }
      (payload as Record<string, unknown>)[name] = value.trim();
    });
    // Blank rows are dropped; an all-blank list sends an empty array, which
    // the completeness check treats as unanswered - correct, not a false tick.
    payload.stock_exchanges_listed = stockExchanges
      .map((s) => s.trim())
      .filter((s) => s !== "");
    // A row counts as real only if its first column is filled - that is
    // the identifying field in both blocks (description / product name).
    payload.business_activities = businessActivities.filter(
      (row) => String(row.description ?? "").trim() !== ""
    );
    payload.products_sold = productsSold.filter(
      (row) => String(row.product_service ?? "").trim() !== ""
    );
    payload.turnover_rates = turnoverRates.filter(
      (row) => String(row.year ?? "").trim() !== ""
    );
    payload.group_companies = groupCompanies.filter(
      (row) => String(row.name ?? "").trim() !== ""
    );
    payload.grievance_redressal = grievances.filter(
      (row) => String(row.stakeholder_group ?? "").trim() !== ""
    );
    // Sent only when something was actually entered. An empty object would
    // occupy the column while still reading as unanswered - dirty for nothing.
    if (Object.keys(locationCounts).length > 0)
      payload.location_counts = locationCounts as never;
    if (Object.keys(marketsServed).length > 0)
      payload.markets_served = marketsServed as never;
    if (Object.keys(employeeCounts).length > 0)
      payload.employee_worker_counts = employeeCounts as never;
    if (Object.keys(womenParticipation).length > 0)
      payload.women_participation = womenParticipation as never;
    saveProfile.mutate(payload);
  };

  const toggleSection = (key: string) =>
    setOpenSections((prev) => ({ ...prev, [key]: !prev[key] }));

  if (isLoading) {
    return <div className="p-6 text-gray-500">Loading BRSR Section A...</div>;
  }

  const pending = completeness?.questions.filter((q) => !q.answered) ?? [];

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">
          BRSR Section A - General Disclosures
        </h1>
        <p className="text-sm text-gray-500 mt-1">
          Company profile disclosures required under SEBI's Business Responsibility
          and Sustainability Report.
        </p>
      </div>

      {completeness && (
        <div className="bg-white rounded-lg border border-gray-200 p-5">
          <div className="flex items-baseline justify-between">
            <span className="text-sm font-medium text-gray-700">Completion</span>
            <span className="text-sm text-gray-600">
              {completeness.answered_questions} of {completeness.tracked_questions} answered
              <span className="ml-2 font-semibold text-gray-900">
                {completeness.completeness_percent}%
              </span>
            </span>
          </div>
          <div className="mt-2 h-2 w-full rounded-full bg-gray-100">
            <div
              className="h-2 rounded-full bg-emerald-500 transition-all"
              style={{ width: `${completeness.completeness_percent}%` }}
            />
          </div>
          {pending.length > 0 && (
            <div className="mt-4">
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                Still to answer
              </p>
              <ul className="mt-2 space-y-1">
                {pending.map((q) => (
                  <li key={q.question} className="text-sm text-gray-600">
                    <span className="font-medium text-gray-800">{q.question}</span> - {q.label}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {SECTIONS.map((section) => {
        const isOpen = openSections[section.key];
        return (
          <div key={section.key} className="bg-white rounded-lg border border-gray-200">
            <button
              onClick={() => toggleSection(section.key)}
              className="w-full flex items-center gap-2 px-5 py-4 text-left"
            >
              {isOpen ? (
                <ChevronDown className="h-4 w-4 text-gray-400" />
              ) : (
                <ChevronRight className="h-4 w-4 text-gray-400" />
              )}
              <span className="font-medium text-gray-900">{section.title}</span>
            </button>
            {isOpen && (
              <div className="px-5 pb-5 grid grid-cols-1 md:grid-cols-2 gap-4">
                {section.fields.map((field) => (
                  <div
                    key={field.name}
                    className={field.type === "textarea" ? "md:col-span-2" : ""}
                  >
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      {field.label}
                    </label>
                    {field.type === "textarea" ? (
                      <textarea
                        rows={2}
                        value={form[field.name] ?? ""}
                        onChange={(e) => handleChange(field.name, e.target.value)}
                        className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none"
                      />
                    ) : field.type === "select" ? (
                      <select
                        value={form[field.name] ?? ""}
                        onChange={(e) => handleChange(field.name, e.target.value)}
                        className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none"
                      >
                        <option value="">Select...</option>
                        {field.options?.map((option) => (
                          <option key={option} value={option}>
                            {option}
                          </option>
                        ))}
                      </select>
                    ) : (
                      <input
                        type={field.type === "number" ? "number" : "text"}
                        value={form[field.name] ?? ""}
                        onChange={(e) => handleChange(field.name, e.target.value)}
                        className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none"
                      />
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        );
      })}

      <div className="bg-white rounded-lg border border-gray-200 p-5">
        <StringListField
          label="Q10  Stock exchanges where listed"
          value={stockExchanges}
          onChange={setStockExchanges}
          placeholder="e.g. BSE"
        />
      </div>

      <div className="bg-white rounded-lg border border-gray-200 p-5">
        <ObjectListField
          label="Q14  Business activities accounting for 90% of turnover"
          fields={[
            { name: "description", label: "Description of main activity" },
            { name: "nic_code", label: "NIC code" },
            { name: "turnover_percent", label: "% of turnover", type: "number" },
          ]}
          value={businessActivities}
          onChange={setBusinessActivities}
        />
      </div>

      <div className="bg-white rounded-lg border border-gray-200 p-5">
        <ObjectListField
          label="Q15  Products/services sold (90% of turnover)"
          fields={[
            { name: "product_service", label: "Product / service" },
            { name: "nic_code", label: "NIC code" },
            { name: "turnover_percent", label: "% of total turnover", type: "number" },
          ]}
          value={productsSold}
          onChange={setProductsSold}
        />
      </div>

      <div className="bg-white rounded-lg border border-gray-200 p-5">
        <ObjectListField
          label="Q20  Turnover rate for employees and workers"
          fields={[
            { name: "year", label: "Financial year" },
            { name: "category", label: "Category" },
            { name: "total_turnover_percent", label: "Total turnover %", type: "number" },
          ]}
          value={turnoverRates}
          onChange={setTurnoverRates}
        />
      </div>

      <div className="bg-white rounded-lg border border-gray-200 p-5">
        <ObjectListField
          label="Q21  Holding, subsidiary and associate companies"
          fields={[
            { name: "name", label: "Company name" },
            { name: "relationship", label: "Holding / Subsidiary / Associate" },
            { name: "shareholding_percent", label: "Shareholding %", type: "number" },
          ]}
          value={groupCompanies}
          onChange={setGroupCompanies}
        />
      </div>

      <div className="bg-white rounded-lg border border-gray-200 p-5">
        <ObjectListField
          label="Q23  Grievance redressal by stakeholder group"
          fields={[
            { name: "stakeholder_group", label: "Stakeholder group" },
            { name: "filed_current_year", label: "Filed this year", type: "number" },
            { name: "pending_current_year", label: "Pending this year", type: "number" },
          ]}
          value={grievances}
          onChange={setGrievances}
        />
      </div>

      <div className="bg-white rounded-lg border border-gray-200 p-5">
        <NestedFieldsGroup
          label="Q16  Number of plants and offices"
          columns={4}
          fields={[
            { path: "plants.national", label: "Plants - national", type: "number" },
            { path: "plants.international", label: "Plants - international", type: "number" },
            { path: "offices.national", label: "Offices - national", type: "number" },
            { path: "offices.international", label: "Offices - international", type: "number" },
          ]}
          value={locationCounts}
          onChange={setLocationCounts}
        />
      </div>

      <div className="bg-white rounded-lg border border-gray-200 p-5">
        <NestedFieldsGroup
          label="Q17  Markets served"
          fields={[
            { path: "national_states", label: "States covered", type: "number" },
            { path: "international_countries", label: "Countries covered", type: "number" },
            { path: "exports_percent", label: "Exports as % of turnover", type: "number" },
            { path: "customer_types", label: "Types of customers" },
          ]}
          value={marketsServed}
          onChange={setMarketsServed}
        />
      </div>

      <div className="bg-white rounded-lg border border-gray-200 p-5">
        <NestedFieldsGroup
          label="Q18  Employees and workers"
          fields={[
            { path: "employees.permanent.total", label: "Permanent employees - total", type: "number" },
            { path: "employees.permanent.male", label: "Permanent employees - male", type: "number" },
            { path: "employees.permanent.female", label: "Permanent employees - female", type: "number" },
            { path: "employees.other.total", label: "Other employees - total", type: "number" },
            { path: "employees.other.male", label: "Other employees - male", type: "number" },
            { path: "employees.other.female", label: "Other employees - female", type: "number" },
            { path: "workers.permanent.total", label: "Permanent workers - total", type: "number" },
            { path: "workers.permanent.male", label: "Permanent workers - male", type: "number" },
            { path: "workers.permanent.female", label: "Permanent workers - female", type: "number" },
            { path: "workers.other.total", label: "Other workers - total", type: "number" },
            { path: "workers.other.male", label: "Other workers - male", type: "number" },
            { path: "workers.other.female", label: "Other workers - female", type: "number" },
          ]}
          value={employeeCounts}
          onChange={setEmployeeCounts}
        />
      </div>

      <div className="bg-white rounded-lg border border-gray-200 p-5">
        <NestedFieldsGroup
          label="Q19  Participation of women"
          columns={4}
          fields={[
            { path: "board_total", label: "Board - total", type: "number" },
            { path: "board_female", label: "Board - female", type: "number" },
            { path: "kmp_total", label: "KMP - total", type: "number" },
            { path: "kmp_female", label: "KMP - female", type: "number" },
          ]}
          value={womenParticipation}
          onChange={setWomenParticipation}
        />
      </div>

      <div className="flex justify-end">
        <button
          onClick={handleSave}
          disabled={saveProfile.isPending}
          className="inline-flex items-center gap-2 rounded-md bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700 disabled:opacity-50"
        >
          <Save className="h-4 w-4" />
          {saveProfile.isPending ? "Saving..." : "Save Section A"}
        </button>
      </div>
    </div>
  );
}
