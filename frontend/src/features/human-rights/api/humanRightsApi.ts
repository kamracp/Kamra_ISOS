import client from "../../../services/api/client";

// Category unions must match the backend Literals and DB CHECKs.
export type WorkforceCategory = "permanent_employees" | "other_employees" | "permanent_workers" | "other_workers";
export type RemunerationCategory = "bod" | "kmp" | "employees" | "workers";
export type ComplaintCategory = "sexual_harassment" | "discrimination" | "child_labour" | "forced_labour" | "wages" | "other";

export const WORKFORCE_LABELS: Record<WorkforceCategory, string> = {
  permanent_employees: "Permanent employees",
  other_employees: "Other than permanent employees",
  permanent_workers: "Permanent workers",
  other_workers: "Other than permanent workers",
};
export const REMUNERATION_LABELS: Record<RemunerationCategory, string> = {
  bod: "Board of Directors",
  kmp: "Key Managerial Personnel",
  employees: "Employees other than BoD and KMP",
  workers: "Workers",
};
export const COMPLAINT_LABELS: Record<ComplaintCategory, string> = {
  sexual_harassment: "Sexual harassment",
  discrimination: "Discrimination at workplace",
  child_labour: "Child labour",
  forced_labour: "Forced / involuntary labour",
  wages: "Wages",
  other: "Other human rights issues",
};

interface ChildMeta {
  id: number;
  human_rights_record_id: number;
  created_at: string;
  updated_at?: string | null;
}

export interface WorkforceCoverageFields {
  category: WorkforceCategory;
  total_count?: number | null;
  hr_training_covered?: number | null;
  equal_min_wage_male?: number | null;
  equal_min_wage_female?: number | null;
  more_than_min_wage_male?: number | null;
  more_than_min_wage_female?: number | null;
  remarks?: string | null;
}
export interface WorkforceCoverage extends WorkforceCoverageFields, ChildMeta {
  hr_training_coverage_percent?: number | null; // derived by backend
}

export interface RemunerationFields {
  category: RemunerationCategory;
  male_count?: number | null;
  male_median_inr?: number | null;
  female_count?: number | null;
  female_median_inr?: number | null;
  remarks?: string | null;
}
export interface Remuneration extends RemunerationFields, ChildMeta {}

export interface ComplaintFields {
  category: ComplaintCategory;
  filed_count?: number | null;
  pending_count?: number | null;
  remarks?: string | null;
}
export interface Complaint extends ComplaintFields, ChildMeta {}

export type ChildKind = "workforce" | "remuneration" | "complaint";
export type ChildFields = WorkforceCoverageFields | RemunerationFields | ComplaintFields;
export type ChildRow = WorkforceCoverage | Remuneration | Complaint;

export interface HumanRightsFields {
  has_human_rights_focal_point?: boolean | null;
  focal_point_details?: string | null;
  grievance_mechanism_details?: string | null;
  complainant_protection_details?: string | null;
  hr_requirements_in_contracts?: boolean | null;
  hr_requirements_details?: string | null;
  assessed_child_labour_percent?: number | null;
  assessed_forced_labour_percent?: number | null;
  assessed_sexual_harassment_percent?: number | null;
  assessed_discrimination_percent?: number | null;
  assessed_wages_percent?: number | null;
  assessed_other_percent?: number | null;
  assessed_other_description?: string | null;
  corrective_actions_from_assessments?: string | null;
  process_modifications_from_grievances?: string | null;
  human_rights_due_diligence_details?: string | null;
  premises_accessible_to_differently_abled?: boolean | null;
  accessibility_details?: string | null;
  value_chain_partners_assessed_percent?: number | null;
  value_chain_assessment_details?: string | null;
  value_chain_corrective_actions?: string | null;
  remarks?: string | null;
}

export interface HumanRightsRecord extends HumanRightsFields {
  id: number;
  organization_id: number;
  reporting_year: number;
  workforce_coverage: WorkforceCoverage[];
  remuneration: Remuneration[];
  complaints: Complaint[];
  total_complaints_filed?: number | null; // derived
  total_complaints_pending?: number | null; // derived
  created_at: string;
  updated_at?: string | null;
}
export interface HumanRightsRecordCreate extends HumanRightsFields { reporting_year: number; }
export interface HumanRightsRecordUpdate extends HumanRightsFields { reporting_year?: number; }

const BASE = "/human-rights-records";
// URL segment per child kind (the API uses plural "complaints").
const CHILD_PATH: Record<ChildKind, string> = { workforce: "workforce", remuneration: "remuneration", complaint: "complaints" };

export const humanRightsApi = {
  getAll: async (): Promise<HumanRightsRecord[]> => (await client.get<HumanRightsRecord[]>(`${BASE}/`)).data,
  getById: async (id: number): Promise<HumanRightsRecord> => (await client.get<HumanRightsRecord>(`${BASE}/${id}`)).data,
  create: async (data: HumanRightsRecordCreate): Promise<HumanRightsRecord> => (await client.post<HumanRightsRecord>(`${BASE}/`, data)).data,
  update: async (id: number, data: HumanRightsRecordUpdate): Promise<HumanRightsRecord> => (await client.put<HumanRightsRecord>(`${BASE}/${id}`, data)).data,
  remove: async (id: number): Promise<void> => { await client.delete(`${BASE}/${id}`); },
  createChild: async (kind: ChildKind, recordId: number, data: ChildFields): Promise<ChildRow> =>
    (await client.post<ChildRow>(`${BASE}/${recordId}/${CHILD_PATH[kind]}`, data)).data,
  updateChild: async (kind: ChildKind, childId: number, data: Partial<ChildFields>): Promise<ChildRow> =>
    (await client.put<ChildRow>(`${BASE}/${CHILD_PATH[kind]}/${childId}`, data)).data,
  removeChild: async (kind: ChildKind, childId: number): Promise<void> => { await client.delete(`${BASE}/${CHILD_PATH[kind]}/${childId}`); },
};

export default humanRightsApi;
