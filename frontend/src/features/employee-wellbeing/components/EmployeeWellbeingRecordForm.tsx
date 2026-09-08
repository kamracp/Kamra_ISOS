import DisclosureForm, { type SectionDef } from "../../../components/brsr/DisclosureForm";
import type { EmployeeWellbeingFields, EmployeeWellbeingRecord, EmployeeWellbeingRecordCreate, EmployeeWellbeingRecordUpdate } from "../api/employeeWellbeingApi";

type K = keyof EmployeeWellbeingFields;
const DEPOSIT = [{ value: "yes", label: "Yes" }, { value: "no", label: "No" }, { value: "na", label: "N.A." }];

export const WELLBEING_SECTIONS: SectionDef<K>[] = [
  {
    title: "EI 2 -- Spending on Well-being",
    fields: [{ name: "wellbeing_spend_percent_revenue", label: "Spending on well-being measures (% of revenue)", kind: "pct" }],
  },
  {
    title: "EI 3 -- Retirement Benefits",
    subtitle: "% of employees / workers covered and whether deductions are deposited with the authority.",
    fields: [
      { name: "pf_employees_percent", label: "PF -- employees (%)", kind: "pct" },
      { name: "pf_workers_percent", label: "PF -- workers (%)", kind: "pct" },
      { name: "pf_deposited", label: "PF -- deposited with authority", kind: "select", options: DEPOSIT },
      { name: "gratuity_employees_percent", label: "Gratuity -- employees (%)", kind: "pct" },
      { name: "gratuity_workers_percent", label: "Gratuity -- workers (%)", kind: "pct" },
      { name: "gratuity_deposited", label: "Gratuity -- deposited with authority", kind: "select", options: DEPOSIT },
      { name: "esi_employees_percent", label: "ESI -- employees (%)", kind: "pct" },
      { name: "esi_workers_percent", label: "ESI -- workers (%)", kind: "pct" },
      { name: "esi_deposited", label: "ESI -- deposited with authority", kind: "select", options: DEPOSIT },
      { name: "other_benefit_name", label: "Other benefit -- name", kind: "text" },
      { name: "other_benefit_employees_percent", label: "Other -- employees (%)", kind: "pct" },
      { name: "other_benefit_workers_percent", label: "Other -- workers (%)", kind: "pct" },
      { name: "other_benefit_deposited", label: "Other -- deposited with authority", kind: "select", options: DEPOSIT },
    ],
  },
  {
    title: "EI 4 & 5 -- Accessibility and Equal Opportunity",
    fields: [
      { name: "premises_accessible_to_differently_abled", label: "Premises accessible to differently abled?", kind: "yesno" },
      { name: "has_equal_opportunity_policy", label: "Equal opportunity policy (RPwD Act 2016)?", kind: "yesno" },
      { name: "accessibility_details", label: "Accessibility details", kind: "textarea" },
      { name: "equal_opportunity_policy_link", label: "Policy web link", kind: "text" },
    ],
  },
  {
    title: "EI 7 -- Union Membership",
    subtitle: "Permanent employees and workers who are members of associations or unions; % is derived.",
    fields: [
      { name: "permanent_employees_total", label: "Permanent employees -- total", kind: "int" },
      { name: "permanent_employees_union_members", label: "Permanent employees -- union members", kind: "int" },
      { name: "permanent_workers_total", label: "Permanent workers -- total", kind: "int" },
      { name: "permanent_workers_union_members", label: "Permanent workers -- union members", kind: "int" },
    ],
  },
  {
    title: "EI 10 -- Occupational Health and Safety",
    fields: [
      { name: "has_ohs_management_system", label: "OHS management system implemented?", kind: "yesno" },
      { name: "has_medical_facilities", label: "Non-occupational medical / healthcare services?", kind: "yesno" },
      { name: "ohs_system_coverage", label: "OHS system coverage", kind: "textarea" },
      { name: "hazard_identification_process", label: "Processes to identify work-related hazards and assess risks", kind: "textarea" },
      { name: "non_routine_risk_reporting_process", label: "Process for workers to report hazards and remove themselves from risk", kind: "textarea" },
      { name: "safety_assessments_details", label: "Safety-related assessments", kind: "textarea" },
    ],
  },
  {
    title: "EI 11 -- Safety Incidents",
    subtitle: "LTIFR per one million person-hours worked.",
    fields: [
      { name: "ltifr_employees", label: "LTIFR -- employees", kind: "num" },
      { name: "ltifr_workers", label: "LTIFR -- workers", kind: "num" },
      { name: "recordable_injuries_employees", label: "Recordable injuries -- employees", kind: "int" },
      { name: "recordable_injuries_workers", label: "Recordable injuries -- workers", kind: "int" },
      { name: "fatalities_employees", label: "Fatalities -- employees", kind: "int" },
      { name: "fatalities_workers", label: "Fatalities -- workers", kind: "int" },
      { name: "high_consequence_injuries_employees", label: "High-consequence injuries (excl. fatalities) -- employees", kind: "int" },
      { name: "high_consequence_injuries_workers", label: "High-consequence injuries (excl. fatalities) -- workers", kind: "int" },
    ],
  },
  {
    title: "EI 12, 14 & 15 -- Safe Workplace, Complainant Protection, Assessments",
    fields: [
      { name: "assessed_health_safety_percent", label: "Plants/offices assessed -- health & safety (%)", kind: "pct" },
      { name: "assessed_working_conditions_percent", label: "Plants/offices assessed -- working conditions (%)", kind: "pct" },
      { name: "safe_workplace_measures", label: "Measures to ensure a safe and healthy workplace", kind: "textarea" },
      { name: "complainant_protection_details", label: "Mechanisms preventing adverse consequences to the complainant", kind: "textarea" },
      { name: "corrective_actions_from_assessments", label: "Corrective actions from assessments", kind: "textarea" },
    ],
  },
  {
    title: "Leadership Indicators",
    fields: [
      { name: "life_insurance_employees", label: "Life insurance / compensatory package -- employees?", kind: "yesno" },
      { name: "life_insurance_workers", label: "Life insurance / compensatory package -- workers?", kind: "yesno" },
      { name: "has_transition_assistance", label: "Transition assistance programs?", kind: "yesno" },
      { name: "rehabilitated_employees_count", label: "Rehabilitated / placed after injury -- employees", kind: "int" },
      { name: "rehabilitated_workers_count", label: "Rehabilitated / placed after injury -- workers", kind: "int" },
      { name: "value_chain_assessed_health_safety_percent", label: "Value chain partners assessed -- health & safety (%)", kind: "pct" },
      { name: "value_chain_assessed_working_conditions_percent", label: "Value chain partners assessed -- working conditions (%)", kind: "pct" },
      { name: "value_chain_statutory_dues_details", label: "Measures ensuring statutory dues are deducted and deposited by value chain partners", kind: "textarea" },
      { name: "value_chain_corrective_actions", label: "Corrective actions from value chain assessments", kind: "textarea" },
      { name: "remarks", label: "Remarks", kind: "textarea" },
    ],
  },
];

interface Props {
  initialData?: EmployeeWellbeingRecord;
  onSubmit: (data: EmployeeWellbeingRecordCreate | EmployeeWellbeingRecordUpdate) => void;
  onCancel?: () => void;
  loading?: boolean;
}

export default function EmployeeWellbeingRecordForm({ initialData, onSubmit, onCancel, loading }: Props) {
  return (
    <DisclosureForm
      title="Principle 3 Record"
      subtitle="BRSR Principle 3 -- employee well-being. One record per reporting year; well-being, parental leave, training and complaint tables are added on the record card."
      sections={WELLBEING_SECTIONS}
      initialData={initialData as unknown as Record<string, unknown> & { reporting_year: number }}
      onSubmit={(data) => onSubmit(data as EmployeeWellbeingRecordCreate | EmployeeWellbeingRecordUpdate)}
      onCancel={onCancel}
      loading={loading}
    />
  );
}
