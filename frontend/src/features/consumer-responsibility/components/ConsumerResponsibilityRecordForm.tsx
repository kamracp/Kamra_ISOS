import DisclosureForm, { type SectionDef } from "../../../components/brsr/DisclosureForm";
import type {
  ConsumerResponsibilityFields, ConsumerResponsibilityRecord,
  ConsumerResponsibilityRecordCreate, ConsumerResponsibilityRecordUpdate,
} from "../api/consumerResponsibilityApi";

type K = keyof ConsumerResponsibilityFields;

export const CONSUMER_SECTIONS: SectionDef<K>[] = [
  {
    title: "EI 1 -- Consumer Complaints and Feedback",
    fields: [{ name: "complaint_mechanism_details", label: "Mechanisms to receive and respond to consumer complaints and feedback", kind: "textarea" }],
  },
  {
    title: "EI 2 -- Product Information (% of turnover)",
    subtitle: "Share of turnover from products/services that carry the information.",
    fields: [
      { name: "turnover_percent_env_social_info", label: "Environmental and social parameters (%)", kind: "pct" },
      { name: "turnover_percent_safe_usage_info", label: "Safe and responsible usage (%)", kind: "pct" },
      { name: "turnover_percent_recycling_info", label: "Recycling and/or safe disposal (%)", kind: "pct" },
    ],
  },
  {
    title: "EI 3 -- Product Recalls",
    fields: [
      { name: "voluntary_recalls_count", label: "Voluntary recalls -- number", kind: "int" },
      { name: "forced_recalls_count", label: "Forced recalls -- number", kind: "int" },
      { name: "voluntary_recalls_reasons", label: "Voluntary recalls -- reasons", kind: "textarea" },
      { name: "forced_recalls_reasons", label: "Forced recalls -- reasons", kind: "textarea" },
    ],
  },
  {
    title: "EI 4 & 5 -- Cyber Security and Corrective Actions",
    fields: [
      { name: "has_cyber_security_policy", label: "Framework / policy on cyber security and data privacy?", kind: "yesno" },
      { name: "cyber_security_policy_link", label: "Policy web link", kind: "text" },
      { name: "corrective_actions_details", label: "Corrective actions on advertising, delivery, recalls, cyber/data privacy issues", kind: "textarea" },
    ],
  },
  {
    title: "Leadership Indicators",
    fields: [
      { name: "product_information_channels", label: "Channels where product/service information is available", kind: "textarea" },
      { name: "consumer_education_details", label: "Steps to inform and educate consumers on safe and responsible usage", kind: "textarea" },
      { name: "service_disruption_disclosure_details", label: "Mechanisms to inform consumers of risk of disruption / discontinuation", kind: "textarea" },
      { name: "displays_product_info_beyond_mandate", label: "Displays product information beyond what is mandated?", kind: "yesno" },
      { name: "consumer_survey_conducted", label: "Consumer satisfaction survey conducted?", kind: "yesno" },
      { name: "consumer_survey_details", label: "Survey details", kind: "textarea" },
      { name: "data_breaches_count", label: "Data breaches -- number", kind: "int" },
      { name: "data_breach_pii_percent", label: "Breaches involving personally identifiable information (%)", kind: "pct" },
      { name: "data_breach_impact_details", label: "Impact of data breaches", kind: "textarea" },
      { name: "remarks", label: "Remarks", kind: "textarea" },
    ],
  },
];

interface Props {
  initialData?: ConsumerResponsibilityRecord;
  onSubmit: (data: ConsumerResponsibilityRecordCreate | ConsumerResponsibilityRecordUpdate) => void;
  onCancel?: () => void;
  loading?: boolean;
}

export default function ConsumerResponsibilityRecordForm({ initialData, onSubmit, onCancel, loading }: Props) {
  return (
    <DisclosureForm
      title="Principle 9 Record"
      subtitle="BRSR Principle 9 -- responsible engagement with consumers. One record per reporting year; complaint rows are added on the record card."
      sections={CONSUMER_SECTIONS}
      initialData={initialData as unknown as Record<string, unknown> & { reporting_year: number }}
      onSubmit={(data) => onSubmit(data as ConsumerResponsibilityRecordCreate | ConsumerResponsibilityRecordUpdate)}
      onCancel={onCancel}
      loading={loading}
    />
  );
}
