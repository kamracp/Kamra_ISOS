import client from "../../../services/api/client";

export interface EthicsRecord {
  id: number;
  organization_id: number;
  reporting_year: number;
  board_kmp_total_count?: number;
  board_kmp_trained_count?: number;
  employees_total_count?: number;
  employees_trained_count?: number;
  workers_total_count?: number;
  workers_trained_count?: number;
  disciplinary_actions_directors?: number;
  disciplinary_actions_kmp?: number;
  disciplinary_actions_employees?: number;
  disciplinary_actions_workers?: number;
  fines_penalties_amount_inr?: string;
  has_conflict_of_interest_process?: string;
  conflict_of_interest_disclosures_count?: number;
  corruption_complaints_received?: number;
  corruption_complaints_pending?: number;
  remarks?: string;
  board_kmp_trained_percent?: number;
  employees_trained_percent?: number;
  workers_trained_percent?: number;
  created_at: string;
  updated_at?: string;
}

export interface EthicsRecordCreate {
  reporting_year: number;
  board_kmp_total_count?: number;
  board_kmp_trained_count?: number;
  employees_total_count?: number;
  employees_trained_count?: number;
  workers_total_count?: number;
  workers_trained_count?: number;
  disciplinary_actions_directors?: number;
  disciplinary_actions_kmp?: number;
  disciplinary_actions_employees?: number;
  disciplinary_actions_workers?: number;
  fines_penalties_amount_inr?: number;
  has_conflict_of_interest_process?: string;
  conflict_of_interest_disclosures_count?: number;
  corruption_complaints_received?: number;
  corruption_complaints_pending?: number;
  remarks?: string;
}

export interface EthicsRecordUpdate {
  reporting_year?: number;
  board_kmp_total_count?: number;
  board_kmp_trained_count?: number;
  employees_total_count?: number;
  employees_trained_count?: number;
  workers_total_count?: number;
  workers_trained_count?: number;
  disciplinary_actions_directors?: number;
  disciplinary_actions_kmp?: number;
  disciplinary_actions_employees?: number;
  disciplinary_actions_workers?: number;
  fines_penalties_amount_inr?: number;
  has_conflict_of_interest_process?: string;
  conflict_of_interest_disclosures_count?: number;
  corruption_complaints_received?: number;
  corruption_complaints_pending?: number;
  remarks?: string;
}

export const ethicsApi = {
  getAll: async (): Promise<EthicsRecord[]> => {
    const response = await client.get<EthicsRecord[]>("/ethics-records/");
    return response.data;
  },
  getById: async (id: number): Promise<EthicsRecord> => {
    const response = await client.get<EthicsRecord>(`/ethics-records/${id}`);
    return response.data;
  },
  create: async (data: EthicsRecordCreate): Promise<EthicsRecord> => {
    const response = await client.post<EthicsRecord>("/ethics-records/", data);
    return response.data;
  },
  update: async (id: number, data: EthicsRecordUpdate): Promise<EthicsRecord> => {
    const response = await client.put<EthicsRecord>(`/ethics-records/${id}`, data);
    return response.data;
  },
  remove: async (id: number): Promise<void> => {
    await client.delete(`/ethics-records/${id}`);
  },
};

export default ethicsApi;
