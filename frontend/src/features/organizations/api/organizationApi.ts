import client from "../../../services/api/client";

export interface Organization {
  id: number;

  organization_code: string;
  organization_name: string;
  legal_name?: string;

  industry?: string;

  email?: string;
  phone?: string;
  website?: string;

  country?: string;
  state?: string;
  city?: string;

  timezone?: string;
  currency?: string;
  employee_count?: number;
  annual_revenue_inr?: number;

  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface OrganizationUpdate {
  organization_name?: string;
  legal_name?: string;

  industry?: string;

  email?: string;
  phone?: string;
  website?: string;

  country?: string;
  state?: string;
  city?: string;

  timezone?: string;
  currency?: string;
  employee_count?: number;
  annual_revenue_inr?: number;
}

export const organizationApi = {
  // Multi-tenant: a user only ever sees their own organization
  getMy: async (): Promise<Organization> => {
    const response = await client.get<Organization>("/organizations/me");
    return response.data;
  },

  updateMy: async (data: OrganizationUpdate): Promise<Organization> => {
    const response = await client.put<Organization>(
      "/organizations/me",
      data
    );
    return response.data;
  },
};

export default organizationApi;
