import { useEffect } from "react";
import { useForm } from "react-hook-form";

import type { EthicsRecord, EthicsRecordCreate } from "../api/ethicsApi";

interface EthicsRecordFormProps {
  initialData?: EthicsRecord;
  onSubmit: (data: EthicsRecordCreate) => void;
  onCancel?: () => void;
  loading?: boolean;
}

export default function EthicsRecordForm({
  initialData,
  onSubmit,
  onCancel,
  loading = false,
}: EthicsRecordFormProps) {
  const {
    register,
    handleSubmit,
    reset,
    watch,
    formState: { errors },
  } = useForm<EthicsRecordCreate>();

  const boardTotal = watch("board_kmp_total_count");
  const boardTrained = watch("board_kmp_trained_count");
  const empTotal = watch("employees_total_count");
  const empTrained = watch("employees_trained_count");
  const workerTotal = watch("workers_total_count");
  const workerTrained = watch("workers_trained_count");

  const pct = (trained?: number, total?: number) =>
    trained !== undefined && total ? ((trained / total) * 100).toFixed(1) : null;

  useEffect(() => {
    if (initialData) {
      reset({
        reporting_year: initialData.reporting_year,
        board_kmp_total_count: initialData.board_kmp_total_count,
        board_kmp_trained_count: initialData.board_kmp_trained_count,
        employees_total_count: initialData.employees_total_count,
        employees_trained_count: initialData.employees_trained_count,
        workers_total_count: initialData.workers_total_count,
        workers_trained_count: initialData.workers_trained_count,
        disciplinary_actions_directors: initialData.disciplinary_actions_directors,
        disciplinary_actions_kmp: initialData.disciplinary_actions_kmp,
        disciplinary_actions_employees: initialData.disciplinary_actions_employees,
        disciplinary_actions_workers: initialData.disciplinary_actions_workers,
        fines_penalties_amount_inr: initialData.fines_penalties_amount_inr
          ? Number(initialData.fines_penalties_amount_inr)
          : undefined,
        has_conflict_of_interest_process: initialData.has_conflict_of_interest_process ?? "",
        conflict_of_interest_disclosures_count: initialData.conflict_of_interest_disclosures_count,
        corruption_complaints_received: initialData.corruption_complaints_received,
        corruption_complaints_pending: initialData.corruption_complaints_pending,
        remarks: initialData.remarks ?? "",
      });
    } else {
      reset({ reporting_year: new Date().getFullYear() });
    }
  }, [initialData, reset]);

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="space-y-8 rounded-xl border border-gray-200 bg-white p-6 shadow-sm"
    >
      <div>
        <h2 className="text-xl font-semibold text-gray-800">
          {initialData ? "Edit Ethics Record" : "Add Ethics Record"}
        </h2>
        <p className="mt-1 text-sm text-gray-500">
          BRSR Principle 1 -- anti-corruption training, disciplinary actions, conflict of interest.
        </p>
      </div>

      <div>
        <label className="mb-1 block text-sm font-medium text-gray-700">Reporting Year *</label>
        <input
          type="number"
          {...register("reporting_year", { required: "Required", valueAsNumber: true })}
          className="w-full max-w-xs rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
        />
        {errors.reporting_year && (
          <p className="mt-1 text-sm text-red-600">{errors.reporting_year.message}</p>
        )}
      </div>

      <section className="space-y-4">
        <h3 className="border-b pb-2 text-lg font-semibold text-gray-700">
          Anti-Corruption Training Coverage
        </h3>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Board/KMP Total
            </label>
            <input
              type="number"
              {...register("board_kmp_total_count", { valueAsNumber: true, min: 0 })}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Board/KMP Trained
            </label>
            <input
              type="number"
              {...register("board_kmp_trained_count", { valueAsNumber: true, min: 0 })}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            />
          </div>
          <div className="flex items-end pb-2 text-sm text-blue-700">
            {pct(boardTrained, boardTotal) && <span>{pct(boardTrained, boardTotal)}% trained</span>}
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Employees Total
            </label>
            <input
              type="number"
              {...register("employees_total_count", { valueAsNumber: true, min: 0 })}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Employees Trained
            </label>
            <input
              type="number"
              {...register("employees_trained_count", { valueAsNumber: true, min: 0 })}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            />
          </div>
          <div className="flex items-end pb-2 text-sm text-blue-700">
            {pct(empTrained, empTotal) && <span>{pct(empTrained, empTotal)}% trained</span>}
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Workers Total
            </label>
            <input
              type="number"
              {...register("workers_total_count", { valueAsNumber: true, min: 0 })}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Workers Trained
            </label>
            <input
              type="number"
              {...register("workers_trained_count", { valueAsNumber: true, min: 0 })}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            />
          </div>
          <div className="flex items-end pb-2 text-sm text-blue-700">
            {pct(workerTrained, workerTotal) && <span>{pct(workerTrained, workerTotal)}% trained</span>}
          </div>
        </div>
      </section>

      <section className="space-y-4">
        <h3 className="border-b pb-2 text-lg font-semibold text-gray-700">
          Disciplinary Actions &amp; Fines
        </h3>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Directors</label>
            <input
              type="number"
              {...register("disciplinary_actions_directors", { valueAsNumber: true, min: 0 })}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">KMP</label>
            <input
              type="number"
              {...register("disciplinary_actions_kmp", { valueAsNumber: true, min: 0 })}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Employees</label>
            <input
              type="number"
              {...register("disciplinary_actions_employees", { valueAsNumber: true, min: 0 })}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Workers</label>
            <input
              type="number"
              {...register("disciplinary_actions_workers", { valueAsNumber: true, min: 0 })}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            />
          </div>
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Fines/Penalties Amount (₹)
          </label>
          <input
            type="number"
            step="any"
            {...register("fines_penalties_amount_inr", { valueAsNumber: true, min: 0 })}
            className="w-full max-w-xs rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
          />
        </div>
      </section>

      <section className="space-y-4">
        <h3 className="border-b pb-2 text-lg font-semibold text-gray-700">
          Conflict of Interest &amp; Complaints
        </h3>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Conflict-of-Interest Process Defined?
            </label>
            <select
              {...register("has_conflict_of_interest_process")}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            >
              <option value="">Select...</option>
              <option value="yes">Yes</option>
              <option value="no">No</option>
            </select>
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Conflict Disclosures This Year
            </label>
            <input
              type="number"
              {...register("conflict_of_interest_disclosures_count", { valueAsNumber: true, min: 0 })}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Corruption Complaints Received
            </label>
            <input
              type="number"
              {...register("corruption_complaints_received", { valueAsNumber: true, min: 0 })}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Corruption Complaints Pending
            </label>
            <input
              type="number"
              {...register("corruption_complaints_pending", { valueAsNumber: true, min: 0 })}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            />
          </div>
        </div>
      </section>

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
