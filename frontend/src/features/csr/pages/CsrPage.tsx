import { useState } from "react";
import toast from "react-hot-toast";

import {
  useCsrRecords,
  useCreateCsrRecord,
  useUpdateCsrRecord,
  useDeleteCsrRecord,
  useCreateCsrProject,
  useUpdateCsrProject,
  useDeleteCsrProject,
} from "../hooks/useCsr";
import CsrRecordForm from "../components/CsrRecordForm";
import CsrProjectForm from "../components/CsrProjectForm";
import type { CsrRecord, CsrRecordCreate, CsrProject, CsrProjectCreate } from "../api/csrApi";
import ConfirmDialog from "../../../components/ui/ConfirmDialog";

export default function CsrPage() {
  const { data: records = [], isLoading, isError } = useCsrRecords();

  const createRecord = useCreateCsrRecord();
  const updateRecord = useUpdateCsrRecord();
  const deleteRecord = useDeleteCsrRecord();
  const createProject = useCreateCsrProject();
  const updateProject = useUpdateCsrProject();
  const deleteProject = useDeleteCsrProject();

  const [showRecordForm, setShowRecordForm] = useState(false);
  const [selectedRecord, setSelectedRecord] = useState<CsrRecord | null>(null);
  const [deleteRecordId, setDeleteRecordId] = useState<number | null>(null);

  const [projectFormFor, setProjectFormFor] = useState<number | null>(null);
  const [selectedProject, setSelectedProject] = useState<CsrProject | null>(null);
  const [deleteProjectId, setDeleteProjectId] = useState<number | null>(null);

  const [expandedId, setExpandedId] = useState<number | null>(null);

  async function saveRecord(data: CsrRecordCreate) {
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
      toast.error("Unable to save CSR record.");
    }
  }

  async function saveProject(data: CsrProjectCreate) {
    if (projectFormFor === null) return;
    try {
      if (selectedProject) {
        await updateProject.mutateAsync({ projectId: selectedProject.id, data });
      } else {
        await createProject.mutateAsync({ recordId: projectFormFor, data });
      }
      setProjectFormFor(null);
      setSelectedProject(null);
    } catch (error) {
      console.error(error);
      toast.error("Unable to save CSR project.");
    }
  }

  if (isLoading) {
    return <div className="p-10 text-center">Loading CSR records...</div>;
  }

  if (isError) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-red-600">
        Unable to load CSR records.
      </div>
    );
  }

  return (
    <div className="space-y-6 p-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">CSR (BRSR Principle 8)</h1>
          <p className="text-gray-500">
            Corporate Social Responsibility spend and projects, per reporting year.
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
          No CSR records yet.
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
                    Budget: ₹{Number(record.csr_budget_inr ?? 0).toLocaleString("en-IN")} ·
                    {" "}Spent: ₹{Number(record.csr_amount_spent_inr ?? 0).toLocaleString("en-IN")}
                    {record.percent_spent_vs_budget !== null &&
                      record.percent_spent_vs_budget !== undefined && (
                        <span className="ml-2 font-semibold text-blue-700">
                          ({record.percent_spent_vs_budget.toFixed(2)}%)
                        </span>
                      )}
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
                    <h3 className="font-medium text-gray-700">
                      Projects (Total: ₹
                      {Number(record.total_project_spend_inr ?? 0).toLocaleString("en-IN")})
                    </h3>
                    <button
                      onClick={() => {
                        setProjectFormFor(record.id);
                        setSelectedProject(null);
                      }}
                      className="rounded bg-green-600 px-3 py-1 text-sm text-white hover:bg-green-700"
                    >
                      + Add Project
                    </button>
                  </div>

                  {record.projects.length === 0 ? (
                    <p className="text-sm text-gray-400">No projects added yet.</p>
                  ) : (
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b text-left text-gray-500">
                          <th className="py-2">Project</th>
                          <th className="py-2">Category</th>
                          <th className="py-2">Location</th>
                          <th className="py-2">Amount</th>
                          <th className="py-2">Beneficiaries</th>
                          <th className="py-2 text-center">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {record.projects.map((p) => (
                          <tr key={p.id} className="border-b">
                            <td className="py-2 font-medium">{p.project_name}</td>
                            <td className="py-2">{p.activity_category ?? "-"}</td>
                            <td className="py-2">{p.location ?? "-"}</td>
                            <td className="py-2">
                              ₹{Number(p.amount_spent_inr ?? 0).toLocaleString("en-IN")}
                            </td>
                            <td className="py-2">{p.direct_beneficiaries_count ?? "-"}</td>
                            <td className="py-2 text-center">
                              <button
                                onClick={() => {
                                  setProjectFormFor(record.id);
                                  setSelectedProject(p);
                                }}
                                className="mr-2 text-amber-600 hover:underline"
                              >
                                Edit
                              </button>
                              <button
                                onClick={() => setDeleteProjectId(p.id)}
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
              <CsrRecordForm
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

      {projectFormFor !== null && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-6">
          <div className="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-xl bg-white shadow-2xl">
            <div className="p-6">
              <CsrProjectForm
                initialData={selectedProject ?? undefined}
                onSubmit={saveProject}
                loading={createProject.isPending || updateProject.isPending}
                onCancel={() => {
                  setProjectFormFor(null);
                  setSelectedProject(null);
                }}
              />
            </div>
          </div>
        </div>
      )}

      <ConfirmDialog
        open={deleteRecordId !== null}
        title="Delete CSR Record"
        message="Are you sure? This will also delete all projects under this record."
        loading={deleteRecord.isPending}
        onCancel={() => setDeleteRecordId(null)}
        onConfirm={async () => {
          if (deleteRecordId === null) return;
          await deleteRecord.mutateAsync(deleteRecordId);
          setDeleteRecordId(null);
        }}
      />

      <ConfirmDialog
        open={deleteProjectId !== null}
        title="Delete CSR Project"
        message="Are you sure you want to delete this project?"
        loading={deleteProject.isPending}
        onCancel={() => setDeleteProjectId(null)}
        onConfirm={async () => {
          if (deleteProjectId === null) return;
          await deleteProject.mutateAsync(deleteProjectId);
          setDeleteProjectId(null);
        }}
      />
    </div>
  );
}
