import client from "../../../services/api/client";

export interface BrsrPolicyDisclosure {
  id: number;
  organization_id: number;
  principle: number;
  has_policy?: boolean | null;
  policy_board_approved?: boolean | null;
  policy_web_link?: string | null;
  translated_to_procedures?: boolean | null;
  extends_to_value_chain?: boolean | null;
  certifications?: string | null;
  commitments_and_targets?: string | null;
  performance_against_targets?: string | null;
  reason_no_policy?: string | null;
  created_at?: string;
  updated_at?: string;
}

/** One principle's edits. `principle` says which row to upsert. */
export type BrsrPolicyDisclosureUpdate = Partial<
  Omit<BrsrPolicyDisclosure, "id" | "organization_id" | "created_at" | "updated_at">
> & { principle: number };

export interface PrincipleStatus {
  principle: number;
  label: string;
  answered: boolean;
  complete: boolean;
  missing: string;
}

export interface BrsrPolicyCompleteness {
  organization_id: number;
  total_principles: number;
  answered_principles: number;
  complete_principles: number;
  completeness_percent: number;
  principles: PrincipleStatus[];
}

export interface PrincipleLabel {
  principle: number;
  label: string;
}

export const brsrPolicyApi = {
  getAll: async (): Promise<BrsrPolicyDisclosure[]> => {
    const response = await client.get<BrsrPolicyDisclosure[]>("/brsr-policy/");
    return response.data;
  },
  // Bulk: the page submits every principle it holds in one transaction.
  save: async (
    disclosures: BrsrPolicyDisclosureUpdate[]
  ): Promise<BrsrPolicyDisclosure[]> => {
    const response = await client.put<BrsrPolicyDisclosure[]>("/brsr-policy/", {
      disclosures,
    });
    return response.data;
  },
  getCompleteness: async (): Promise<BrsrPolicyCompleteness> => {
    const response = await client.get<BrsrPolicyCompleteness>(
      "/brsr-policy/completeness"
    );
    return response.data;
  },
  getPrinciples: async (): Promise<PrincipleLabel[]> => {
    const response = await client.get<PrincipleLabel[]>("/brsr-policy/principles");
    return response.data;
  },
};
