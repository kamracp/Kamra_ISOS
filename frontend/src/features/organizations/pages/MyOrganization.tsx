import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";

import organizationApi, {
  type OrganizationUpdate,
} from "../api/organizationApi";

const QUERY_KEY = ["my-organization"] as const;

export default function MyOrganization() {
  const queryClient = useQueryClient();

  const { data: org, isLoading } = useQuery({
    queryKey: QUERY_KEY,
    queryFn: organizationApi.getMy,
  });

  const [form, setForm] = useState<OrganizationUpdate>({});

  useEffect(() => {
    if (org) {
      setForm({
        organization_name: org.organization_name ?? "",
        legal_name: org.legal_name ?? "",
        industry: org.industry ?? "",
        email: org.email ?? "",
        phone: org.phone ?? "",
        website: org.website ?? "",
        country: org.country ?? "",
        state: org.state ?? "",
        city: org.city ?? "",
        employee_count: org.employee_count,
        annual_revenue_inr: org.annual_revenue_inr,
      });
    }
  }, [org]);

  const mutation = useMutation({
    mutationFn: organizationApi.updateMy,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      toast.success("Organization updated.");
    },
    onError: (error: any) => {
      toast.error(
        error?.response?.data?.detail ?? "Failed to update organization."
      );
    },
  });

  const setField = (key: keyof OrganizationUpdate, value: string) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const setNumericField = (
    key: "employee_count" | "annual_revenue_inr",
    value: string
  ) => {
    setForm((prev) => ({
      ...prev,
      [key]: value === "" ? undefined : Number(value),
    }));
  };

  if (isLoading) {
    return <p className="p-6 text-slate-500">Loading organization...</p>;
  }

  if (!org) {
    return <p className="p-6 text-red-500">Could not load organization.</p>;
  }

  const fields: Array<{
    key: keyof OrganizationUpdate;
    label: string;
  }> = [
    { key: "organization_name", label: "Organization Name" },
    { key: "legal_name", label: "Legal Name" },
    { key: "industry", label: "Industry" },
    { key: "email", label: "Email" },
    { key: "phone", label: "Phone" },
    { key: "website", label: "Website" },
    { key: "country", label: "Country" },
    { key: "state", label: "State" },
    { key: "city", label: "City" },
  ];

  return (
    <div className="mx-auto max-w-3xl p-6">
      <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">
              My Organization
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              Code: <span className="font-mono">{org.organization_code}</span>
            </p>
          </div>

          <span className="rounded-full bg-green-100 px-3 py-1 text-xs font-semibold text-green-700">
            {org.is_active ? "Active" : "Inactive"}
          </span>
        </div>

        <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-2">
          {fields.map(({ key, label }) => (
            <div key={key}>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                {label}
              </label>
              <input
                className="w-full rounded-lg border border-gray-300 p-2.5"
                value={(form[key] as string) ?? ""}
                onChange={(e) => setField(key, e.target.value)}
              />
            </div>
          ))}
        </div>
<div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Employee Count
            </label>
            <input
              type="number"
              min="0"
              className="w-full rounded-lg border border-gray-300 p-2.5"
              value={form.employee_count ?? ""}
              onChange={(e) => setNumericField("employee_count", e.target.value)}
            />
            <p className="mt-1 text-xs text-gray-400">
              Used for GHG intensity per employee in ESG reports.
            </p>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Annual Revenue (Rs)
            </label>
            <input
              type="number"
              min="0"
              step="0.01"
              className="w-full rounded-lg border border-gray-300 p-2.5"
              value={form.annual_revenue_inr ?? ""}
              onChange={(e) => setNumericField("annual_revenue_inr", e.target.value)}
            />
            <p className="mt-1 text-xs text-gray-400">
              Used for GHG intensity per Rs crore revenue in ESG reports.
            </p>
          </div>
        <button
          className="mt-6 rounded-lg bg-blue-600 px-6 py-2.5 font-semibold text-white disabled:opacity-50"
          onClick={() => mutation.mutate(form)}
          disabled={mutation.isPending}
        >
          {mutation.isPending ? "Saving..." : "Save Changes"}
        </button>
      </div>
    </div>
  );
}
