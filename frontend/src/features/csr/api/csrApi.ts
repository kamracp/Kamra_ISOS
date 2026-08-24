import client from "../../../services/api/client";

export interface CsrProject {
  id: number;
  csr_record_id: number;
  project_name: string;
  activity_category?: string;
  location?: string;
  is_local_area?: string;
  amount_spent_inr?: string;
  direct_beneficiaries_count?: number;
  remarks?: string;
  created_at: string;
  updated_at?: string;
}

export interface CsrProjectCreate {
  project_name: string;
  activity_category?: string;
  location?: string;
  is_local_area?: string;
  amount_spent_inr?: number;
  direct_beneficiaries_count?: number;
  remarks?: string;
}

export interface CsrProjectUpdate {
  project_name?: string;
  activity_category?: string;
  location?: string;
  is_local_area?: string;
  amount_spent_inr?: number;
  direct_beneficiaries_count?: number;
  remarks?: string;
}

export interface CsrRecord {
  id: number;
  organization_id: number;
  reporting_year: number;
  csr_budget_inr?: string;
  csr_amount_spent_inr?: string;
  csr_admin_overhead_inr?: string;
  remarks?: string;
  percent_spent_vs_budget?: number;
  total_project_spend_inr?: string;
  projects: CsrProject[];
  created_at: string;
  updated_at?: string;
}

export interface CsrRecordCreate {
  reporting_year: number;
  csr_budget_inr?: number;
  csr_amount_spent_inr?: number;
  csr_admin_overhead_inr?: number;
  remarks?: string;
}

export interface CsrRecordUpdate {
  reporting_year?: number;
  csr_budget_inr?: number;
  csr_amount_spent_inr?: number;
  csr_admin_overhead_inr?: number;
  remarks?: string;
}

export const csrApi = {
  getAll: async (): Promise<CsrRecord[]> => {
    const response = await client.get<CsrRecord[]>("/csr-records/");
    return response.data;
  },
  getById: async (id: number): Promise<CsrRecord> => {
    const response = await client.get<CsrRecord>(`/csr-records/${id}`);
    return response.data;
  },
  create: async (data: CsrRecordCreate): Promise<CsrRecord> => {
    const response = await client.post<CsrRecord>("/csr-records/", data);
    return response.data;
  },
  update: async (id: number, data: CsrRecordUpdate): Promise<CsrRecord> => {
    const response = await client.put<CsrRecord>(`/csr-records/${id}`, data);
    return response.data;
  },
  remove: async (id: number): Promise<void> => {
    await client.delete(`/csr-records/${id}`);
  },

  createProject: async (recordId: number, data: CsrProjectCreate): Promise<CsrProject> => {
    const response = await client.post<CsrProject>(`/csr-records/${recordId}/projects`, data);
    return response.data;
  },
  updateProject: async (projectId: number, data: CsrProjectUpdate): Promise<CsrProject> => {
    const response = await client.put<CsrProject>(`/csr-records/projects/${projectId}`, data);
    return response.data;
  },
  removeProject: async (projectId: number): Promise<void> => {
    await client.delete(`/csr-records/projects/${projectId}`);
  },
};

export default csrApi;
