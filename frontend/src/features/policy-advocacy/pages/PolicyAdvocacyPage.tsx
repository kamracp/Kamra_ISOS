import { useState } from "react";
import toast from "react-hot-toast";

import {
  usePolicyAdvocacyRecords,
  useCreatePolicyAdvocacyRecord,
  useUpdatePolicyAdvocacyRecord,
  useDeletePolicyAdvocacyRecord,
  useCreateTradeAssociation,
  useUpdateTradeAssociation,
  useDeleteTradeAssociation,
} from "../hooks/usePolicyAdvocacy";
import PolicyAdvocacyRecordForm from "../components/PolicyAdvocacyRecordForm";
import TradeAssociationForm from "../components/TradeAssociationForm";
import type {
  PolicyAdvocacyRecord,
  PolicyAdvocacyRecordCreate,
  TradeAssociation,
  TradeAssociationCreate,
} from "../api/policyAdvocacyApi";
import ConfirmDialog from "../../../components/ui/ConfirmDialog";

export default function PolicyAdvocacyPage() {
  const { data: records = [], isLoading, isError } = usePolicyAdvocacyRecords();

  const createRecord = useCreatePolicyAdvocacyRecord();
  const updateRecord = useUpdatePolicyAdvocacyRecord();
  const deleteRecord = useDeletePolicyAdvocacyRecord();
  const createAssociation = useCreateTradeAssociation();
  const updateAssociation = useUpdateTradeAssociation();
  const deleteAssociation = useDeleteTradeAssociation();

  const [showRecordForm, setShowRecordForm] = useState(false);
  const [selectedRecord, setSelectedRecord] = useState<PolicyAdvocacyRecord | null>(null);
  const [deleteRecordId, setDeleteRecordId] = useState<number | null>(null);

  const [associationFormFor, setAssociationFormFor] = useState<number | null>(null);
  const [selectedAssociation, setSelectedAssociation] = useState<TradeAssociation | null>(null);
  const [deleteAssociationId, setDeleteAssociationId] = useState<number | null>(null);

  const [expandedId, setExpandedId] = useState<number | null>(null);

  async function saveRecord(data: PolicyAdvocacyRecordCreate) {
    try {
      if (selectedRecord) {
        await updateRecord.mutateAsync({ id: selectedRecord.id, data });
      } else {
        await createRecord.mutateAsync(data);
      }
      setShowRecordForm(false);
      setSelectedRecord(null);
    } catch (error) {
      console.error(error);
      toast.error("Unable to save policy advocacy record.");
    }
  }

  async function saveAssociation(data: TradeAssociationCreate) {
    if (associationFormFor === null) return;
    try {
      if (selectedAssociation) {
        await updateAssociation.mutateAsync({ associationId: selectedAssociation.id, data });
      } else {
        await createAssociation.mutateAsync({ recordId: associationFormFor, data });
      }
      setAssociationFormFor(null);
      setSelectedAssociation(null);
    } catch (error) {
      console.error(error);
      toast.error("Unable to save trade association.");
    }
  }

  if (isLoading) {
    return <div className="p-10 text-center">Loading policy advocacy records...</div>;
  }

  if (isError) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-red-600">
        Unable to load policy advocacy records.
      </div>
    );
  }

  return (
    <div className="space-y-6 p-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Policy Advocacy (BRSR Principle 7)</h1>
          <p className="text-gray-500">
            Trade association memberships and anti-competitive conduct, per reporting year.
          </p>
        </div>
        <button
          onClick={() => {
            setSelectedRecord(null);
            setShowRecordForm(true);
          }}
          className="rounded-lg bg-blue-600 px-5 py-2 font-medium text-white transition hover:bg-blue-700"
        >
          + Add Year
        </button>
      </div>

      {records.length === 0 ? (
        <div className="rounded-lg border border-gray-200 bg-gray-50 p-6 text-center text-gray-500">
          No policy advocacy records yet.
        </div>
      ) : (
        <div className="space-y-4">
          {records.map((record) => (
            <div key={record.id} className="rounded-xl border bg-white shadow-sm">
              <div
                className="flex cursor-pointer items-center justify-between p-5"
                onClick={() =>
                  setExpandedId(expandedId === record.id ? null : record.id)
                }
              >
                <div>
                  <h2 className="text-lg font-semibold text-gray-800">
                    {record.reporting_year}
                  </h2>
                  <p className="text-sm text-gray-500">
                    Anti-competitive conduct issue:{" "}
                    <span className="font-semibold">
                      {record.has_anti_competitive_conduct_issue === undefined ||
                      record.has_anti_competitive_conduct_issue === null
                        ? "Not stated"
                        : record.has_anti_competitive_conduct_issue
                        ? "Yes"
                        : "No"}
                    </span>
                    {" · "}
                    {record.associations.length} association(s)
                  </p>
                </div>
                <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
                  <button
                    onClick={() => {
                      setSelectedRecord(record);
                      setShowRecordForm(true);
                    }}
                    className="rounded bg-amber-500 px-3 py-1 text-sm text-white hover:bg-amber-600"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => setDeleteRecordId(record.id)}
                    className="rounded bg-red-600 px-3 py-1 text-sm text-white hover:bg-red-700"
                  >
                    Delete
                  </button>
                </div>
              </div>

              {expandedId === record.id && (
                <div className="border-t px-5 py-4">
                  <div className="mb-3 flex items-center justify-between">
                    <h3 className="font-medium text-gray-700">Trade Associations</h3>
                    <button
                      onClick={() => {
                        setAssociationFormFor(record.id);
                        setSelectedAssociation(null);
                      }}
                      className="rounded bg-green-600 px-3 py-1 text-sm text-white hover:bg-green-700"
                    >
                      + Add Association
                    </button>
                  </div>

                  {record.associations.length === 0 ? (
                    <p className="text-sm text-gray-400">No associations added yet.</p>
                  ) : (
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b text-left text-gray-500">
                          <th className="py-2">Association</th>
                          <th className="py-2">Reach</th>
                          <th className="py-2 text-center">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {record.associations.map((a) => (
                          <tr key={a.id} className="border-b">
                            <td className="py-2 font-medium">{a.association_name}</td>
                            <td className="py-2">{a.reach ?? "-"}</td>
                            <td className="py-2 text-center">
                              <button
                                onClick={() => {
                                  setAssociationFormFor(record.id);
                                  setSelectedAssociation(a);
                                }}
                                className="mr-2 text-amber-600 hover:underline"
                              >
                                Edit
                              </button>
                              <button
                                onClick={() => setDeleteAssociationId(a.id)}
                                className="text-red-600 hover:underline"
                              >
                                Remove
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {showRecordForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-6">
          <div className="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-xl bg-white shadow-2xl">
            <div className="p-6">
              <PolicyAdvocacyRecordForm
                initialData={selectedRecord ?? undefined}
                onSubmit={saveRecord}
                loading={createRecord.isPending || updateRecord.isPending}
                onCancel={() => {
                  setShowRecordForm(false);
                  setSelectedRecord(null);
                }}
              />
            </div>
          </div>
        </div>
      )}

      {associationFormFor !== null && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-6">
          <div className="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-xl bg-white shadow-2xl">
            <div className="p-6">
              <TradeAssociationForm
                initialData={selectedAssociation ?? undefined}
                onSubmit={saveAssociation}
                loading={createAssociation.isPending || updateAssociation.isPending}
                onCancel={() => {
                  setAssociationFormFor(null);
                  setSelectedAssociation(null);
                }}
              />
            </div>
          </div>
        </div>
      )}

      <ConfirmDialog
        open={deleteRecordId !== null}
        title="Delete Policy Advocacy Record"
        message="Are you sure? This will also delete all trade associations under this record."
        loading={deleteRecord.isPending}
        onCancel={() => setDeleteRecordId(null)}
        onConfirm={async () => {
          if (deleteRecordId === null) return;
          await deleteRecord.mutateAsync(deleteRecordId);
          setDeleteRecordId(null);
        }}
      />

      <ConfirmDialog
        open={deleteAssociationId !== null}
        title="Delete Trade Association"
        message="Are you sure you want to delete this association?"
        loading={deleteAssociation.isPending}
        onCancel={() => setDeleteAssociationId(null)}
        onConfirm={async () => {
          if (deleteAssociationId === null) return;
          await deleteAssociation.mutateAsync(deleteAssociationId);
          setDeleteAssociationId(null);
        }}
      />
    </div>
  );
}
