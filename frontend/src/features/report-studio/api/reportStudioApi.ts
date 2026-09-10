import client from "../../../services/api/client";

// Mirrors backend app/schemas/report_narrative.py

export interface Milestone {
  year: number;
  title: string;
  description?: string | null;
}

export interface PrincipleNarrative {
  principle: number; // 1-9
  highlight?: string | null;
  intro?: string | null;
  sdgs: number[]; // 1-17
}

export interface ReportNarrative {
  id: number;
  organization_id: number;
  reporting_year: number;
  cover_title?: string | null;
  cover_subtitle?: string | null;
  theme_colour?: string | null; // "#RRGGBB"
  about_company?: string | null;
  leadership_message?: string | null;
  leadership_name?: string | null;
  leadership_designation?: string | null;
  milestones?: Milestone[] | null;
  principle_narratives?: PrincipleNarrative[] | null;
  created_at?: string | null;
  updated_at?: string | null;
}

export type ReportNarrativeUpdate = Partial<Omit<ReportNarrative, "id" | "organization_id" | "reporting_year" | "created_at" | "updated_at">>;

export interface NarrativeCompleteness {
  reporting_year: number;
  exists: boolean;
  answered: number;
  total: number;
  percent: number;
  entity_answered: number;
  entity_total: number;
  principles: Record<string, boolean>;
  missing: string[];
}

export interface SdgLabel {
  number: number;
  label: string;
}

const BASE = "/report-narratives";

export const reportStudioApi = {
  getNarrative: async (year: number): Promise<ReportNarrative | null> => {
    const { data } = await client.get<ReportNarrative | null>(`${BASE}/`, { params: { year } });
    return data;
  },

  saveNarrative: async (year: number, payload: ReportNarrativeUpdate): Promise<ReportNarrative> => {
    const { data } = await client.put<ReportNarrative>(`${BASE}/`, payload, { params: { year } });
    return data;
  },

  getCompleteness: async (year: number): Promise<NarrativeCompleteness> => {
    const { data } = await client.get<NarrativeCompleteness>(`${BASE}/completeness`, { params: { year } });
    return data;
  },

  getYears: async (): Promise<number[]> => {
    const { data } = await client.get<number[]>(`${BASE}/years`);
    return data;
  },

  getSdgs: async (): Promise<SdgLabel[]> => {
    const { data } = await client.get<SdgLabel[]>(`${BASE}/sdgs`);
    return data;
  },

  downloadCompletePdf: async (year: number): Promise<void> => {
    const response = await client.get("/report-studio/complete/pdf", {
      params: { year },
      responseType: "blob",
    });
    const blob = new Blob([response.data], { type: "application/pdf" });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `sustainability-report-${year}.pdf`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },
};
