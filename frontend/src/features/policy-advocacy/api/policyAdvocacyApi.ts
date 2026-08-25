import client from "../../../services/api/client";

export interface TradeAssociation {
  id: number;
  policy_advocacy_record_id: number;
  association_name: string;
  reach?: string;
  remarks?: string;
  created_at: string;
  updated_at?: string;
}

export interface TradeAssociationCreate {
  association_name: string;
  reach?: string;
  remarks?: string;
}

export interface TradeAssociationUpdate {
  association_name?: string;
  reach?: string;
  remarks?: string;
}

export interface PolicyAdvocacyRecord {
  id: number;
  organization_id: number;
  reporting_year: number;
  has_anti_competitive_conduct_issue?: boolean;
  anti_competitive_conduct_details?: string;
  corrective_action_taken?: string;
  remarks?: string;
  associations: TradeAssociation[];
  created_at: string;
  updated_at?: string;
}

export interface PolicyAdvocacyRecordCreate {
  reporting_year: number;
  has_anti_competitive_conduct_issue?: boolean;
  anti_competitive_conduct_details?: string;
  corrective_action_taken?: string;
  remarks?: string;
}

export interface PolicyAdvocacyRecordUpdate {
  reporting_year?: number;
  has_anti_competitive_conduct_issue?: boolean;
  anti_competitive_conduct_details?: string;
  corrective_action_taken?: string;
  remarks?: string;
}

export const policyAdvocacyApi = {
  getAll: async (): Promise<PolicyAdvocacyRecord[]> => {
    const response = await client.get<PolicyAdvocacyRecord[]>("/policy-advocacy-records/");
    return response.data;
  },
  getById: async (id: number): Promise<PolicyAdvocacyRecord> => {
    const response = await client.get<PolicyAdvocacyRecord>(`/policy-advocacy-records/${id}`);
    return response.data;
  },
  create: async (data: PolicyAdvocacyRecordCreate): Promise<PolicyAdvocacyRecord> => {
    const response = await client.post<PolicyAdvocacyRecord>("/policy-advocacy-records/", data);
    return response.data;
  },
  update: async (id: number, data: PolicyAdvocacyRecordUpdate): Promise<PolicyAdvocacyRecord> => {
    const response = await client.put<PolicyAdvocacyRecord>(`/policy-advocacy-records/${id}`, data);
    return response.data;
  },
  remove: async (id: number): Promise<void> => {
    await client.delete(`/policy-advocacy-records/${id}`);
  },
  createAssociation: async (recordId: number, data: TradeAssociationCreate): Promise<TradeAssociation> => {
    const response = await client.post<TradeAssociation>(`/policy-advocacy-records/${recordId}/associations`, data);
    return response.data;
  },
  updateAssociation: async (associationId: number, data: TradeAssociationUpdate): Promise<TradeAssociation> => {
    const response = await client.put<TradeAssociation>(`/policy-advocacy-records/associations/${associationId}`, data);
    return response.data;
  },
  removeAssociation: async (associationId: number): Promise<void> => {
    await client.delete(`/policy-advocacy-records/associations/${associationId}`);
  },
};

export default policyAdvocacyApi;
