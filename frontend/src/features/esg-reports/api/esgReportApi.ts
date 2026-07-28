import client from "../../../services/api/client";

export interface Datapoint {
  value: number | null;
  unit?: string;
  status: "tracked" | "not_tracked";
  source?: string;
  note?: string;
}

export interface Indicator {
  label: string;
  data?: Datapoint;
  renewable_gj?: Datapoint;
  non_renewable_gj?: Datapoint;
  note?: string;
}

export interface BrsrReport {
  framework: string;
  section: string;
  reporting_year: number;
  organization_id: number;
  data_basis: string;
  essential_indicators: Record<string, Indicator>;
  totals: {
    scope1_plus_2_tCO2e: number;
    total_all_scopes: Datapoint;
  };
}

export const esgReportApi = {
  getBrsrPrinciple6: async (year: number): Promise<BrsrReport> => {
    const response = await client.get<BrsrReport>(
      "/esg-reports/brsr-principle6",
      { params: { year } },
    );
    return response.data;
  },
};

export default esgReportApi;