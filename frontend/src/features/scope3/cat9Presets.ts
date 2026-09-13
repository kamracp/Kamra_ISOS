// Scope 3 category 9 (downstream distribution) presets for ceramic tiles: published market -> mode -> distance
// scenarios. Every row cites the document it was transcribed from (PDFs in backend/data/references/).
// Distances are one-way averages as published; picking a preset selects the DEFRA freight factor and fills
// quantity = tonnes shipped x distance_km (tonne.km). Mode mapping to DEFRA rows (chief decision, 13 Sep 2026):
// 32-t trailer / 27-t truck / "lorry" -> "HGV articulated >33 t, average laden"; ocean-going / transoceanic
// cargo ship / "tanker" (Ferrari 2019 wording for the sea leg) -> "Cargo ship, container ship" (tiles move containerised).
export interface Cat9Preset {
  id: string;
  label: string;
  meter_type: string;   // exact emission_factors.meter_type of the DEFRA freight row
  distance_km: number;  // one-way distance as published
  citation: string;
}

const HGV = "freight_hgv_articulated_33t_avg_laden";
const SHIP = "freight_cargo_ship_container_ship";
const IB = "Ibanez-Fores, Bovea & Simo (2011) Int J LCA 16:916-928, Table 4 (ASCER 2009 sales shares, average distance, transport type)";
const EPD = "Confindustria Ceramica / IBU EPD-COI-20160202-ICG1-EN (2016), section 4 'Transport to the building site (A4)'";
const FER = "Ferrari, Volpi, Pini, Siligardi, Garcia-Muina & Settembre-Blundo (2019) Resources 8:11, Table A5 (Italian porcelain stoneware, 2016, share of sales)";
const PINI = "Pini et al. (2014) Int J LCA 19:1567-1580, section 3.3: 100 km distribution scenario required by the EPD General Programme Instructions (2008)";

export const CAT9_PRESETS: Cat9Preset[] = [
  // Ibanez-Fores 2011, Table 4 - Spanish tile sector
  { id: "ib_national",    label: "Spain 2011 - national market, 32-t trailer (50% of sales)",               meter_type: HGV,  distance_km: 500,   citation: IB },
  { id: "ib_europe",      label: "Spain 2011 - rest of Europe, 32-t trailer (33.75%)",                      meter_type: HGV,  distance_km: 2000,  citation: IB },
  { id: "ib_america",     label: "Spain 2011 - America, ocean-going cargo ship (5.05%)",                    meter_type: SHIP, distance_km: 7000,  citation: IB },
  { id: "ib_middle_east", label: "Spain 2011 - Middle East, ocean-going cargo ship (5.55%)",                meter_type: SHIP, distance_km: 4000,  citation: IB },
  { id: "ib_asia",        label: "Spain 2011 - East and Southeast Asia, ocean-going cargo ship (1.35%)",    meter_type: SHIP, distance_km: 20000, citation: IB },
  { id: "ib_africa",      label: "Spain 2011 - Africa, ocean-going cargo ship (3.9%)",                      meter_type: SHIP, distance_km: 5000,  citation: IB },
  { id: "ib_oceania",     label: "Spain 2011 - Oceania, ocean-going cargo ship (0.4%)",                     meter_type: SHIP, distance_km: 20000, citation: IB },
  // Confindustria Ceramica EPD 2016, module A4 - Italian tile sector average
  { id: "epd_national",     label: "Italy EPD 2016 - national destination, 27-t truck (51% of tiles sold)", meter_type: HGV,  distance_km: 300,   citation: EPD },
  { id: "epd_europe",       label: "Italy EPD 2016 - European destination, 27-t truck (34%)",              meter_type: HGV,  distance_km: 1390,  citation: EPD },
  { id: "epd_transoceanic", label: "Italy EPD 2016 - transoceanic freight ship",                           meter_type: SHIP, distance_km: 6520,  citation: EPD },
  // Ferrari 2019, Table A5 - Italian porcelain stoneware; overseas markets = lorry leg to port + sea leg (two lines)
  { id: "fer_italy",        label: "Italy 2019 - domestic, lorry (20.24% of sales)",                        meter_type: HGV,  distance_km: 500,   citation: FER },
  { id: "fer_europe",       label: "Italy 2019 - Europe, lorry (39.88%)",                                   meter_type: HGV,  distance_km: 2780,  citation: FER },
  { id: "fer_port_leg",     label: "Italy 2019 - lorry leg to port for overseas markets",                   meter_type: HGV,  distance_km: 745,   citation: FER },
  { id: "fer_north_america", label: "Italy 2019 - North America, sea leg (15.95%)",                         meter_type: SHIP, distance_km: 10000, citation: FER },
  { id: "fer_south_america", label: "Italy 2019 - South America, sea leg (15.95%)",                         meter_type: SHIP, distance_km: 15000, citation: FER },
  { id: "fer_asia",         label: "Italy 2019 - Asia, sea leg (7.98%)",                                    meter_type: SHIP, distance_km: 14300, citation: FER },
  // EPD programme default when the real route is unknown
  { id: "epd_default_100",  label: "EPD default distribution scenario, road 100 km",                        meter_type: HGV,  distance_km: 100,   citation: PINI },
];
