import DisclosureForm, { type SectionDef } from "../../../components/brsr/DisclosureForm";
import type { HumanRightsFields, HumanRightsRecord, HumanRightsRecordCreate, HumanRightsRecordUpdate } from "../api/humanRightsApi";

type K = keyof HumanRightsFields;

// SEBI Principle 5 scalar disclosures. Tabular ones (EI 1-3, EI 6) live in
// child rows on the page, not here.
export const HUMAN_RIGHTS_SECTIONS: SectionDef<K>[] = [
  {
    title: "EI 4 -- Focal Point",
    subtitle: "Whether the entity has a focal point (individual/committee) for human rights impacts or issues.",
    fields: [
      { name: "has_human_rights_focal_point", label: "Focal point in place?", kind: "yesno" },
      { name: "focal_point_details", label: "Focal point details", kind: "textarea" },
    ],
  },
  {
    title: "EI 5 & 7 -- Grievance Mechanisms",
    subtitle: "Internal mechanisms to redress grievances and to prevent adverse consequences to the complainant.",
    fields: [
      { name: "grievance_mechanism_details", label: "Grievance redressal mechanism", kind: "textarea" },
      { name: "complainant_protection_details", label: "Mechanisms preventing adverse consequences to complainant", kind: "textarea" },
    ],
  },
  {
    title: "EI 8 -- Business Agreements",
    fields: [
      { name: "hr_requirements_in_contracts", label: "Human rights requirements part of contracts?", kind: "yesno" },
      { name: "hr_requirements_details", label: "Details", kind: "textarea" },
    ],
  },
  {
    title: "EI 9 & 10 -- Assessments",
    subtitle: "% of plants and offices assessed by the entity, statutory authorities or third parties, and corrective actions.",
    fields: [
      { name: "assessed_child_labour_percent", label: "Child labour (% assessed)", kind: "pct" },
      { name: "assessed_forced_labour_percent", label: "Forced / involuntary labour (% assessed)", kind: "pct" },
      { name: "assessed_sexual_harassment_percent", label: "Sexual harassment (% assessed)", kind: "pct" },
      { name: "assessed_discrimination_percent", label: "Discrimination at workplace (% assessed)", kind: "pct" },
      { name: "assessed_wages_percent", label: "Wages (% assessed)", kind: "pct" },
      { name: "assessed_other_percent", label: "Other (% assessed)", kind: "pct" },
      { name: "assessed_other_description", label: "Other -- describe", kind: "textarea" },
      { name: "corrective_actions_from_assessments", label: "Corrective actions arising from assessments", kind: "textarea" },
    ],
  },
  {
    title: "Leadership Indicators",
    fields: [
      { name: "process_modifications_from_grievances", label: "Business process modifications from grievances", kind: "textarea" },
      { name: "human_rights_due_diligence_details", label: "Scope and coverage of human rights due diligence", kind: "textarea" },
      { name: "premises_accessible_to_differently_abled", label: "Premises accessible to differently abled?", kind: "yesno" },
      { name: "accessibility_details", label: "Accessibility details", kind: "textarea" },
      { name: "value_chain_partners_assessed_percent", label: "Value chain partners assessed (%)", kind: "pct" },
      { name: "value_chain_assessment_details", label: "Value chain assessment details", kind: "textarea" },
      { name: "value_chain_corrective_actions", label: "Corrective actions from value chain assessments", kind: "textarea" },
      { name: "remarks", label: "Remarks", kind: "textarea" },
    ],
  },
];

interface Props {
  initialData?: HumanRightsRecord;
  onSubmit: (data: HumanRightsRecordCreate | HumanRightsRecordUpdate) => void;
  onCancel?: () => void;
  loading?: boolean;
}

export default function HumanRightsRecordForm({ initialData, onSubmit, onCancel, loading }: Props) {
  return (
    <DisclosureForm
      title="Principle 5 Record"
      subtitle="BRSR Principle 5 -- human rights. One record per reporting year; workforce, remuneration and complaint tables are added on the record card."
      sections={HUMAN_RIGHTS_SECTIONS}
      initialData={initialData as unknown as Record<string, unknown> & { reporting_year: number }}
      onSubmit={(data) => onSubmit(data as HumanRightsRecordCreate | HumanRightsRecordUpdate)}
      onCancel={onCancel}
      loading={loading}
    />
  );
}
