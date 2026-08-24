import { useEffect } from "react";
import { useForm } from "react-hook-form";

import type { CsrRecord, CsrRecordCreate } from "../api/csrApi";

interface CsrRecordFormProps {
  initialData?: CsrRecord;
  onSubmit: (data: CsrRecordCreate) => void;
  onCancel?: () => void;
  loading?: boolean;
}

export default function CsrRecordForm({
  initialData,
  onSubmit,
  onCancel,
  loading = false,
}: CsrRecordFormProps) {
  const {
    register,
    handleSubmit,
    reset,
    watch,
    formState: { errors },
  } = useForm<CsrRecordCreate>();

  const budget = watch("csr_budget_inr");
  const spent = watch("csr_amount_spent_inr");

  const percentSpent =
    budget && spent ? (Number(spent) / Number(budget)) * 100 : null;

  useEffect(() => {
    if (initialData) {
      reset({
        reporting_year: initialData.reporting_year,
        csr_budget_inr: initialData.csr_budget_inr
          ? Number(initialData.csr_budget_inr)
          : undefined,
        csr_amount_spent_inr: initialData.csr_amount_spent_inr
          ? Number(initialData.csr_amount_spent_inr)
          : undefined,
        csr_admin_overhead_inr: initialData.csr_admin_overhead_inr
          ? Number(initialData.csr_admin_overhead_inr)
          : undefined,
        remarks: initialData.remarks ?? "",
      });
    } else {
      reset({
        reporting_year: new Date().getFullYear(),
        csr_budget_inr: undefined,
        csr_amount_spent_inr: undefined,
        csr_admin_overhead_inr: undefined,
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
          {initialData ? "Edit CSR Record" : "Add CSR Record"}
        </h2>
        <p className="mt-1 text-sm text-gray-500">
          BRSR Principle 8 -- CSR budget and actual spend for the reporting year.
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
            CSR Budget (₹) [2% mandate]
          </label>
          <input
            type="number"
            step="any"
            {...register("csr_budget_inr", { valueAsNumber: true, min: 0 })}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            CSR Amount Spent (₹)
          </label>
          <input
            type="number"
            step="any"
            {...register("csr_amount_spent_inr", { valueAsNumber: true, min: 0 })}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Admin Overhead (₹) [max 5% of spend]
          </label>
          <input
            type="number"
            step="any"
            {...register("csr_admin_overhead_inr", { valueAsNumber: true, min: 0 })}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
          />
        </div>
      </div>

      {percentSpent !== null && (
        <div className="rounded-lg bg-blue-50 px-4 py-3 text-sm text-blue-800">
          Spent vs Budget:{" "}
          <span className="font-semibold">{percentSpent.toFixed(2)}%</span>
        </div>
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
