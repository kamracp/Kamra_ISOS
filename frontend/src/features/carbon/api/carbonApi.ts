import client from "../../../services/api/client";

// ── Types ────────────────────────────────────────────────────────────────────

export interface CarbonLineItem {
  bill_id: number;
  meter_id: number;
  meter_code: string;
  meter_name: string;
  meter_type: string;
  unit: string;
  scope: string;
  period_start: string;
  period_end: string;
  consumption: number;
  co2e_kg: number | null;
  factor_id: number | null;
  factor_value: number | null;
  factor_source: string | null;
  status: "calculated" | "no_factor";
}

export interface CarbonSummary {
  total_co2e_kg: number;
  total_co2e_tonnes: number;
  by_scope_kg: Record<string, number>;
  avoided_co2e_kg: number;
  monthly_co2e_kg: Record<string, number>;
  bills_calculated: number;
  bills_pending_factor: CarbonLineItem[];
  line_items: CarbonLineItem[];
}

// ── API calls ─────────────────────────────────────────────────────────────────

export const carbonApi = {
  async getSummary(year?: number): Promise<CarbonSummary> {
    const { data } = await client.get<CarbonSummary>("/carbon/summary", {
      params: year ? { year } : undefined,
    });
    return data;
  },
};
