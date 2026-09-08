import { useState } from "react";

import {
  useHumanRightsRecords, useCreateHumanRightsRecord, useUpdateHumanRightsRecord, useDeleteHumanRightsRecord,
  useCreateHumanRightsChild, useUpdateHumanRightsChild, useDeleteHumanRightsChild,
} from "../hooks/useHumanRights";
import HumanRightsRecordForm from "../components/HumanRightsRecordForm";
import ChildRowForm, { CHILD_CONFIG } from "../components/ChildRowForm";
import type {
  ChildFields, ChildKind, ChildRow, HumanRightsRecord, HumanRightsRecordCreate, HumanRightsRecordUpdate,
} from "../api/humanRightsApi";
import ConfirmDialog from "../../../components/ui/ConfirmDialog";

const yesNo = (v: boolean | null | undefined) => (v === null || v === undefined ? "Not stated" : v ? "Yes" : "No");
const pct = (v: number | null | undefined) => (v === null || v === undefined ? "Not stated" : `${v}%`);
const num = (v: number | null | undefined) => (v === null || v === undefined ? "Not disclosed" : v.toLocaleString("en-IN"));

// Which array on the record holds each child kind.
const RELATION: Record<ChildKind, "workforce_coverage" | "remuneration" | "complaints"> = {
  workforce: "workforce_coverage", remuneration: "remuneration", complaint: "complaints",
};

interface ChildTableProps {
  kind: ChildKind;
  record: HumanRightsRecord;
  onAdd: () => void;
  onEdit: (row: ChildRow) => void;
  onDelete: (row: ChildRow) => void;
}

function ChildTable({ kind, record, onAdd, onEdit, onDelete }: ChildTableProps) {
  const cfg = CHILD_CONFIG[kind];
  const rows = record[RELATION[kind]] as ChildRow[];
  const full = rows.length >= Object.keys(cfg.labels).length;
  return (
    <div>
      <div className="mb-2 flex items-center justify-between">
        <h3 className="font-medium text-gray-700">{cfg.title}</h3>
        <button onClick={onAdd} disabled={full}
          className="rounded bg-green-600 px-3 py-1 text-sm text-white hover:bg-green-700 disabled:cursor-not-allowed disabled:opacity-50">
          + Add Row
        </button>
      </div>
      {rows.length === 0 ? (
        <p className="text-sm text-gray-400">No rows yet.</p>
      ) : (
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-left text-gray-500">
              <th className="py-2">Category</th>
              {cfg.fields.map((f) => <th key={f.name} className="py-2 text-right">{f.label}</th>)}
              {kind === "workforce" && <th className="py-2 text-right">Training coverage (B/A)</th>}
              <th className="py-2 text-center">Actions</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => {
              const rec = r as unknown as Record<string, number | null | undefined>;
              return (
                <tr key={r.id} className="border-b">
                  <td className="py-2 font-medium">{cfg.labels[r.category]}</td>
                  {cfg.fields.map((f) => <td key={f.name} className="py-2 text-right">{num(rec[f.name])}</td>)}
                  {kind === "workforce" && <td className="py-2 text-right">{pct(rec.hr_training_coverage_percent)}</td>}
                  <td className="py-2 text-center">
                    <button onClick={() => onEdit(r)} className="mr-2 text-amber-600 hover:underline">Edit</button>
                    <button onClick={() => onDelete(r)} className="text-red-600 hover:underline">Remove</button>
                  </td>
                </tr>
              );
            })}
            {kind === "complaint" && (
              <tr className="bg-gray-50 font-semibold">
                <td className="py-2">Total</td>
                <td className="py-2 text-right">{num(record.total_complaints_filed)}</td>
                <td className="py-2 text-right">{num(record.total_complaints_pending)}</td>
                <td />
              </tr>
            )}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default function HumanRightsPage() {
  const { data: records = [], isLoading, isError } = useHumanRightsRecords();
  const createRecord = useCreateHumanRightsRecord();
  const updateRecord = useUpdateHumanRightsRecord();
  const deleteRecord = useDeleteHumanRightsRecord();
  const createChild = useCreateHumanRightsChild();
  const updateChild = useUpdateHumanRightsChild();
  const deleteChild = useDeleteHumanRightsChild();

  const [showRecordForm, setShowRecordForm] = useState(false);
  const [selectedRecord, setSelectedRecord] = useState<HumanRightsRecord | null>(null);
  const [deleteRecordId, setDeleteRecordId] = useState<number | null>(null);
  const [expandedId, setExpandedId] = useState<number | null>(null);

  // Child modal state: which kind, for which record, editing which row.
  const [childForm, setChildForm] = useState<{ kind: ChildKind; record: HumanRightsRecord; row?: ChildRow } | null>(null);
  const [deleteChildTarget, setDeleteChildTarget] = useState<{ kind: ChildKind; id: number } | null>(null);

  async function saveRecord(data: HumanRightsRecordCreate | HumanRightsRecordUpdate) {
    try {
      if (selectedRecord) await updateRecord.mutateAsync({ id: selectedRecord.id, data });
      else await createRecord.mutateAsync(data as HumanRightsRecordCreate);
      setShowRecordForm(false);
      setSelectedRecord(null);
    } catch (error) { console.error(error); }
  }

  async function saveChild(data: ChildFields | Partial<ChildFields>) {
    if (!childForm) return;
    try {
      if (childForm.row) await updateChild.mutateAsync({ kind: childForm.kind, childId: childForm.row.id, data });
      else await createChild.mutateAsync({ kind: childForm.kind, recordId: childForm.record.id, data: data as ChildFields });
      setChildForm(null);
    } catch (error) { console.error(error); }
  }

  if (isLoading) return <div className="p-10 text-center">Loading Principle 5 records...</div>;
  if (isError) return <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-red-600">Unable to load Principle 5 records.</div>;

  return (
    <div className="space-y-6 p-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Human Rights (BRSR Principle 5)</h1>
          <p className="text-gray-500">Training, minimum wages, remuneration, complaints, assessments. One record per year.</p>
        </div>
        <button onClick={() => { setSelectedRecord(null); setShowRecordForm(true); }}
          className="rounded-lg bg-blue-600 px-5 py-2 font-medium text-white transition hover:bg-blue-700">
          + Add Year
        </button>
      </div>

      {records.length === 0 ? (
        <div className="rounded-lg border border-gray-200 bg-gray-50 p-6 text-center text-gray-500">No Principle 5 records yet.</div>
      ) : (
        <div className="space-y-4">
          {records.map((record) => (
            <div key={record.id} className="rounded-xl border bg-white shadow-sm">
              <div className="flex cursor-pointer items-center justify-between p-5"
                onClick={() => setExpandedId(expandedId === record.id ? null : record.id)}>
                <div>
                  <h2 className="text-lg font-semibold text-gray-800">{record.reporting_year}</h2>
                  <p className="text-sm text-gray-500">
                    Focal point: <span className="font-semibold">{yesNo(record.has_human_rights_focal_point)}</span>
                    {" · "}Complaints filed: <span className="font-semibold">{num(record.total_complaints_filed)}</span>
                    {" · "}{record.workforce_coverage.length}/4 workforce · {record.remuneration.length}/4 remuneration · {record.complaints.length}/6 complaint rows
                  </p>
                </div>
                <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
                  <button onClick={() => { setSelectedRecord(record); setShowRecordForm(true); }}
                    className="rounded bg-amber-500 px-3 py-1 text-sm text-white hover:bg-amber-600">Edit</button>
                  <button onClick={() => setDeleteRecordId(record.id)}
                    className="rounded bg-red-600 px-3 py-1 text-sm text-white hover:bg-red-700">Delete</button>
                </div>
              </div>

              {expandedId === record.id && (
                <div className="space-y-6 border-t px-5 py-4">
                  <dl className="grid grid-cols-1 gap-x-8 gap-y-2 text-sm md:grid-cols-2">
                    <div className="flex justify-between"><dt className="text-gray-500">HR requirements in contracts</dt><dd className="font-medium">{yesNo(record.hr_requirements_in_contracts)}</dd></div>
                    <div className="flex justify-between"><dt className="text-gray-500">Premises accessible to differently abled</dt><dd className="font-medium">{yesNo(record.premises_accessible_to_differently_abled)}</dd></div>
                    <div className="flex justify-between"><dt className="text-gray-500">Assessed -- child labour / forced labour</dt><dd className="font-medium">{pct(record.assessed_child_labour_percent)} / {pct(record.assessed_forced_labour_percent)}</dd></div>
                    <div className="flex justify-between"><dt className="text-gray-500">Assessed -- sexual harassment / discrimination</dt><dd className="font-medium">{pct(record.assessed_sexual_harassment_percent)} / {pct(record.assessed_discrimination_percent)}</dd></div>
                    <div className="flex justify-between"><dt className="text-gray-500">Assessed -- wages / other</dt><dd className="font-medium">{pct(record.assessed_wages_percent)} / {pct(record.assessed_other_percent)}</dd></div>
                    <div className="flex justify-between"><dt className="text-gray-500">Value chain partners assessed</dt><dd className="font-medium">{pct(record.value_chain_partners_assessed_percent)}</dd></div>
                  </dl>

                  {(["workforce", "remuneration", "complaint"] as ChildKind[]).map((kind) => (
                    <ChildTable key={kind} kind={kind} record={record}
                      onAdd={() => setChildForm({ kind, record })}
                      onEdit={(row) => setChildForm({ kind, record, row })}
                      onDelete={(row) => setDeleteChildTarget({ kind, id: row.id })} />
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {showRecordForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-6">
          <div className="max-h-[90vh] w-full max-w-4xl overflow-y-auto rounded-xl bg-white shadow-2xl">
            <div className="p-6">
              <HumanRightsRecordForm initialData={selectedRecord ?? undefined} onSubmit={saveRecord}
                loading={createRecord.isPending || updateRecord.isPending}
                onCancel={() => { setShowRecordForm(false); setSelectedRecord(null); }} />
            </div>
          </div>
        </div>
      )}

      {childForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-6">
          <div className="max-h-[90vh] w-full max-w-3xl overflow-y-auto rounded-xl bg-white shadow-2xl">
            <div className="p-6">
              <ChildRowForm kind={childForm.kind} initialData={childForm.row}
                usedCategories={(childForm.record[RELATION[childForm.kind]] as ChildRow[]).map((r) => r.category)}
                onSubmit={saveChild}
                loading={createChild.isPending || updateChild.isPending}
                onCancel={() => setChildForm(null)} />
            </div>
          </div>
        </div>
      )}

      <ConfirmDialog open={deleteRecordId !== null} title="Delete Principle 5 Record"
        message="Are you sure? This will also delete all workforce, remuneration and complaint rows under this year."
        loading={deleteRecord.isPending} onCancel={() => setDeleteRecordId(null)}
        onConfirm={async () => { if (deleteRecordId === null) return; await deleteRecord.mutateAsync(deleteRecordId); setDeleteRecordId(null); }} />

      <ConfirmDialog open={deleteChildTarget !== null} title="Delete Row" message="Are you sure you want to delete this row?"
        loading={deleteChild.isPending} onCancel={() => setDeleteChildTarget(null)}
        onConfirm={async () => { if (!deleteChildTarget) return; await deleteChild.mutateAsync({ kind: deleteChildTarget.kind, childId: deleteChildTarget.id }); setDeleteChildTarget(null); }} />
    </div>
  );
}
