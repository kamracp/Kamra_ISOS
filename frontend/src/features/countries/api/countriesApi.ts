import client from "../../../services/api/client";

export type Region = "india" | "asia" | "middle_east" | "europe";

export interface Country {
  code: string;
  name: string;
  region: Region;
  grid_factor_kgco2e_per_kwh: number | null;
  grid_factor_source: string;
  applicable_standards: string;
  needs_verification: boolean;
}

export const countriesApi = {
  getAll: async (): Promise<Country[]> => {
    const response = await client.get<Country[]>("/countries/");
    return response.data;
  },
  getByCode: async (code: string): Promise<Country> => {
    const response = await client.get<Country>(`/countries/${code}`);
    return response.data;
  },
};

export default countriesApi;
