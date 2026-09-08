import { useState } from "react";
import {
  useEmployeeWellbeingRecords, useCreateEmployeeWellbeingRecord, useUpdateEmployeeWellbeingRecord, useDeleteEmployeeWellbeingRecord,
  useCreateEmployeeWellbeingChild, useUpdateEmployeeWellbeingChild, useDeleteEmployeeWellbeingChild,
} from "../hooks/useEmployeeWellbeing";
import EmployeeWellbeingRecordForm from "../components/EmployeeWellbeingRecordForm";
import CategoryRowForm from "../../../components/brsr/CategoryRowForm";
import { CHILD_CONFIG, type ChildKind, type ChildRow, type EmployeeWellbeingRecord, type EmployeeWellbeingRecordCreate, type EmployeeWellbeingRecordUpdate } from "../api/employeeWellbeingApi";
import ConfirmDialog from "../../../components/ui/ConfirmDialog";

const yesNo = (v: boolean | null | undefined) => (v === null || v === undefined ? "Not stated" : v ? "Yes" : "No");
const pct = (v: unknown) => (v === null || v === undefined ? "Not stated" : `${v}%`);
const num = (v: unknown) => (v === null || v === undefined ? "Not disclosed" : Number(v).toLocaleString("en-IN"));
const KINDS: ChildKind[] = ["measure", "parental", "training", "complaint"];

function ChildTable({ kind, record, onAdd, onEdit, onDelete }: {
  kind: ChildKind; record: EmployeeWellbeingRecord; onAdd: () => void; onEdit: (r: ChildRow) => void; onDelete: (r: ChildRow) => void;
}) {
  const cfg = CHILD_CONFIG[kind];
  const rows = record[cfg.relation as keyof EmployeeWellbeingRecord] as ChildRow[];
  const full = rows.length >= Object.keys(cfg.labels).length;
  return (
    <div>
      <div className="mb-2 flex items-center justify-between">
        <h3 className="font-medium text-gray-700">{cfg.title}</h3>
        <button onClick={onAdd} disabled={full}
          className="rounded bg-green-600 px-3 py-1 text-sm text-white hover:bg-green-700 disabled:cursor-not-allowed disabled:opacity-50">+ Add Row</button>
      </div>
      {rows.length === 0 ? <p className="text-sm text-gray-400">No rows yet.</p> : (
        <table className="w-full text-sm">
          <thead><tr className="border-b text-left text-gray-500">
            <th className="py-2">Category</th>
            {cfg.fields.map((f) => <th key={f.name} className="py-2 text-right">{f.label}{cfg.pctOfTotal.includes(f.name) ? " (n / %)" : ""}</th>)}
            <th className="py-2 text-center">Actions</th>
          </tr></thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id} className="border-b">
                <td className="py-2 font-medium">{cfg.labels[r.category]}</td>
                {cfg.fields.map((f) => (
                  <td key={f.name} className="py-2 text-right">
                    {kind === "parental" ? pct(r[f.name]) : num(r[f.name])}
                    {cfg.pctOfTotal.includes(f.name) && <span className="text-gray-400"> / {pct(r[`${f.name}_percent`])}</span>}
                  </td>
                ))}
                <td className="py-2 text-center">
                  <button onClick={() => onEdit(r)} className="mr-2 text-amber-600 hover:underline">Edit</button>
                  <button onClick={() => onDelete(r)} className="text-red-600 hover:underline">Remove</button>
                </td>
              </tr>
            ))}
            {kind === "complaint" && (
              <tr className="bg-gray-50 font-semibold"><td className="py-2">Total</td>
                <td className="py-2 text-right">{num(record.total_complaints_filed)}</td>
                <td className="py-2 text-right">{num(record.total_complaints_pending)}</td><td /></tr>
            )}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default function EmployeeWellbeingPage() {
  const { data: records = [], isLoading, isError } = useEmployeeWellbeingRecords();
  const createRecord = useCreateEmployeeWellbeingRecord();
  const updateRecord = useUpdateEmployeeWellbeingRecord();
  const deleteRecord = useDeleteEmployeeWellbeingRecord();
  const createChild = useCreateEmployeeWellbeingChild();
  const updateChild = useUpdateEmployeeWellbeingChild();
  const deleteChild = useDeleteEmployeeWellbeingChild();

  const [showRecordForm, setShowRecordForm] = useState(false);
  const [selectedRecord, setSelectedRecord] = useState<EmployeeWellbeingRecord | null>(null);
  const [deleteRecordId, setDeleteRecordId] = useState<number | null>(null);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [childForm, setChildForm] = useState<{ kind: ChildKind; record: EmployeeWellbeingRecord; row?: ChildRow } | null>(null);
  const [deleteChildTarget, setDeleteChildTarget] = useState<{ kind: ChildKind; id: number } | null>(null);

  async function saveRecord(data: EmployeeWellbeingRecordCreate | EmployeeWellbeingRecordUpdate) {
    try {
      if (selectedRecord) await updateRecord.mutateAsync({ id: selectedRecord.id, data });
      else await createRecord.mutateAsync(data as EmployeeWellbeingRecordCreate);
      setShowRecordForm(false); setSelectedRecord(null);
    } catch (e) { console.error(e); }
  }
  async function saveChild(data: Record<string, unknown>) {
    if (!childForm) return;
    try {
      if (childForm.row) await updateChild.mutateAsync({ kind: childForm.kind, childId: childForm.row.id, data });
      else await createChild.mutateAsync({ kind: childForm.kind, recordId: childForm.record.id, data });
      setChildForm(null);
    } catch (e) { console.error(e); }
  }

  if (isLoading) return <div className="p-10 text-center">Loading Principle 3 records...</div>;
  if (isError) return <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-red-600">Unable to load Principle 3 records.</div>;

  return (
    <div className="space-y-6 p-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Employee Well-being (BRSR Principle 3)</h1>
          <p className="text-gray-500">Well-being measures, retirement benefits, parental leave, unions, OHS, incidents, training, complaints. One record per year.</p>
        </div>
        <button onClick={() => { setSelectedRecord(null); setShowRecordForm(true); }}
          className="rounded-lg bg-blue-600 px-5 py-2 font-medium text-white transition hover:bg-blue-700">+ Add Year</button>
      </div>

      {records.length === 0 ? (
        <div className="rounded-lg border border-gray-200 bg-gray-50 p-6 text-center text-gray-500">No Principle 3 records yet.</div>
      ) : (
        <div className="space-y-4">
          {records.map((record) => (
            <div key={record.id} className="rounded-xl border bg-white shadow-sm">
              <div className="flex cursor-pointer items-center justify-between p-5" onClick={() => setExpandedId(expandedId === record.id ? null : record.id)}>
                <div>
                  <h2 className="text-lg font-semibold text-gray-800">{record.reporting_year}</h2>
                  <p className="text-sm text-gray-500">
                    OHS system: <span className="font-semibold">{yesNo(record.has_ohs_management_system)}</span>
                    {" · "}Fatalities (emp / wkr): <span className="font-semibold">{num(record.fatalities_employees)} / {num(record.fatalities_workers)}</span>
                    {" · "}LTIFR (emp / wkr): <span className="font-semibold">{num(record.ltifr_employees)} / {num(record.ltifr_workers)}</span>
                    {" · "}Complaints filed: <span className="font-semibold">{num(record.total_complaints_filed)}</span>
                  </p>
                </div>
                <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
                  <button onClick={() => { setSelectedRecord(record); setShowRecordForm(true); }} className="rounded bg-amber-500 px-3 py-1 text-sm text-white hover:bg-amber-600">Edit</button>
                  <button onClick={() => setDeleteRecordId(record.id)} className="rounded bg-red-600 px-3 py-1 text-sm text-white hover:bg-red-700">Delete</button>
                </div>
              </div>

              {expandedId === record.id && (
                <div className="space-y-6 border-t px-5 py-4">
                  <dl className="grid grid-cols-1 gap-x-8 gap-y-2 text-sm md:grid-cols-2">
                    <div className="flex justify-between"><dt className="text-gray-500">Well-being spend (% revenue)</dt><dd className="font-medium">{pct(record.wellbeing_spend_percent_revenue)}</dd></div>
                    <div className="flex justify-between"><dt className="text-gray-500">PF coverage emp / wkr (deposited)</dt><dd className="font-medium">{pct(record.pf_employees_percent)} / {pct(record.pf_workers_percent)} ({record.pf_deposited ?? "not stated"})</dd></div>
                    <div className="flex justify-between"><dt className="text-gray-500">Union membership emp / wkr</dt><dd className="font-medium">{pct(record.permanent_employees_union_percent)} / {pct(record.permanent_workers_union_percent)}</dd></div>
                    <div className="flex justify-between"><dt className="text-gray-500">Equal opportunity policy</dt><dd className="font-medium">{yesNo(record.has_equal_opportunity_policy)}</dd></div>
                    <div className="flex justify-between"><dt className="text-gray-500">Recordable injuries emp / wkr</dt><dd className="font-medium">{num(record.recordable_injuries_employees)} / {num(record.recordable_injuries_workers)}</dd></div>
                    <div className="flex justify-between"><dt className="text-gray-500">Assessed H&S / working conditions</dt><dd className="font-medium">{pct(record.assessed_health_safety_percent)} / {pct(record.assessed_working_conditions_percent)}</dd></div>
                  </dl>
                  {KINDS.map((kind) => (
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
          <div className="max-h-[90vh] w-full max-w-5xl overflow-y-auto rounded-xl bg-white shadow-2xl"><div className="p-6">
            <EmployeeWellbeingRecordForm initialData={selectedRecord ?? undefined} onSubmit={saveRecord}
              loading={createRecord.isPending || updateRecord.isPending}
              onCancel={() => { setShowRecordForm(false); setSelectedRecord(null); }} />
          </div></div>
        </div>
      )}
      {childForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-6">
          <div className="max-h-[90vh] w-full max-w-4xl overflow-y-auto rounded-xl bg-white shadow-2xl"><div className="p-6">
            <CategoryRowForm config={CHILD_CONFIG[childForm.kind]} initialData={childForm.row}
              usedCategories={(childForm.record[CHILD_CONFIG[childForm.kind].relation as keyof EmployeeWellbeingRecord] as ChildRow[]).map((r) => r.category)}
              onSubmit={saveChild} loading={createChild.isPending || updateChild.isPending} onCancel={() => setChildForm(null)} />
          </div></div>
        </div>
      )}

      <ConfirmDialog open={deleteRecordId !== null} title="Delete Principle 3 Record"
        message="Are you sure? This will also delete all well-being, parental leave, training and complaint rows under this year."
        loading={deleteRecord.isPending} onCancel={() => setDeleteRecordId(null)}
        onConfirm={async () => { if (deleteRecordId === null) return; await deleteRecord.mutateAsync(deleteRecordId); setDeleteRecordId(null); }} />
      <ConfirmDialog open={deleteChildTarget !== null} title="Delete Row" message="Are you sure you want to delete this row?"
        loading={deleteChild.isPending} onCancel={() => setDeleteChildTarget(null)}
        onConfirm={async () => { if (!deleteChildTarget) return; await deleteChild.mutateAsync({ kind: deleteChildTarget.kind, childId: deleteChildTarget.id }); setDeleteChildTarget(null); }} />
    </div>
  );
}
