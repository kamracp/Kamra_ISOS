import { useState } from "react";
import toast from "react-hot-toast";

import {
  useStakeholderEngagementRecords,
  useCreateStakeholderEngagementRecord,
  useUpdateStakeholderEngagementRecord,
  useDeleteStakeholderEngagementRecord,
  useCreateStakeholderGroup,
  useUpdateStakeholderGroup,
  useDeleteStakeholderGroup,
} from "../hooks/useStakeholderEngagement";
import StakeholderEngagementRecordForm from "../components/StakeholderEngagementRecordForm";
import StakeholderGroupForm from "../components/StakeholderGroupForm";
import type {
  StakeholderEngagementRecord,
  StakeholderEngagementRecordCreate,
  StakeholderGroup,
  StakeholderGroupCreate,
} from "../api/stakeholderEngagementApi";
import ConfirmDialog from "../../../components/ui/ConfirmDialog";

export default function StakeholderEngagementPage() {
  const { data: records = [], isLoading, isError } = useStakeholderEngagementRecords();

  const createRecord = useCreateStakeholderEngagementRecord();
  const updateRecord = useUpdateStakeholderEngagementRecord();
  const deleteRecord = useDeleteStakeholderEngagementRecord();
  const createGroup = useCreateStakeholderGroup();
  const updateGroup = useUpdateStakeholderGroup();
  const deleteGroup = useDeleteStakeholderGroup();

  const [showRecordForm, setShowRecordForm] = useState(false);
  const [selectedRecord, setSelectedRecord] = useState<StakeholderEngagementRecord | null>(null);
  const [deleteRecordId, setDeleteRecordId] = useState<number | null>(null);

  const [groupFormFor, setGroupFormFor] = useState<number | null>(null);
  const [selectedGroup, setSelectedGroup] = useState<StakeholderGroup | null>(null);
  const [deleteGroupId, setDeleteGroupId] = useState<number | null>(null);

  const [expandedId, setExpandedId] = useState<number | null>(null);

  async function saveRecord(data: StakeholderEngagementRecordCreate) {
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
      toast.error("Unable to save stakeholder engagement record.");
    }
  }

  async function saveGroup(data: StakeholderGroupCreate) {
    if (groupFormFor === null) return;
    try {
      if (selectedGroup) {
        await updateGroup.mutateAsync({ groupId: selectedGroup.id, data });
      } else {
        await createGroup.mutateAsync({ recordId: groupFormFor, data });
      }
      setGroupFormFor(null);
      setSelectedGroup(null);
    } catch (error) {
      console.error(error);
      toast.error("Unable to save stakeholder group.");
    }
  }

  if (isLoading) {
    return <div className="p-10 text-center">Loading stakeholder engagement records...</div>;
  }

  if (isError) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-red-600">
        Unable to load stakeholder engagement records.
      </div>
    );
  }

  return (
    <div className="space-y-6 p-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Stakeholder Engagement (BRSR Principle 4)</h1>
          <p className="text-gray-500">
            Stakeholder groups and consultation process, per reporting year.
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
          No stakeholder engagement records yet.
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
                    Consultation conducted:{" "}
                    <span className="font-semibold">
                      {record.has_consultation_process === undefined ||
                      record.has_consultation_process === null
                        ? "Not stated"
                        : record.has_consultation_process
                        ? "Yes"
                        : "No"}
                    </span>
                    {" · "}
                    {record.stakeholder_groups.length} group(s)
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
                    <h3 className="font-medium text-gray-700">Stakeholder Groups</h3>
                    <button
                      onClick={() => {
                        setGroupFormFor(record.id);
                        setSelectedGroup(null);
                      }}
                      className="rounded bg-green-600 px-3 py-1 text-sm text-white hover:bg-green-700"
                    >
                      + Add Group
                    </button>
                  </div>

                  {record.stakeholder_groups.length === 0 ? (
                    <p className="text-sm text-gray-400">No stakeholder groups added yet.</p>
                  ) : (
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b text-left text-gray-500">
                          <th className="py-2">Group</th>
                          <th className="py-2">Vulnerable?</th>
                          <th className="py-2">Frequency</th>
                          <th className="py-2 text-center">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {record.stakeholder_groups.map((g) => (
                          <tr key={g.id} className="border-b">
                            <td className="py-2 font-medium">{g.group_name}</td>
                            <td className="py-2">
                              {g.is_vulnerable_marginalized === undefined ||
                              g.is_vulnerable_marginalized === null
                                ? "-"
                                : g.is_vulnerable_marginalized
                                ? "Yes"
                                : "No"}
                            </td>
                            <td className="py-2">{g.frequency_of_engagement ?? "-"}</td>
                            <td className="py-2 text-center">
                              <button
                                onClick={() => {
                                  setGroupFormFor(record.id);
                                  setSelectedGroup(g);
                                }}
                                className="mr-2 text-amber-600 hover:underline"
                              >
                                Edit
                              </button>
                              <button
                                onClick={() => setDeleteGroupId(g.id)}
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
              <StakeholderEngagementRecordForm
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

      {groupFormFor !== null && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-6">
          <div className="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-xl bg-white shadow-2xl">
            <div className="p-6">
              <StakeholderGroupForm
                initialData={selectedGroup ?? undefined}
                onSubmit={saveGroup}
                loading={createGroup.isPending || updateGroup.isPending}
                onCancel={() => {
                  setGroupFormFor(null);
                  setSelectedGroup(null);
                }}
              />
            </div>
          </div>
        </div>
      )}

      <ConfirmDialog
        open={deleteRecordId !== null}
        title="Delete Stakeholder Engagement Record"
        message="Are you sure? This will also delete all stakeholder groups under this record."
        loading={deleteRecord.isPending}
        onCancel={() => setDeleteRecordId(null)}
        onConfirm={async () => {
          if (deleteRecordId === null) return;
          await deleteRecord.mutateAsync(deleteRecordId);
          setDeleteRecordId(null);
        }}
      />

      <ConfirmDialog
        open={deleteGroupId !== null}
        title="Delete Stakeholder Group"
        message="Are you sure you want to delete this group?"
        loading={deleteGroup.isPending}
        onCancel={() => setDeleteGroupId(null)}
        onConfirm={async () => {
          if (deleteGroupId === null) return;
          await deleteGroup.mutateAsync(deleteGroupId);
          setDeleteGroupId(null);
        }}
      />
    </div>
  );
}
