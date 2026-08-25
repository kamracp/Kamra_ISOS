import client from "../../../services/api/client";

export interface StakeholderGroup {
  id: number;
  engagement_record_id: number;
  group_name: string;
  is_vulnerable_marginalized?: boolean;
  communication_channels?: string;
  frequency_of_engagement?: string;
  purpose_and_scope?: string;
  remarks?: string;
  created_at: string;
  updated_at?: string;
}

export interface StakeholderGroupCreate {
  group_name: string;
  is_vulnerable_marginalized?: boolean;
  communication_channels?: string;
  frequency_of_engagement?: string;
  purpose_and_scope?: string;
  remarks?: string;
}

export interface StakeholderGroupUpdate {
  group_name?: string;
  is_vulnerable_marginalized?: boolean;
  communication_channels?: string;
  frequency_of_engagement?: string;
  purpose_and_scope?: string;
  remarks?: string;
}

export interface StakeholderEngagementRecord {
  id: number;
  organization_id: number;
  reporting_year: number;
  has_consultation_process?: boolean;
  consultation_process_details?: string;
  resulted_in_policy_change?: boolean;
  policy_change_details?: string;
  remarks?: string;
  stakeholder_groups: StakeholderGroup[];
  created_at: string;
  updated_at?: string;
}

export interface StakeholderEngagementRecordCreate {
  reporting_year: number;
  has_consultation_process?: boolean;
  consultation_process_details?: string;
  resulted_in_policy_change?: boolean;
  policy_change_details?: string;
  remarks?: string;
}

export interface StakeholderEngagementRecordUpdate {
  reporting_year?: number;
  has_consultation_process?: boolean;
  consultation_process_details?: string;
  resulted_in_policy_change?: boolean;
  policy_change_details?: string;
  remarks?: string;
}

export const stakeholderEngagementApi = {
  getAll: async (): Promise<StakeholderEngagementRecord[]> => {
    const response = await client.get<StakeholderEngagementRecord[]>("/stakeholder-engagement-records/");
    return response.data;
  },
  getById: async (id: number): Promise<StakeholderEngagementRecord> => {
    const response = await client.get<StakeholderEngagementRecord>(`/stakeholder-engagement-records/${id}`);
    return response.data;
  },
  create: async (data: StakeholderEngagementRecordCreate): Promise<StakeholderEngagementRecord> => {
    const response = await client.post<StakeholderEngagementRecord>("/stakeholder-engagement-records/", data);
    return response.data;
  },
  update: async (id: number, data: StakeholderEngagementRecordUpdate): Promise<StakeholderEngagementRecord> => {
    const response = await client.put<StakeholderEngagementRecord>(`/stakeholder-engagement-records/${id}`, data);
    return response.data;
  },
  remove: async (id: number): Promise<void> => {
    await client.delete(`/stakeholder-engagement-records/${id}`);
  },
  createGroup: async (recordId: number, data: StakeholderGroupCreate): Promise<StakeholderGroup> => {
    const response = await client.post<StakeholderGroup>(`/stakeholder-engagement-records/${recordId}/groups`, data);
    return response.data;
  },
  updateGroup: async (groupId: number, data: StakeholderGroupUpdate): Promise<StakeholderGroup> => {
    const response = await client.put<StakeholderGroup>(`/stakeholder-engagement-records/groups/${groupId}`, data);
    return response.data;
  },
  removeGroup: async (groupId: number): Promise<void> => {
    await client.delete(`/stakeholder-engagement-records/groups/${groupId}`);
  },
};

export default stakeholderEngagementApi;
