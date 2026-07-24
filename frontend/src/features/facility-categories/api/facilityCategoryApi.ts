import client from "../../../services/api/client";

export interface FacilityCategory {
  id: number;
  organization_id: number;
  segment: "benas" | "manufacturing";
  name: string;
  display_order: number;
}

export interface FacilityCategoryCreate {
  segment: "benas" | "manufacturing";
  name: string;
  display_order?: number;
}

export const facilityCategoryApi = {
  getBySegment: async (segment: "benas" | "manufacturing"): Promise<FacilityCategory[]> => {
    const response = await client.get<FacilityCategory[]>("/facility-categories/", {
      params: { segment },
    });
    return response.data;
  },
  create: async (data: FacilityCategoryCreate): Promise<FacilityCategory> => {
    const response = await client.post<FacilityCategory>("/facility-categories/", data);
    return response.data;
  },
  remove: async (id: number): Promise<void> => {
    await client.delete(`/facility-categories/${id}`);
  },
};

export default facilityCategoryApi;
