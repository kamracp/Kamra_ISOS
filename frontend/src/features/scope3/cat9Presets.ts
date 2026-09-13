// Scope 3 category 9 (downstream distribution) presets: typical market -> mode -> distance
// scenarios for ceramic tiles, transcribed from Ibáñez-Forés, Bovea & Simó (2011), Int J LCA 16:916-928, Table 4.
// Picking a preset selects the DEFRA freight factor and fills quantity = tonnes shipped x distance_km (tonne.km).
// EMPTY until Table 4 is transcribed from the paper itself: distances are never typed from memory.
export interface Cat9Preset {
  id: string;
  label: string;        // e.g. "National market, road"
  meter_type: string;   // exact emission_factors.meter_type of the DEFRA freight row, e.g. "freight_hgv_all_hgvs_avg_laden"
  distance_km: number;  // one-way distance as published
  citation: string;     // "Ibáñez-Forés et al. 2011, Table 4, row ..."
}

export const CAT9_PRESETS: Cat9Preset[] = [];
