import client from "../../../services/api/client";
import type { CategoryRowConfig } from "../../../components/brsr/CategoryRowForm";

export type ChildKind = "measure" | "parental" | "training" | "complaint";

// Category labels per child kind -- must match backend Literals / DB CHECKs.
const GENDER_LABELS = {
  permanent_employees_male: "Permanent employees -- male",
  permanent_employees_female: "Permanent employees -- female",
  other_employees_male: "Other than permanent employees -- male",
  other_employees_female: "Other than permanent employees -- female",
  permanent_workers_male: "Permanent workers -- male",
  permanent_workers_female: "Permanent workers -- female",
  other_workers_male: "Other than permanent workers -- male",
  other_workers_female: "Other than permanent workers -- female",
};
const PARENTAL_LABELS = {
  employees_male: "Employees -- male", employees_female: "Employees -- female",
  workers_male: "Workers -- male", workers_female: "Workers -- female",
};
const TRAINING_LABELS = {
  permanent_employees_male: "Permanent employees -- male", permanent_employees_female: "Permanent employees -- female",
  permanent_workers_male: "Permanent workers -- male", permanent_workers_female: "Permanent workers -- female",
};
const COMPLAINT_LABELS = {
  working_conditions_employees: "Working conditions -- employees", health_safety_employees: "Health & safety -- employees",
  working_conditions_workers: "Working conditions -- workers", health_safety_workers: "Health & safety -- workers",
};

// Everything the page and forms need per child kind, in one place.
export const CHILD_CONFIG: Record<ChildKind, CategoryRowConfig & { path: string; relation: string; pctOfTotal: string[] }> = {
  measure: {
    title: "Well-being measures (EI 1)", path: "measures", relation: "wellbeing_measures", labels: GENDER_LABELS,
    fields: [
      { name: "total_count", label: "Total (A)" },
      { name: "health_insurance", label: "Health insurance" },
      { name: "accident_insurance", label: "Accident insurance" },
      { name: "maternity_benefits", label: "Maternity benefits" },
      { name: "paternity_benefits", label: "Paternity benefits" },
      { name: "day_care_facilities", label: "Day care facilities" },
    ],
    pctOfTotal: ["health_insurance", "accident_insurance", "maternity_benefits", "paternity_benefits", "day_care_facilities"],
  },
  parental: {
    title: "Parental leave return and retention (EI 6)", path: "parental-leave", relation: "parental_leave", labels: PARENTAL_LABELS,
    fields: [
      { name: "return_to_work_rate_percent", label: "Return to work rate (%)", step: "0.01" },
      { name: "retention_rate_percent", label: "Retention rate (%)", step: "0.01" },
    ],
    pctOfTotal: [],
  },
  training: {
    title: "Training and performance reviews (EI 8-9)", path: "training", relation: "training", labels: TRAINING_LABELS,
    fields: [
      { name: "total_count", label: "Total (A)" },
      { name: "health_safety_trained", label: "Health & safety trained" },
      { name: "skill_upgraded", label: "Skill upgradation" },
      { name: "performance_reviewed", label: "Performance / career review" },
    ],
    pctOfTotal: ["health_safety_trained", "skill_upgraded", "performance_reviewed"],
  },
  complaint: {
    title: "Complaints on working conditions and health & safety (EI 13)", path: "complaints", relation: "complaints", labels: COMPLAINT_LABELS,
    fields: [
      { name: "filed_count", label: "Filed during the year" },
      { name: "pending_count", label: "Pending at year end" },
    ],
    pctOfTotal: [],
  },
};

export type ChildRow = { id: number; employee_wellbeing_record_id: number; category: string; remarks?: string | null } & Record<string, unknown>;

export interface EmployeeWellbeingFields {
  wellbeing_spend_percent_revenue?: number | null;
  pf_employees_percent?: number | null; pf_workers_percent?: number | null; pf_deposited?: "yes" | "no" | "na" | null;
  gratuity_employees_percent?: number | null; gratuity_workers_percent?: number | null; gratuity_deposited?: "yes" | "no" | "na" | null;
  esi_employees_percent?: number | null; esi_workers_percent?: number | null; esi_deposited?: "yes" | "no" | "na" | null;
  other_benefit_name?: string | null; other_benefit_employees_percent?: number | null; other_benefit_workers_percent?: number | null; other_benefit_deposited?: "yes" | "no" | "na" | null;
  premises_accessible_to_differently_abled?: boolean | null; accessibility_details?: string | null;
  has_equal_opportunity_policy?: boolean | null; equal_opportunity_policy_link?: string | null;
  permanent_employees_total?: number | null; permanent_employees_union_members?: number | null;
  permanent_workers_total?: number | null; permanent_workers_union_members?: number | null;
  has_ohs_management_system?: boolean | null; ohs_system_coverage?: string | null;
  hazard_identification_process?: string | null; non_routine_risk_reporting_process?: string | null;
  has_medical_facilities?: boolean | null; safety_assessments_details?: string | null;
  ltifr_employees?: number | null; ltifr_workers?: number | null;
  recordable_injuries_employees?: number | null; recordable_injuries_workers?: number | null;
  fatalities_employees?: number | null; fatalities_workers?: number | null;
  high_consequence_injuries_employees?: number | null; high_consequence_injuries_workers?: number | null;
  safe_workplace_measures?: string | null; complainant_protection_details?: string | null;
  assessed_health_safety_percent?: number | null; assessed_working_conditions_percent?: number | null;
  corrective_actions_from_assessments?: string | null;
  life_insurance_employees?: boolean | null; life_insurance_workers?: boolean | null;
  value_chain_statutory_dues_details?: string | null;
  rehabilitated_employees_count?: number | null; rehabilitated_workers_count?: number | null;
  has_transition_assistance?: boolean | null;
  value_chain_assessed_health_safety_percent?: number | null; value_chain_assessed_working_conditions_percent?: number | null;
  value_chain_corrective_actions?: string | null;
  remarks?: string | null;
}

export interface EmployeeWellbeingRecord extends EmployeeWellbeingFields {
  id: number; organization_id: number; reporting_year: number;
  wellbeing_measures: ChildRow[]; parental_leave: ChildRow[]; training: ChildRow[]; complaints: ChildRow[];
  permanent_employees_union_percent?: number | null; permanent_workers_union_percent?: number | null;
  total_complaints_filed?: number | null; total_complaints_pending?: number | null;
  created_at: string; updated_at?: string | null;
}
export interface EmployeeWellbeingRecordCreate extends EmployeeWellbeingFields { reporting_year: number; }
export interface EmployeeWellbeingRecordUpdate extends EmployeeWellbeingFields { reporting_year?: number; }

const BASE = "/employee-wellbeing-records";

export const employeeWellbeingApi = {
  getAll: async () => (await client.get<EmployeeWellbeingRecord[]>(`${BASE}/`)).data,
  create: async (data: EmployeeWellbeingRecordCreate) => (await client.post<EmployeeWellbeingRecord>(`${BASE}/`, data)).data,
  update: async (id: number, data: EmployeeWellbeingRecordUpdate) => (await client.put<EmployeeWellbeingRecord>(`${BASE}/${id}`, data)).data,
  remove: async (id: number) => { await client.delete(`${BASE}/${id}`); },
  createChild: async (kind: ChildKind, recordId: number, data: Record<string, unknown>) =>
    (await client.post<ChildRow>(`${BASE}/${recordId}/${CHILD_CONFIG[kind].path}`, data)).data,
  updateChild: async (kind: ChildKind, childId: number, data: Record<string, unknown>) =>
    (await client.put<ChildRow>(`${BASE}/${CHILD_CONFIG[kind].path}/${childId}`, data)).data,
  removeChild: async (kind: ChildKind, childId: number) => { await client.delete(`${BASE}/${CHILD_CONFIG[kind].path}/${childId}`); },
};
export default employeeWellbeingApi;
