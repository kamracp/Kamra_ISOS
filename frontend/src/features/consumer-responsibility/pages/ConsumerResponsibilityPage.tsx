import { useState } from "react";
import {
  useConsumerResponsibilityRecords, useCreateConsumerResponsibilityRecord, useUpdateConsumerResponsibilityRecord,
  useDeleteConsumerResponsibilityRecord, useCreateConsumerComplaint, useUpdateConsumerComplaint, useDeleteConsumerComplaint,
} from "../hooks/useConsumerResponsibility";
import ConsumerResponsibilityRecordForm from "../components/ConsumerResponsibilityRecordForm";
import ConsumerComplaintForm from "../components/ConsumerComplaintForm";
import {
  COMPLAINT_LABELS, type ConsumerComplaint, type ConsumerComplaintFields,
  type ConsumerResponsibilityRecord, type ConsumerResponsibilityRecordCreate, type ConsumerResponsibilityRecordUpdate,
} from "../api/consumerResponsibilityApi";
import ConfirmDialog from "../../../components/ui/ConfirmDialog";

const yesNo = (v: boolean | null | undefined) => (v === null || v === undefined ? "Not stated" : v ? "Yes" : "No");
const pct = (v: number | null | undefined) => (v === null || v === undefined ? "Not stated" : `${v}%`);
const num = (v: number | null | undefined) => (v === null || v === undefined ? "Not disclosed" : v.toLocaleString("en-IN"));

export default function ConsumerResponsibilityPage() {
  const { data: records = [], isLoading, isError } = useConsumerResponsibilityRecords();
  const createRecord = useCreateConsumerResponsibilityRecord();
  const updateRecord = useUpdateConsumerResponsibilityRecord();
  const deleteRecord = useDeleteConsumerResponsibilityRecord();
  const createComplaint = useCreateConsumerComplaint();
  const updateComplaint = useUpdateConsumerComplaint();
  const deleteComplaint = useDeleteConsumerComplaint();

  const [showRecordForm, setShowRecordForm] = useState(false);
  const [selectedRecord, setSelectedRecord] = useState<ConsumerResponsibilityRecord | null>(null);
  const [deleteRecordId, setDeleteRecordId] = useState<number | null>(null);
  const [complaintFormFor, setComplaintFormFor] = useState<ConsumerResponsibilityRecord | null>(null);
  const [selectedComplaint, setSelectedComplaint] = useState<ConsumerComplaint | null>(null);
  const [deleteComplaintId, setDeleteComplaintId] = useState<number | null>(null);
  const [expandedId, setExpandedId] = useState<number | null>(null);

  async function saveRecord(data: ConsumerResponsibilityRecordCreate | ConsumerResponsibilityRecordUpdate) {
    try {
      if (selectedRecord) await updateRecord.mutateAsync({ id: selectedRecord.id, data });
      else await createRecord.mutateAsync(data as ConsumerResponsibilityRecordCreate);
      setShowRecordForm(false); setSelectedRecord(null);
    } catch (e) { console.error(e); }
  }
  async function saveComplaint(data: ConsumerComplaintFields | Partial<ConsumerComplaintFields>) {
    if (!complaintFormFor) return;
    try {
      if (selectedComplaint) await updateComplaint.mutateAsync({ id: selectedComplaint.id, data });
      else await createComplaint.mutateAsync({ recordId: complaintFormFor.id, data: data as ConsumerComplaintFields });
      setComplaintFormFor(null); setSelectedComplaint(null);
    } catch (e) { console.error(e); }
  }

  if (isLoading) return <div className="p-10 text-center">Loading Principle 9 records...</div>;
  if (isError) return <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-red-600">Unable to load Principle 9 records.</div>;

  return (
    <div className="space-y-6 p-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Consumer Responsibility (BRSR Principle 9)</h1>
          <p className="text-gray-500">Complaints, product information, recalls, cyber security, data breaches. One record per year.</p>
        </div>
        <button onClick={() => { setSelectedRecord(null); setShowRecordForm(true); }}
          className="rounded-lg bg-blue-600 px-5 py-2 font-medium text-white transition hover:bg-blue-700">+ Add Year</button>
      </div>

      {records.length === 0 ? (
        <div className="rounded-lg border border-gray-200 bg-gray-50 p-6 text-center text-gray-500">No Principle 9 records yet.</div>
      ) : (
        <div className="space-y-4">
          {records.map((record) => {
            const used = record.complaints.map((c) => c.category);
            return (
              <div key={record.id} className="rounded-xl border bg-white shadow-sm">
                <div className="flex cursor-pointer items-center justify-between p-5"
                  onClick={() => setExpandedId(expandedId === record.id ? null : record.id)}>
                  <div>
                    <h2 className="text-lg font-semibold text-gray-800">{record.reporting_year}</h2>
                    <p className="text-sm text-gray-500">
                      Cyber security policy: <span className="font-semibold">{yesNo(record.has_cyber_security_policy)}</span>
                      {" · "}Complaints received: <span className="font-semibold">{num(record.total_complaints_received)}</span>
                      {" · "}Data breaches: <span className="font-semibold">{num(record.data_breaches_count)}</span>
                      {" · "}{record.complaints.length} of 7 complaint categories
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
                  <div className="space-y-5 border-t px-5 py-4">
                    <dl className="grid grid-cols-1 gap-x-8 gap-y-2 text-sm md:grid-cols-2">
                      <div className="flex justify-between"><dt className="text-gray-500">Turnover with env/social info</dt><dd className="font-medium">{pct(record.turnover_percent_env_social_info)}</dd></div>
                      <div className="flex justify-between"><dt className="text-gray-500">Turnover with safe-usage info</dt><dd className="font-medium">{pct(record.turnover_percent_safe_usage_info)}</dd></div>
                      <div className="flex justify-between"><dt className="text-gray-500">Turnover with recycling info</dt><dd className="font-medium">{pct(record.turnover_percent_recycling_info)}</dd></div>
                      <div className="flex justify-between"><dt className="text-gray-500">Recalls -- voluntary / forced</dt><dd className="font-medium">{num(record.voluntary_recalls_count)} / {num(record.forced_recalls_count)}</dd></div>
                      <div className="flex justify-between"><dt className="text-gray-500">Consumer survey conducted</dt><dd className="font-medium">{yesNo(record.consumer_survey_conducted)}</dd></div>
                      <div className="flex justify-between"><dt className="text-gray-500">Breaches involving PII</dt><dd className="font-medium">{pct(record.data_breach_pii_percent)}</dd></div>
                    </dl>

                    <div>
                      <div className="mb-3 flex items-center justify-between">
                        <h3 className="font-medium text-gray-700">Consumer complaints (EI 6)</h3>
                        <button onClick={() => { setComplaintFormFor(record); setSelectedComplaint(null); }} disabled={used.length >= 7}
                          className="rounded bg-green-600 px-3 py-1 text-sm text-white hover:bg-green-700 disabled:cursor-not-allowed disabled:opacity-50">+ Add Complaint Row</button>
                      </div>
                      {record.complaints.length === 0 ? (
                        <p className="text-sm text-gray-400">No complaint rows yet.</p>
                      ) : (
                        <table className="w-full text-sm">
                          <thead><tr className="border-b text-left text-gray-500">
                            <th className="py-2">Category</th><th className="py-2 text-right">Received</th><th className="py-2 text-right">Pending</th><th className="py-2 text-center">Actions</th>
                          </tr></thead>
                          <tbody>
                            {record.complaints.map((c) => (
                              <tr key={c.id} className="border-b">
                                <td className="py-2 font-medium">{COMPLAINT_LABELS[c.category]}</td>
                                <td className="py-2 text-right">{num(c.received_count)}</td>
                                <td className="py-2 text-right">{num(c.pending_count)}</td>
                                <td className="py-2 text-center">
                                  <button onClick={() => { setComplaintFormFor(record); setSelectedComplaint(c); }} className="mr-2 text-amber-600 hover:underline">Edit</button>
                                  <button onClick={() => setDeleteComplaintId(c.id)} className="text-red-600 hover:underline">Remove</button>
                                </td>
                              </tr>
                            ))}
                            <tr className="bg-gray-50 font-semibold">
                              <td className="py-2">Total</td>
                              <td className="py-2 text-right">{num(record.total_complaints_received)}</td>
                              <td className="py-2 text-right">{num(record.total_complaints_pending)}</td>
                              <td />
                            </tr>
                          </tbody>
                        </table>
                      )}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {showRecordForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-6">
          <div className="max-h-[90vh] w-full max-w-4xl overflow-y-auto rounded-xl bg-white shadow-2xl"><div className="p-6">
            <ConsumerResponsibilityRecordForm initialData={selectedRecord ?? undefined} onSubmit={saveRecord}
              loading={createRecord.isPending || updateRecord.isPending}
              onCancel={() => { setShowRecordForm(false); setSelectedRecord(null); }} />
          </div></div>
        </div>
      )}
      {complaintFormFor && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-6">
          <div className="max-h-[90vh] w-full max-w-3xl overflow-y-auto rounded-xl bg-white shadow-2xl"><div className="p-6">
            <ConsumerComplaintForm initialData={selectedComplaint ?? undefined}
              usedCategories={complaintFormFor.complaints.map((c) => c.category)} onSubmit={saveComplaint}
              loading={createComplaint.isPending || updateComplaint.isPending}
              onCancel={() => { setComplaintFormFor(null); setSelectedComplaint(null); }} />
          </div></div>
        </div>
      )}

      <ConfirmDialog open={deleteRecordId !== null} title="Delete Principle 9 Record"
        message="Are you sure? This will also delete all complaint rows under this year."
        loading={deleteRecord.isPending} onCancel={() => setDeleteRecordId(null)}
        onConfirm={async () => { if (deleteRecordId === null) return; await deleteRecord.mutateAsync(deleteRecordId); setDeleteRecordId(null); }} />
      <ConfirmDialog open={deleteComplaintId !== null} title="Delete Complaint Row" message="Are you sure you want to delete this row?"
        loading={deleteComplaint.isPending} onCancel={() => setDeleteComplaintId(null)}
        onConfirm={async () => { if (deleteComplaintId === null) return; await deleteComplaint.mutateAsync(deleteComplaintId); setDeleteComplaintId(null); }} />
    </div>
  );
}
