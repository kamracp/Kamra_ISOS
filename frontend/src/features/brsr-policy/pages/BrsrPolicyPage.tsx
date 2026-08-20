import { useEffect, useState } from "react";
import { Save } from "lucide-react";
import {
  useBrsrPolicyDisclosures,
  useBrsrPolicyCompleteness,
  usePrincipleLabels,
  useSaveBrsrPolicy,
} from "../hooks/useBrsrPolicy";
import type { BrsrPolicyDisclosureUpdate } from "../api/brsrPolicyApi";
// Section B's three entity-level questions are stored on the Section A
// profile row (they are asked once for the whole entity), so this page
// reads and writes them through the profile hooks.
import {
  useBrsrProfile,
  useSaveBrsrProfile,
} from "../../brsr-profile/hooks/useBrsrProfile";

type TriState = "" | "true" | "false";

interface PrincipleForm {
  has_policy: TriState;
  policy_board_approved: TriState;
  policy_web_link: string;
  translated_to_procedures: TriState;
  extends_to_value_chain: TriState;
  certifications: string;
  commitments_and_targets: string;
  performance_against_targets: string;
  reason_no_policy: string;
}

const emptyForm = (): PrincipleForm => ({
  has_policy: "",
  policy_board_approved: "",
  policy_web_link: "",
  translated_to_procedures: "",
  extends_to_value_chain: "",
  certifications: "",
  commitments_and_targets: "",
  performance_against_targets: "",
  reason_no_policy: "",
});

const toTri = (value: boolean | null | undefined): TriState =>
  value === true ? "true" : value === false ? "false" : "";

const fromTri = (value: TriState): boolean | undefined =>
  value === "true" ? true : value === "false" ? false : undefined;

const YES_NO_FIELDS: { name: keyof PrincipleForm; label: string }[] = [
  { name: "has_policy", label: "Does the entity have a policy for this principle?" },
  { name: "policy_board_approved", label: "Has the policy been approved by the Board?" },
  { name: "translated_to_procedures", label: "Translated into procedures?" },
  { name: "extends_to_value_chain", label: "Extends to value chain partners?" },
];

const TEXT_FIELDS: { name: keyof PrincipleForm; label: string; rows?: number }[] = [
  { name: "policy_web_link", label: "Web link to the policy" },
  { name: "certifications", label: "Certifications / standards adopted", rows: 2 },
  { name: "commitments_and_targets", label: "Specific commitments, goals and targets", rows: 3 },
  { name: "performance_against_targets", label: "Performance against those targets", rows: 3 },
];

export default function BrsrPolicyPage() {
  const { data: disclosures, isLoading } = useBrsrPolicyDisclosures();
  const { data: completeness } = useBrsrPolicyCompleteness();
  const { data: principles } = usePrincipleLabels();
  const savePolicy = useSaveBrsrPolicy();

  const [active, setActive] = useState(1);
  const [forms, setForms] = useState<Record<number, PrincipleForm>>({});

  const { data: profile } = useBrsrProfile();
  const saveProfile = useSaveBrsrProfile();
  const [committee, setCommittee] = useState<TriState>("");
  const [reviewFrequency, setReviewFrequency] = useState("");
  const [assessmentAgency, setAssessmentAgency] = useState("");

  useEffect(() => {
    if (!profile) return;
    setCommittee(toTri(profile.has_sustainability_committee));
    setReviewFrequency(profile.policy_review_frequency ?? "");
    setAssessmentAgency(profile.independent_assessment_agency ?? "");
  }, [profile]);

  useEffect(() => {
    const next: Record<number, PrincipleForm> = {};
    for (let n = 1; n <= 9; n++) next[n] = emptyForm();
    (disclosures ?? []).forEach((row) => {
      next[row.principle] = {
        has_policy: toTri(row.has_policy),
        policy_board_approved: toTri(row.policy_board_approved),
        policy_web_link: row.policy_web_link ?? "",
        translated_to_procedures: toTri(row.translated_to_procedures),
        extends_to_value_chain: toTri(row.extends_to_value_chain),
        certifications: row.certifications ?? "",
        commitments_and_targets: row.commitments_and_targets ?? "",
        performance_against_targets: row.performance_against_targets ?? "",
        reason_no_policy: row.reason_no_policy ?? "",
      };
    });
    setForms(next);
  }, [disclosures]);

  const current = forms[active] ?? emptyForm();

  const handleChange = (name: keyof PrincipleForm, value: string) =>
    setForms((prev) => ({
      ...prev,
      [active]: { ...(prev[active] ?? emptyForm()), [name]: value },
    }));

  const handleSave = () => {
    // Only principles the user actually touched are sent. An untouched
    // principle would otherwise create an all-null row that reads as
    // unanswered anyway - a row for nothing.
    const payload: BrsrPolicyDisclosureUpdate[] = [];
    Object.entries(forms).forEach(([key, form]) => {
      const touched =
        Object.values(form).some((v) => v !== "");
      if (!touched) return;
      payload.push({
        principle: Number(key),
        has_policy: fromTri(form.has_policy),
        policy_board_approved: fromTri(form.policy_board_approved),
        policy_web_link: form.policy_web_link.trim() || undefined,
        translated_to_procedures: fromTri(form.translated_to_procedures),
        extends_to_value_chain: fromTri(form.extends_to_value_chain),
        certifications: form.certifications.trim() || undefined,
        commitments_and_targets: form.commitments_and_targets.trim() || undefined,
        performance_against_targets:
          form.performance_against_targets.trim() || undefined,
        reason_no_policy: form.reason_no_policy.trim() || undefined,
      });
    });
    // Two writes: principles go to the Section B table, the three
    // entity-level answers to the profile row. Separate endpoints because
    // they are separate shapes, not because they are separate concerns.
    saveProfile.mutate({
      has_sustainability_committee: fromTri(committee),
      policy_review_frequency:
        (reviewFrequency as "annually" | "half_yearly" | "quarterly" | "other") ||
        undefined,
      independent_assessment_agency: assessmentAgency.trim() || undefined,
    });
    if (payload.length === 0) {
      return;
    }
    savePolicy.mutate(payload);
  };

  if (isLoading) {
    return <div className="p-6 text-gray-500">Loading BRSR Section B...</div>;
  }

  const statusFor = (n: number) =>
    completeness?.principles.find((p) => p.principle === n);
  const activeStatus = statusFor(active);
  const noPolicy = current.has_policy === "false";

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">
          BRSR Section B - Management and Process Disclosures
        </h1>
        <p className="text-sm text-gray-500 mt-1">
          Policy and governance disclosures for each of the nine NGRBC principles.
        </p>
      </div>

      {completeness && (
        <div className="bg-white rounded-lg border border-gray-200 p-5">
          <div className="flex items-baseline justify-between">
            <span className="text-sm font-medium text-gray-700">Completion</span>
            <span className="text-sm text-gray-600">
              {completeness.answered_principles} of {completeness.total_principles} answered
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
          {completeness.answered_principles > completeness.complete_principles && (
            <p className="mt-3 text-sm text-amber-700">
              {completeness.answered_principles - completeness.complete_principles}{" "}
              answered principle(s) still need supporting detail.
            </p>
          )}
        </div>
      )}

      <div className="bg-white rounded-lg border border-gray-200 p-5">
        <h2 className="font-medium text-gray-900 mb-4">
          Entity-level disclosures
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Board committee overseeing sustainability?
            </label>
            <select
              value={committee}
              onChange={(e) => setCommittee(e.target.value as TriState)}
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none"
            >
              <option value="">Not stated</option>
              <option value="true">Yes</option>
              <option value="false">No</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Frequency of policy review
            </label>
            <select
              value={reviewFrequency}
              onChange={(e) => setReviewFrequency(e.target.value)}
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none"
            >
              <option value="">Not stated</option>
              <option value="annually">Annually</option>
              <option value="half_yearly">Half-yearly</option>
              <option value="quarterly">Quarterly</option>
              <option value="other">Other</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Independent assessment agency
            </label>
            <input
              type="text"
              value={assessmentAgency}
              onChange={(e) => setAssessmentAgency(e.target.value)}
              placeholder="Leave blank if not assessed"
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none"
            />
          </div>
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        {(principles ?? []).map((p) => {
          const status = statusFor(p.principle);
          const isActive = p.principle === active;
          return (
            <button
              key={p.principle}
              onClick={() => setActive(p.principle)}
              title={p.label}
              className={`rounded-md px-3 py-2 text-sm font-medium border ${
                isActive
                  ? "border-emerald-500 bg-emerald-50 text-emerald-800"
                  : "border-gray-200 bg-white text-gray-600 hover:bg-gray-50"
              }`}
            >
              P{p.principle}
              {status?.complete ? (
                <span className="ml-1 text-emerald-600">&#10003;</span>
              ) : status?.answered ? (
                <span className="ml-1 text-amber-500">&#8226;</span>
              ) : null}
            </button>
          );
        })}
      </div>

      <div className="bg-white rounded-lg border border-gray-200 p-5 space-y-5">
        <div>
          <h2 className="font-medium text-gray-900">
            Principle {active} - {(principles ?? []).find((p) => p.principle === active)?.label}
          </h2>
          {activeStatus?.missing && (
            <p className="mt-1 text-sm text-amber-700">{activeStatus.missing}</p>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {YES_NO_FIELDS.map((field) => (
            <div key={field.name}>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {field.label}
              </label>
              <select
                value={current[field.name] as string}
                onChange={(e) => handleChange(field.name, e.target.value)}
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none"
              >
                <option value="">Not stated</option>
                <option value="true">Yes</option>
                <option value="false">No</option>
              </select>
            </div>
          ))}
        </div>

        {noPolicy && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Reason for not having a policy
            </label>
            <textarea
              rows={2}
              value={current.reason_no_policy}
              onChange={(e) => handleChange("reason_no_policy", e.target.value)}
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none"
            />
          </div>
        )}

        {TEXT_FIELDS.map((field) => (
          <div key={field.name}>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {field.label}
            </label>
            {field.rows ? (
              <textarea
                rows={field.rows}
                value={current[field.name] as string}
                onChange={(e) => handleChange(field.name, e.target.value)}
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none"
              />
            ) : (
              <input
                type="text"
                value={current[field.name] as string}
                onChange={(e) => handleChange(field.name, e.target.value)}
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none"
              />
            )}
          </div>
        ))}
      </div>

      <div className="flex justify-end">
        <button
          onClick={handleSave}
          disabled={savePolicy.isPending}
          className="inline-flex items-center gap-2 rounded-md bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700 disabled:opacity-50"
        >
          <Save className="h-4 w-4" />
          {savePolicy.isPending ? "Saving..." : "Save all principles"}
        </button>
      </div>
    </div>
  );
}
