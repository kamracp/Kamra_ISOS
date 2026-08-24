import { useState } from "react";
import toast from "react-hot-toast";

import {
  useEthicsRecords,
  useCreateEthicsRecord,
  useUpdateEthicsRecord,
  useDeleteEthicsRecord,
} from "../hooks/useEthics";
import EthicsRecordForm from "../components/EthicsRecordForm";
import type { EthicsRecord, EthicsRecordCreate } from "../api/ethicsApi";
import ConfirmDialog from "../../../components/ui/ConfirmDialog";

export default function EthicsPage() {
  const { data: records = [], isLoading, isError } = useEthicsRecords();
  const createRecord = useCreateEthicsRecord();
  const updateRecord = useUpdateEthicsRecord();
  const deleteRecord = useDeleteEthicsRecord();

  const [showForm, setShowForm] = useState(false);
  const [selectedRecord, setSelectedRecord] = useState<EthicsRecord | null>(null);
  const [deleteId, setDeleteId] = useState<number | null>(null);

  async function saveRecord(data: EthicsRecordCreate) {
    try {
      if (selectedRecord) {
        await updateRecord.mutateAsync({ id: selectedRecord.id, data });
      } else {
        await createRecord.mutateAsync(data);
      }
      setShowForm(false);
      setSelectedRecord(null);
    } catch (error) {
      console.error(error);
      toast.error("Unable to save ethics record.");
    }
  }

  if (isLoading) {
    return <div className="p-10 text-center">Loading ethics records...</div>;
  }

  if (isError) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-red-600">
        Unable to load ethics records.
      </div>
    );
  }

  return (
    <div className="space-y-6 p-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Ethics (BRSR Principle 1)</h1>
          <p className="text-gray-500">
            Anti-corruption training, disciplinary actions, conflict of interest, per reporting year.
          </p>
        </div>
        <button
          onClick={() => {
            setSelectedRecord(null);
            setShowForm(true);
          }}
          className="rounded-lg bg-blue-600 px-5 py-2 font-medium text-white transition hover:bg-blue-700"
        >
          + Add Year
        </button>
      </div>

      {records.length === 0 ? (
        <div className="rounded-lg border border-gray-200 bg-gray-50 p-6 text-center text-gray-500">
          No ethics records yet.
        </div>
      ) : (
        <div className="overflow-hidden rounded-xl border bg-white shadow">
          <table className="min-w-full">
            <thead className="bg-gray-100">
              <tr>
                <th className="border-b px-4 py-3 text-left">Year</th>
                <th className="border-b px-4 py-3 text-left">Board/KMP Trained</th>
                <th className="border-b px-4 py-3 text-left">Employees Trained</th>
                <th className="border-b px-4 py-3 text-left">Workers Trained</th>
                <th className="border-b px-4 py-3 text-left">Complaints (Recv/Pending)</th>
                <th className="border-b px-4 py-3 text-center">Actions</th>
              </tr>
            </thead>
            <tbody>
              {records.map((r) => (
                <tr key={r.id} className="hover:bg-gray-50">
                  <td className="border-b px-4 py-3 font-medium">{r.reporting_year}</td>
                  <td className="border-b px-4 py-3">
                    {r.board_kmp_trained_percent !== undefined && r.board_kmp_trained_percent !== null
                      ? `${r.board_kmp_trained_percent}%`
                      : "-"}
                  </td>
                  <td className="border-b px-4 py-3">
                    {r.employees_trained_percent !== undefined && r.employees_trained_percent !== null
                      ? `${r.employees_trained_percent}%`
                      : "-"}
                  </td>
                  <td className="border-b px-4 py-3">
                    {r.workers_trained_percent !== undefined && r.workers_trained_percent !== null
                      ? `${r.workers_trained_percent}%`
                      : "-"}
                  </td>
                  <td className="border-b px-4 py-3">
                    {r.corruption_complaints_received ?? "-"} / {r.corruption_complaints_pending ?? "-"}
                  </td>
                  <td className="border-b px-4 py-3 text-center">
                    <button
                      onClick={() => {
                        setSelectedRecord(r);
                        setShowForm(true);
                      }}
                      className="mr-2 rounded bg-amber-500 px-3 py-1 text-white hover:bg-amber-600"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => setDeleteId(r.id)}
                      className="rounded bg-red-600 px-3 py-1 text-white hover:bg-red-700"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-6">
          <div className="max-h-[90vh] w-full max-w-3xl overflow-y-auto rounded-xl bg-white shadow-2xl">
            <div className="p-6">
              <EthicsRecordForm
                initialData={selectedRecord ?? undefined}
                onSubmit={saveRecord}
                loading={createRecord.isPending || updateRecord.isPending}
                onCancel={() => {
                  setShowForm(false);
                  setSelectedRecord(null);
                }}
              />
            </div>
          </div>
        </div>
      )}

      <ConfirmDialog
        open={deleteId !== null}
        title="Delete Ethics Record"
        message="Are you sure you want to delete this record?"
        loading={deleteRecord.isPending}
        onCancel={() => setDeleteId(null)}
        onConfirm={async () => {
          if (deleteId === null) return;
          await deleteRecord.mutateAsync(deleteId);
          setDeleteId(null);
        }}
      />
    </div>
  );
}
