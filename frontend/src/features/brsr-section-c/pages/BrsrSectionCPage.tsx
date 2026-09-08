import { Link } from "react-router-dom";
import {
  Scale, Package, HeartPulse, Handshake, HeartHandshake, Recycle, Landmark, Heart, MessageSquareWarning,
  type LucideIcon,
} from "lucide-react";

// SEBI's nine NGRBC principles, in SEBI order, each linking to its data page.
const PRINCIPLES: { n: number; title: string; summary: string; path: string; icon: LucideIcon }[] = [
  { n: 1, title: "Ethics, Transparency and Accountability", summary: "Training on principles, fines and penalties, anti-corruption, conflicts of interest.", path: "/ethics", icon: Scale },
  { n: 2, title: "Sustainable and Safe Goods and Services", summary: "R&D and capex on sustainable technologies, sourcing, product reclaim, EPR.", path: "/sustainable-products", icon: Package },
  { n: 3, title: "Employee Well-being", summary: "Well-being measures, retirement benefits, parental leave, unions, OHS, incidents, training, complaints.", path: "/employee-wellbeing", icon: HeartPulse },
  { n: 4, title: "Stakeholder Engagement", summary: "Identification of stakeholder groups, engagement channels and frequency, consultation.", path: "/stakeholder-engagement", icon: Handshake },
  { n: 5, title: "Human Rights", summary: "Training, minimum wages, remuneration, complaints, assessments, due diligence.", path: "/human-rights", icon: HeartHandshake },
  { n: 6, title: "Environment", summary: "Energy, water, emissions and waste -- water and waste disclosures entered here; energy and GHG flow from the carbon modules.", path: "/water-waste", icon: Recycle },
  { n: 7, title: "Public and Regulatory Policy Advocacy", summary: "Trade and industry association memberships, anti-competitive conduct.", path: "/policy-advocacy", icon: Landmark },
  { n: 8, title: "Inclusive Growth and Equitable Development", summary: "CSR projects, social impact assessments, aspirational districts.", path: "/csr", icon: Heart },
  { n: 9, title: "Responsible Engagement with Consumers", summary: "Consumer complaints, product information, recalls, cyber security, data breaches.", path: "/consumer-responsibility", icon: MessageSquareWarning },
];

export default function BrsrSectionCPage() {
  return (
    <div className="space-y-6 p-8">
      <div>
        <h1 className="text-3xl font-bold">BRSR Section C -- Principle-wise Performance</h1>
        <p className="text-gray-500">
          The nine NGRBC principles. Each opens its own disclosure page; every principle also feeds a report endpoint used by ESG Reports and the Filing Validator.
        </p>
      </div>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
        {PRINCIPLES.map(({ n, title, summary, path, icon: Icon }) => (
          <Link key={n} to={path} className="group rounded-xl border border-gray-200 bg-white p-5 shadow-sm transition hover:border-blue-400 hover:shadow-md">
            <div className="mb-3 flex items-center gap-3">
              <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-50 text-blue-600 group-hover:bg-blue-600 group-hover:text-white">
                <Icon size={20} />
              </span>
              <div>
                <p className="text-xs font-semibold uppercase tracking-wide text-gray-400">Principle {n}</p>
                <h2 className="font-semibold text-gray-800">{title}</h2>
              </div>
            </div>
            <p className="text-sm text-gray-500">{summary}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
