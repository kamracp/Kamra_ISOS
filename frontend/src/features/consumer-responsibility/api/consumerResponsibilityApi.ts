import client from "../../../services/api/client";

export type ConsumerComplaintCategory =
  | "data_privacy" | "advertising" | "cyber_security" | "delivery_of_essential_services"
  | "restrictive_trade_practices" | "unfair_trade_practices" | "other";

export const COMPLAINT_LABELS: Record<ConsumerComplaintCategory, string> = {
  data_privacy: "Data privacy",
  advertising: "Advertising",
  cyber_security: "Cyber security",
  delivery_of_essential_services: "Delivery of essential services",
  restrictive_trade_practices: "Restrictive trade practices",
  unfair_trade_practices: "Unfair trade practices",
  other: "Other",
};

export interface ConsumerComplaintFields {
  category: ConsumerComplaintCategory;
  received_count?: number | null;
  pending_count?: number | null;
  remarks?: string | null;
}
export interface ConsumerComplaint extends ConsumerComplaintFields {
  id: number;
  consumer_responsibility_record_id: number;
  created_at: string;
  updated_at?: string | null;
}

export interface ConsumerResponsibilityFields {
  complaint_mechanism_details?: string | null;
  turnover_percent_env_social_info?: number | null;
  turnover_percent_safe_usage_info?: number | null;
  turnover_percent_recycling_info?: number | null;
  voluntary_recalls_count?: number | null;
  voluntary_recalls_reasons?: string | null;
  forced_recalls_count?: number | null;
  forced_recalls_reasons?: string | null;
  has_cyber_security_policy?: boolean | null;
  cyber_security_policy_link?: string | null;
  corrective_actions_details?: string | null;
  product_information_channels?: string | null;
  consumer_education_details?: string | null;
  service_disruption_disclosure_details?: string | null;
  displays_product_info_beyond_mandate?: boolean | null;
  consumer_survey_conducted?: boolean | null;
  consumer_survey_details?: string | null;
  data_breaches_count?: number | null;
  data_breach_pii_percent?: number | null;
  data_breach_impact_details?: string | null;
  remarks?: string | null;
}
export interface ConsumerResponsibilityRecord extends ConsumerResponsibilityFields {
  id: number;
  organization_id: number;
  reporting_year: number;
  complaints: ConsumerComplaint[];
  total_complaints_received?: number | null; // derived
  total_complaints_pending?: number | null; // derived
  created_at: string;
  updated_at?: string | null;
}
export interface ConsumerResponsibilityRecordCreate extends ConsumerResponsibilityFields { reporting_year: number; }
export interface ConsumerResponsibilityRecordUpdate extends ConsumerResponsibilityFields { reporting_year?: number; }

const BASE = "/consumer-responsibility-records";

export const consumerResponsibilityApi = {
  getAll: async () => (await client.get<ConsumerResponsibilityRecord[]>(`${BASE}/`)).data,
  create: async (data: ConsumerResponsibilityRecordCreate) => (await client.post<ConsumerResponsibilityRecord>(`${BASE}/`, data)).data,
  update: async (id: number, data: ConsumerResponsibilityRecordUpdate) => (await client.put<ConsumerResponsibilityRecord>(`${BASE}/${id}`, data)).data,
  remove: async (id: number) => { await client.delete(`${BASE}/${id}`); },
  createComplaint: async (recordId: number, data: ConsumerComplaintFields) => (await client.post<ConsumerComplaint>(`${BASE}/${recordId}/complaints`, data)).data,
  updateComplaint: async (id: number, data: Partial<ConsumerComplaintFields>) => (await client.put<ConsumerComplaint>(`${BASE}/complaints/${id}`, data)).data,
  removeComplaint: async (id: number) => { await client.delete(`${BASE}/complaints/${id}`); },
};
export default consumerResponsibilityApi;
