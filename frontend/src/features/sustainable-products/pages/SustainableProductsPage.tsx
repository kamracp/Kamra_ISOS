import { useState } from "react";

import {
  useSustainableProductRecords,
  useCreateSustainableProductRecord,
  useUpdateSustainableProductRecord,
  useDeleteSustainableProductRecord,
  useCreateReclaimedMaterial,
  useUpdateReclaimedMaterial,
  useDeleteReclaimedMaterial,
} from "../hooks/useSustainableProducts";
import SustainableProductRecordForm from "../components/SustainableProductRecordForm";
import ReclaimedMaterialForm from "../components/ReclaimedMaterialForm";
import {
  RECLAIM_CATEGORY_LABELS,
  type ReclaimedMaterial,
  type ReclaimedMaterialCreate,
  type ReclaimedMaterialUpdate,
  type SustainableProductRecord,
  type SustainableProductRecordCreate,
  type SustainableProductRecordUpdate,
} from "../api/sustainableProductsApi";
import ConfirmDialog from "../../../components/ui/ConfirmDialog";

// Null/undefined must read as "not stated" -- never as 0, "No" or blank.
const yesNo = (v: boolean | null | undefined) => (v === null || v === undefined ? "Not stated" : v ? "Yes" : "No");
const pct = (v: number | null | undefined) => (v === null || v === undefined ? "Not stated" : `${v}%`);
const mt = (v: number | null | undefined) => (v === null || v === undefined ? "Not tracked" : v.toFixed(3));

export default function SustainableProductsPage() {
  const { data: records = [], isLoading, isError } = useSustainableProductRecords();

  const createRecord = useCreateSustainableProductRecord();
  const updateRecord = useUpdateSustainableProductRecord();
  const deleteRecord = useDeleteSustainableProductRecord();
  const createMaterial = useCreateReclaimedMaterial();
  const updateMaterial = useUpdateReclaimedMaterial();
  const deleteMaterial = useDeleteReclaimedMaterial();

  const [showRecordForm, setShowRecordForm] = useState(false);
  const [selectedRecord, setSelectedRecord] = useState<SustainableProductRecord | null>(null);
  const [deleteRecordId, setDeleteRecordId] = useState<number | null>(null);

  const [materialFormFor, setMaterialFormFor] = useState<SustainableProductRecord | null>(null);
  const [selectedMaterial, setSelectedMaterial] = useState<ReclaimedMaterial | null>(null);
  const [deleteMaterialId, setDeleteMaterialId] = useState<number | null>(null);

  const [expandedId, setExpandedId] = useState<number | null>(null);

  // Hooks already toast on error; the catch only stops the modal closing.
  async function saveRecord(data: SustainableProductRecordCreate | SustainableProductRecordUpdate) {
    try {
      if (selectedRecord) {
        await updateRecord.mutateAsync({ id: selectedRecord.id, data });
      } else {
        await createRecord.mutateAsync(data as SustainableProductRecordCreate);
      }
      setShowRecordForm(false);
      setSelectedRecord(null);
    } catch (error) {
      console.error(error);
    }
  }

  async function saveMaterial(data: ReclaimedMaterialCreate | ReclaimedMaterialUpdate) {
    if (materialFormFor === null) return;
    try {
      if (selectedMaterial) {
        await updateMaterial.mutateAsync({ materialId: selectedMaterial.id, data });
      } else {
        await createMaterial.mutateAsync({ recordId: materialFormFor.id, data: data as ReclaimedMaterialCreate });
      }
      setMaterialFormFor(null);
      setSelectedMaterial(null);
    } catch (error) {
      console.error(error);
    }
  }

  if (isLoading) return <div className="p-10 text-center">Loading Principle 2 records...</div>;
  if (isError) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-red-600">
        Unable to load Principle 2 records.
      </div>
    );
  }

  return (
    <div className="space-y-6 p-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Sustainable Products (BRSR Principle 2)</h1>
          <p className="text-gray-500">
            Sustainable and safe goods and services -- R&D/capex, sourcing, reclaim processes, EPR. One record per year.
          </p>
        </div>
        <button
          onClick={() => { setSelectedRecord(null); setShowRecordForm(true); }}
          className="rounded-lg bg-blue-600 px-5 py-2 font-medium text-white transition hover:bg-blue-700"
        >
          + Add Year
        </button>
      </div>

      {records.length === 0 ? (
        <div className="rounded-lg border border-gray-200 bg-gray-50 p-6 text-center text-gray-500">
          No Principle 2 records yet.
        </div>
      ) : (
        <div className="space-y-4">
          {records.map((record) => {
            const used = record.reclaimed_materials.map((m) => m.material_category);
            return (
              <div key={record.id} className="rounded-xl border bg-white shadow-sm">
                <div
                  className="flex cursor-pointer items-center justify-between p-5"
                  onClick={() => setExpandedId(expandedId === record.id ? null : record.id)}
                >
                  <div>
                    <h2 className="text-lg font-semibold text-gray-800">{record.reporting_year}</h2>
                    <p className="text-sm text-gray-500">
                      Sustainable sourcing: <span className="font-semibold">{pct(record.sustainable_sourcing_percent)}</span>
                      {" · "}EPR applicable: <span className="font-semibold">{yesNo(record.epr_applicable)}</span>
                      {" · "}{record.reclaimed_materials.length} of 4 material categories
                    </p>
                  </div>
                  <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
                    <button
                      onClick={() => { setSelectedRecord(record); setShowRecordForm(true); }}
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
                  <div className="space-y-5 border-t px-5 py-4">
                    <dl className="grid grid-cols-1 gap-x-8 gap-y-2 text-sm md:grid-cols-2">
                      <div className="flex justify-between"><dt className="text-gray-500">R&D on sustainable tech (current / previous)</dt><dd className="font-medium">{pct(record.rnd_sustainable_percent_current)} / {pct(record.rnd_sustainable_percent_previous)}</dd></div>
                      <div className="flex justify-between"><dt className="text-gray-500">Capex on sustainable tech (current / previous)</dt><dd className="font-medium">{pct(record.capex_sustainable_percent_current)} / {pct(record.capex_sustainable_percent_previous)}</dd></div>
                      <div className="flex justify-between"><dt className="text-gray-500">Sustainable sourcing procedure</dt><dd className="font-medium">{yesNo(record.has_sustainable_sourcing_procedure)}</dd></div>
                      <div className="flex justify-between"><dt className="text-gray-500">EPR plan in line</dt><dd className="font-medium">{yesNo(record.epr_plan_in_line)}</dd></div>
                      <div className="flex justify-between"><dt className="text-gray-500">LCA conducted</dt><dd className="font-medium">{yesNo(record.has_conducted_lca)}</dd></div>
                      <div className="flex justify-between"><dt className="text-gray-500">Recycled input material</dt><dd className="font-medium">{pct(record.recycled_input_percent)}</dd></div>
                    </dl>

                    <div>
                      <div className="mb-3 flex items-center justify-between">
                        <h3 className="font-medium text-gray-700">Reclaimed materials (Leadership Indicator 4)</h3>
                        <button
                          onClick={() => { setMaterialFormFor(record); setSelectedMaterial(null); }}
                          disabled={used.length >= 4}
                          className="rounded bg-green-600 px-3 py-1 text-sm text-white hover:bg-green-700 disabled:cursor-not-allowed disabled:opacity-50"
                        >
                          + Add Material Row
                        </button>
                      </div>

                      {record.reclaimed_materials.length === 0 ? (
                        <p className="text-sm text-gray-400">No reclaimed material rows yet.</p>
                      ) : (
                        <table className="w-full text-sm">
                          <thead>
                            <tr className="border-b text-left text-gray-500">
                              <th className="py-2">Material</th>
                              <th className="py-2 text-right">Re-used (MT)</th>
                              <th className="py-2 text-right">Recycled (MT)</th>
                              <th className="py-2 text-right">Disposed (MT)</th>
                              <th className="py-2 text-center">Actions</th>
                            </tr>
                          </thead>
                          <tbody>
                            {record.reclaimed_materials.map((m) => (
                              <tr key={m.id} className="border-b">
                                <td className="py-2 font-medium">{RECLAIM_CATEGORY_LABELS[m.material_category]}</td>
                                <td className="py-2 text-right">{mt(m.reused_mt)}</td>
                                <td className="py-2 text-right">{mt(m.recycled_mt)}</td>
                                <td className="py-2 text-right">{mt(m.disposed_mt)}</td>
                                <td className="py-2 text-center">
                                  <button
                                    onClick={() => { setMaterialFormFor(record); setSelectedMaterial(m); }}
                                    className="mr-2 text-amber-600 hover:underline"
                                  >
                                    Edit
                                  </button>
                                  <button onClick={() => setDeleteMaterialId(m.id)} className="text-red-600 hover:underline">
                                    Remove
                                  </button>
                                </td>
                              </tr>
                            ))}
                            {/* Totals come from the backend -- derived, never stored. */}
                            <tr className="bg-gray-50 font-semibold">
                              <td className="py-2">Total</td>
                              <td className="py-2 text-right">{mt(record.total_reused_mt)}</td>
                              <td className="py-2 text-right">{mt(record.total_recycled_mt)}</td>
                              <td className="py-2 text-right">{mt(record.total_disposed_mt)}</td>
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
          <div className="max-h-[90vh] w-full max-w-4xl overflow-y-auto rounded-xl bg-white shadow-2xl">
            <div className="p-6">
              <SustainableProductRecordForm
                initialData={selectedRecord ?? undefined}
                onSubmit={saveRecord}
                loading={createRecord.isPending || updateRecord.isPending}
                onCancel={() => { setShowRecordForm(false); setSelectedRecord(null); }}
              />
            </div>
          </div>
        </div>
      )}

      {materialFormFor !== null && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-6">
          <div className="max-h-[90vh] w-full max-w-3xl overflow-y-auto rounded-xl bg-white shadow-2xl">
            <div className="p-6">
              <ReclaimedMaterialForm
                initialData={selectedMaterial ?? undefined}
                usedCategories={materialFormFor.reclaimed_materials.map((m) => m.material_category)}
                onSubmit={saveMaterial}
                loading={createMaterial.isPending || updateMaterial.isPending}
                onCancel={() => { setMaterialFormFor(null); setSelectedMaterial(null); }}
              />
            </div>
          </div>
        </div>
      )}

      <ConfirmDialog
        open={deleteRecordId !== null}
        title="Delete Principle 2 Record"
        message="Are you sure? This will also delete all reclaimed material rows under this year."
        loading={deleteRecord.isPending}
        onCancel={() => setDeleteRecordId(null)}
        onConfirm={async () => {
          if (deleteRecordId === null) return;
          await deleteRecord.mutateAsync(deleteRecordId);
          setDeleteRecordId(null);
        }}
      />

      <ConfirmDialog
        open={deleteMaterialId !== null}
        title="Delete Reclaimed Material Row"
        message="Are you sure you want to delete this row?"
        loading={deleteMaterial.isPending}
        onCancel={() => setDeleteMaterialId(null)}
        onConfirm={async () => {
          if (deleteMaterialId === null) return;
          await deleteMaterial.mutateAsync(deleteMaterialId);
          setDeleteMaterialId(null);
        }}
      />
    </div>
  );
}
