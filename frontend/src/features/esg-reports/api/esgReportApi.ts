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

export interface EsgReport {
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

// Kept as an alias so any existing import of BrsrReport still works.
export type BrsrReport = EsgReport;

export type ReportFramework = "brsr" | "gri-305" | "esrs-e1";

export const REPORT_FRAMEWORK_LABELS: Record<ReportFramework, string> = {
  brsr: "BRSR (India)",
  "gri-305": "GRI 305 (Global)",
  "esrs-e1": "ESRS E1 (EU / CSRD)",
};

const FRAMEWORK_ENDPOINTS: Record<ReportFramework, string> = {
  brsr: "/esg-reports/brsr-principle6",
  "gri-305": "/esg-reports/gri-305",
  "esrs-e1": "/esg-reports/esrs-e1",
};

export const esgReportApi = {
  getReport: async (
    framework: ReportFramework,
    year: number,
  ): Promise<EsgReport> => {
    const response = await client.get<EsgReport>(
      FRAMEWORK_ENDPOINTS[framework],
      { params: { year } },
    );
    return response.data;
  },

  downloadReportPdf: async (
    framework: ReportFramework,
    year: number,
  ): Promise<void> => {
    const response = await client.get(
      `${FRAMEWORK_ENDPOINTS[framework]}/pdf`,
      { params: { year }, responseType: "blob" },
    );

    const blob = new Blob([response.data], { type: "application/pdf" });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${framework}-${year}.pdf`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },

  // Kept for backward compatibility with any existing caller.
  getBrsrPrinciple6: async (year: number): Promise<EsgReport> => {
    return esgReportApi.getReport("brsr", year);
  },
};

export default esgReportApi;