import client from "../../../services/api/client";

export interface Building {
  category_id?: number | null;
  id: number;
  organization_id: number;
  building_code: string;
  building_name: string;
  description?: string;
  address_line_1?: string;
  address_line_2?: string;
  city?: string;
  state?: string;
  country?: string;
  pincode?: string;
  building_type?: string;
  total_floor_area?: number;
  number_of_floors?: number;
  year_constructed?: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface BuildingCreate {
  category_id?: number | null;
  building_code: string;
  building_name: string;
  description?: string;
  address_line_1?: string;
  address_line_2?: string;
  city?: string;
  state?: string;
  country?: string;
  pincode?: string;
  building_type?: string;
  total_floor_area?: number;
  number_of_floors?: number;
  year_constructed?: number;
  is_active?: boolean;
}

export interface BuildingUpdate {
  category_id?: number | null;
  building_code?: string;
  building_name?: string;
  description?: string;
  address_line_1?: string;
  address_line_2?: string;
  city?: string;
  state?: string;
  country?: string;
  pincode?: string;
  building_type?: string;
  total_floor_area?: number;
  number_of_floors?: number;
  year_constructed?: number;
  is_active?: boolean;
}

export const buildingApi = {
  getAll: async (): Promise<Building[]> => {
    const response = await client.get<Building[]>("/buildings/");
    return response.data;
  },
  getById: async (id: number): Promise<Building> => {
    const response = await client.get<Building>(`/buildings/${id}`);
    return response.data;
  },
  create: async (data: BuildingCreate): Promise<Building> => {
    const response = await client.post<Building>("/buildings/", data);
    return response.data;
  },
  update: async (id: number, data: BuildingUpdate): Promise<Building> => {
    const response = await client.put<Building>(`/buildings/${id}`, data);
    return response.data;
  },
  remove: async (id: number): Promise<void> => {
    await client.delete(`/buildings/${id}`);
  },
};

export default buildingApi;
