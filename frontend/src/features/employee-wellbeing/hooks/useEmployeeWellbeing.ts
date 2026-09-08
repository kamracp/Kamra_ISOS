import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import api, { type ChildKind, type EmployeeWellbeingRecord, type EmployeeWellbeingRecordCreate, type EmployeeWellbeingRecordUpdate } from "../api/employeeWellbeingApi";
import { getApiErrorMessage } from "../../../utils/apiError";

const QUERY_KEY = ["employee-wellbeing-records"] as const;

function useInvalidatingMutation<TVars>(mutationFn: (v: TVars) => Promise<unknown>, ok: string, fail: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn,
    onSuccess: () => { qc.invalidateQueries({ queryKey: QUERY_KEY }); toast.success(ok); },
    onError: (error: unknown) => { toast.error(getApiErrorMessage(error, fail)); },
  });
}

export function useEmployeeWellbeingRecords() {
  return useQuery<EmployeeWellbeingRecord[]>({ queryKey: QUERY_KEY, queryFn: () => api.getAll(), staleTime: 5 * 60 * 1000, refetchOnWindowFocus: false });
}
export const useCreateEmployeeWellbeingRecord = () =>
  useInvalidatingMutation((d: EmployeeWellbeingRecordCreate) => api.create(d), "Principle 3 record created.", "Failed to create Principle 3 record.");
export const useUpdateEmployeeWellbeingRecord = () =>
  useInvalidatingMutation(({ id, data }: { id: number; data: EmployeeWellbeingRecordUpdate }) => api.update(id, data), "Principle 3 record updated.", "Failed to update Principle 3 record.");
export const useDeleteEmployeeWellbeingRecord = () =>
  useInvalidatingMutation((id: number) => api.remove(id), "Principle 3 record deleted.", "Failed to delete Principle 3 record.");
export const useCreateEmployeeWellbeingChild = () =>
  useInvalidatingMutation(({ kind, recordId, data }: { kind: ChildKind; recordId: number; data: Record<string, unknown> }) => api.createChild(kind, recordId, data), "Row added.", "Failed to add row.");
export const useUpdateEmployeeWellbeingChild = () =>
  useInvalidatingMutation(({ kind, childId, data }: { kind: ChildKind; childId: number; data: Record<string, unknown> }) => api.updateChild(kind, childId, data), "Row updated.", "Failed to update row.");
export const useDeleteEmployeeWellbeingChild = () =>
  useInvalidatingMutation(({ kind, childId }: { kind: ChildKind; childId: number }) => api.removeChild(kind, childId), "Row deleted.", "Failed to delete row.");
