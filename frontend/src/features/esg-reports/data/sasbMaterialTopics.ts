/**
 * Sector-level ESG materiality reference, informed by SASB's
 * industry-materiality approach (financially material issues differ
 * by sector) but scoped to the PatSector values this platform already
 * tracks -- not a full 77-industry taxonomy. Informational only: does
 * NOT change any calculation, just highlights which topics matter most
 * for the selected sector, mirroring the kind of materiality matrix
 * seen in real sustainability reports (e.g. Prism Johnson's M1-M21
 * High/Medium/Low table).
 */
import type { PatSector } from "../../manufacturing-units/api/manufacturingUnitApi";

export interface MaterialTopic {
  topic: string;
  priority: "High" | "Medium";
}

export const SASB_MATERIAL_TOPICS: Record<PatSector, MaterialTopic[]> = {
  cement: [
    { topic: "GHG emissions (process + energy)", priority: "High" },
    { topic: "Air quality (PM, NOx, SOx)", priority: "High" },
    { topic: "Energy management", priority: "High" },
    { topic: "Water management", priority: "Medium" },
    { topic: "Waste and byproduct management", priority: "Medium" },
  ],
  aluminium: [
    { topic: "Energy management (highly electricity-intensive)", priority: "High" },
    { topic: "GHG emissions", priority: "High" },
    { topic: "Water management", priority: "Medium" },
    { topic: "Waste management (red mud / process waste)", priority: "High" },
    { topic: "Supply chain (bauxite sourcing)", priority: "Medium" },
  ],
  iron_steel: [
    { topic: "GHG emissions", priority: "High" },
    { topic: "Energy management", priority: "High" },
    { topic: "Air quality", priority: "Medium" },
    { topic: "Water management", priority: "Medium" },
    { topic: "Worker health and safety", priority: "High" },
  ],
  pulp_paper: [
    { topic: "Water management and effluent", priority: "High" },
    { topic: "Biogenic GHG emissions", priority: "High" },
    { topic: "Sustainable forestry / raw material sourcing", priority: "High" },
    { topic: "Air quality", priority: "Medium" },
    { topic: "Waste management", priority: "Medium" },
  ],
  chlor_alkali: [
    { topic: "Hazardous materials management", priority: "High" },
    { topic: "Energy management", priority: "High" },
    { topic: "Air and water emissions", priority: "High" },
    { topic: "Worker health and safety", priority: "High" },
  ],
  fertilizer: [
    { topic: "GHG emissions", priority: "High" },
    { topic: "Water management", priority: "Medium" },
    { topic: "Air quality", priority: "Medium" },
    { topic: "Product safety and handling", priority: "High" },
  ],
  petrochemicals: [
    { topic: "GHG emissions", priority: "High" },
    { topic: "Air quality", priority: "High" },
    { topic: "Hazardous materials management", priority: "High" },
    { topic: "Water management", priority: "Medium" },
    { topic: "Process safety", priority: "High" },
  ],
  refineries: [
    { topic: "GHG emissions", priority: "High" },
    { topic: "Air quality", priority: "High" },
    { topic: "Water management", priority: "Medium" },
    { topic: "Process safety and emergency management", priority: "High" },
  ],
  thermal_power: [
    { topic: "GHG emissions", priority: "High" },
    { topic: "Air quality", priority: "High" },
    { topic: "Water management", priority: "High" },
    { topic: "Coal ash / waste management", priority: "High" },
  ],
  textile: [
    { topic: "Water management and effluent", priority: "High" },
    { topic: "Energy management", priority: "Medium" },
    { topic: "Chemical/dye management", priority: "High" },
    { topic: "Labour practices in supply chain", priority: "Medium" },
  ],
  discoms: [
    { topic: "Grid reliability and access", priority: "High" },
    { topic: "End-use energy efficiency", priority: "Medium" },
    { topic: "GHG emissions (transmission losses)", priority: "Medium" },
  ],
  railways: [
    { topic: "Energy management", priority: "Medium" },
    { topic: "GHG emissions", priority: "Medium" },
    { topic: "Worker and public safety", priority: "High" },
  ],
  other: [
    { topic: "GHG emissions", priority: "High" },
    { topic: "Energy management", priority: "High" },
    { topic: "Water management", priority: "Medium" },
    { topic: "Waste management", priority: "Medium" },
  ],
};
