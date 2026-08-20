import client from "../../../services/api/client";

export type ReportingBoundary = "standalone" | "consolidated";
export type PolicyReviewFrequency =
  | "annually"
  | "half_yearly"
  | "quarterly"
  | "other";

export interface LocationSplit {
  national: number;
  international: number;
}

export interface LocationCounts {
  plants: LocationSplit;
  offices: LocationSplit;
}

export interface MarketsServed {
  national_states?: number;
  international_countries?: number;
  exports_percent?: number;
  customer_types?: string;
}

export interface WomenParticipation {
  board_total?: number;
  board_female?: number;
  kmp_total?: number;
  kmp_female?: number;
}

/**
 * BRSR Section A profile.
 *
 * Repeating disclosure blocks (business_activities, products_sold,
 * employee_worker_counts, turnover_rates, group_companies,
 * grievance_redressal) are stored as JSONB server-side. They are typed
 * loosely here for now: the repeating-row UI for them is a second
 * iteration, so the current form does not read or write them.
 */
export interface BrsrProfile {
  id: number;
  organization_id: number;

  // A.I Details of the listed entity
  cin?: string;
  year_of_incorporation?: number;
  registered_office_address?: string;
  corporate_address?: string;
  contact_email?: string;
  contact_telephone?: string;
  website?: string;
  financial_year_reported?: string;
  stock_exchanges_listed?: string[];
  paid_up_capital_inr?: number;
  brsr_contact_name?: string;
  brsr_contact_phone?: string;
  brsr_contact_email?: string;
  reporting_boundary?: ReportingBoundary;

  // A.II Products and services (repeating - not in v1 form)
  business_activities?: unknown[];
  products_sold?: unknown[];

  // A.III Operations
  location_counts?: LocationCounts;
  markets_served?: MarketsServed;

  // A.IV Employees
  employee_worker_counts?: unknown;
  differently_abled_counts?: unknown;
  women_participation?: WomenParticipation;
  turnover_rates?: unknown[];

  // A.V Group companies (repeating - not in v1 form)
  group_companies?: unknown[];

  // A.VI CSR
  csr_applicable?: boolean;
  csr_turnover_inr?: number;
  csr_net_worth_inr?: number;

  // A.VII Grievances (repeating - not in v1 form)
  grievance_redressal?: unknown[];

  // A.VIII Assurance
  assurance_provider_name?: string;
  assurance_type?: string;

  // Section B, entity-level (Q10-Q12). Stored on the profile because they
  // are asked once for the whole entity, but edited on the Section B page.
  has_sustainability_committee?: boolean;
  policy_review_frequency?: PolicyReviewFrequency;
  independent_assessment_agency?: string;

  created_at?: string;
  updated_at?: string;
}

/** PUT body. Only the keys present are applied server-side (exclude_unset). */
export type BrsrProfileUpdate = Partial<Omit<BrsrProfile, "id" | "organization_id" | "created_at" | "updated_at">>;

export interface CompletenessQuestion {
  question: string;
  label: string;
  answered: boolean;
}

export interface BrsrCompleteness {
  organization_id: number;
  profile_exists: boolean;
  tracked_questions: number;
  answered_questions: number;
  completeness_percent: number;
  questions: CompletenessQuestion[];
}

export const brsrProfileApi = {
  // Returns null (not 404) when no profile exists yet.
  get: async (): Promise<BrsrProfile | null> => {
    const response = await client.get<BrsrProfile | null>("/brsr-profile/");
    return response.data;
  },
  save: async (data: BrsrProfileUpdate): Promise<BrsrProfile> => {
    const response = await client.put<BrsrProfile>("/brsr-profile/", data);
    return response.data;
  },
  getCompleteness: async (): Promise<BrsrCompleteness> => {
    const response = await client.get<BrsrCompleteness>("/brsr-profile/completeness");
    return response.data;
  },
  remove: async (): Promise<void> => {
    await client.delete("/brsr-profile/");
  },
};
