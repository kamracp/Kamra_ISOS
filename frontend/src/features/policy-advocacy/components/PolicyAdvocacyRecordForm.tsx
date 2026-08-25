import { useEffect } from "react";
import { useForm } from "react-hook-form";

import type { PolicyAdvocacyRecord, PolicyAdvocacyRecordCreate } from "../api/policyAdvocacyApi";

interface PolicyAdvocacyRecordFormProps {
  initialData?: PolicyAdvocacyRecord;
  onSubmit: (data: PolicyAdvocacyRecordCreate) => void;
  onCancel?: () => void;
  loading?: boolean;
}

export default function PolicyAdvocacyRecordForm({
  initialData,
  onSubmit,
  onCancel,
  loading = false,
}: PolicyAdvocacyRecordFormProps) {
  const {
    register,
    handleSubmit,
    reset,
    watch,
    formState: { errors },
  } = useForm<PolicyAdvocacyRecordCreate>();

  const hasIssue = watch("has_anti_competitive_conduct_issue");

  useEffect(() => {
    if (initialData) {
      reset({
        reporting_year: initialData.reporting_year,
        has_anti_competitive_conduct_issue: initialData.has_anti_competitive_conduct_issue,
        anti_competitive_conduct_details: initialData.anti_competitive_conduct_details ?? "",
        corrective_action_taken: initialData.corrective_action_taken ?? "",
        remarks: initialData.remarks ?? "",
      });
    } else {
      reset({
        reporting_year: new Date().getFullYear(),
        has_anti_competitive_conduct_issue: undefined,
        anti_competitive_conduct_details: "",
        corrective_action_taken: "",
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
          {initialData ? "Edit Policy Advocacy Record" : "Add Policy Advocacy Record"}
        </h2>
        <p className="mt-1 text-sm text-gray-500">
          BRSR Principle 7 -- trade association memberships and anti-competitive conduct.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Reporting Year *
          </label>
          <input
            type="number"
            {...register("reporting_year", {
              required: "Required",
              valueAsNumber: true,
              min: { value: 2000, message: "Must be 2000 or later" },
            })}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
          />
          {errors.reporting_year && (
            <p className="mt-1 text-sm text-red-600">{errors.reporting_year.message}</p>
          )}
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Anti-Competitive Conduct Issue?
          </label>
          <select
            {...register("has_anti_competitive_conduct_issue", {
              setValueAs: (v) => (v === "" ? undefined : v === "true"),
            })}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
          >
            <option value="">Not stated</option>
            <option value="false">No</option>
            <option value="true">Yes</option>
          </select>
        </div>
      </div>

      {hasIssue && (
        <>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Anti-Competitive Conduct Details
            </label>
            <textarea
              {...register("anti_competitive_conduct_details")}
              rows={3}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Corrective Action Taken
            </label>
            <textarea
              {...register("corrective_action_taken")}
              rows={3}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            />
          </div>
        </>
      )}

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
          {loading ? "Saving..." : initialData ? "Update Record" : "Add Record"}
        </button>
      </div>
    </form>
  );
}
