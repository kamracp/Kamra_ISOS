import { useEffect } from "react";
import { useForm } from "react-hook-form";

import type { StakeholderGroup, StakeholderGroupCreate } from "../api/stakeholderEngagementApi";

interface StakeholderGroupFormProps {
  initialData?: StakeholderGroup;
  onSubmit: (data: StakeholderGroupCreate) => void;
  onCancel?: () => void;
  loading?: boolean;
}

export default function StakeholderGroupForm({
  initialData,
  onSubmit,
  onCancel,
  loading = false,
}: StakeholderGroupFormProps) {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<StakeholderGroupCreate>();

  useEffect(() => {
    if (initialData) {
      reset({
        group_name: initialData.group_name,
        is_vulnerable_marginalized: initialData.is_vulnerable_marginalized,
        communication_channels: initialData.communication_channels ?? "",
        frequency_of_engagement: initialData.frequency_of_engagement ?? "",
        purpose_and_scope: initialData.purpose_and_scope ?? "",
        remarks: initialData.remarks ?? "",
      });
    } else {
      reset({
        group_name: "",
        is_vulnerable_marginalized: undefined,
        communication_channels: "",
        frequency_of_engagement: "",
        purpose_and_scope: "",
        remarks: "",
      });
    }
  }, [initialData, reset]);

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="space-y-6 rounded-xl border border-gray-200 bg-white p-6 shadow-sm"
    >
      <div>
        <h2 className="text-xl font-semibold text-gray-800">
          {initialData ? "Edit Stakeholder Group" : "Add Stakeholder Group"}
        </h2>
        <p className="mt-1 text-sm text-gray-500">
          Stakeholder group identified within this reporting year.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Group Name *
          </label>
          <input
            type="text"
            placeholder="e.g. Employees, Investors, Local Community"
            {...register("group_name", { required: "Required" })}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
          />
          {errors.group_name && (
            <p className="mt-1 text-sm text-red-600">{errors.group_name.message}</p>
          )}
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Vulnerable/Marginalized?
          </label>
          <select
            {...register("is_vulnerable_marginalized", {
              setValueAs: (v) => (v === "" ? undefined : v === "true"),
            })}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
          >
            <option value="">Not stated</option>
            <option value="false">No</option>
            <option value="true">Yes</option>
          </select>
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Frequency of Engagement
          </label>
          <select
            {...register("frequency_of_engagement")}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
          >
            <option value="">Select...</option>
            <option value="Annually">Annually</option>
            <option value="Half-yearly">Half-yearly</option>
            <option value="Quarterly">Quarterly</option>
            <option value="Others">Others</option>
          </select>
        </div>
      </div>

      <div>
        <label className="mb-1 block text-sm font-medium text-gray-700">
          Communication Channels
        </label>
        <textarea
          placeholder="e.g. Sustainability report, website, meetings, notice board"
          {...register("communication_channels")}
          rows={2}
          className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
        />
      </div>

      <div>
        <label className="mb-1 block text-sm font-medium text-gray-700">
          Purpose and Scope of Engagement
        </label>
        <textarea
          {...register("purpose_and_scope")}
          rows={2}
          className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
        />
      </div>

      <div>
        <label className="mb-1 block text-sm font-medium text-gray-700">Remarks</label>
        <textarea
          {...register("remarks")}
          rows={2}
          className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
        />
      </div>

      <div className="flex justify-end gap-3 border-t border-gray-200 pt-6">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            disabled={loading}
            className="rounded-lg border border-gray-300 px-5 py-2 font-medium text-gray-700 transition hover:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Cancel
          </button>
        )}
        <button
          type="submit"
          disabled={loading}
          className="rounded-lg bg-blue-600 px-5 py-2 font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? "Saving..." : initialData ? "Update Group" : "Add Group"}
        </button>
      </div>
    </form>
  );
}
