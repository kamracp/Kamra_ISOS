import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import api, {
  type ConsumerComplaintFields, type ConsumerResponsibilityRecord,
  type ConsumerResponsibilityRecordCreate, type ConsumerResponsibilityRecordUpdate,
} from "../api/consumerResponsibilityApi";
import { getApiErrorMessage } from "../../../utils/apiError";

const QUERY_KEY = ["consumer-responsibility-records"] as const;

function useInvalidatingMutation<TVars>(mutationFn: (v: TVars) => Promise<unknown>, ok: string, fail: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn,
    onSuccess: () => { qc.invalidateQueries({ queryKey: QUERY_KEY }); toast.success(ok); },
    onError: (error: unknown) => { toast.error(getApiErrorMessage(error, fail)); },
  });
}

export function useConsumerResponsibilityRecords() {
  return useQuery<ConsumerResponsibilityRecord[]>({
    queryKey: QUERY_KEY, queryFn: () => api.getAll(), staleTime: 5 * 60 * 1000, refetchOnWindowFocus: false,
  });
}
export const useCreateConsumerResponsibilityRecord = () =>
  useInvalidatingMutation((d: ConsumerResponsibilityRecordCreate) => api.create(d), "Principle 9 record created.", "Failed to create Principle 9 record.");
export const useUpdateConsumerResponsibilityRecord = () =>
  useInvalidatingMutation(({ id, data }: { id: number; data: ConsumerResponsibilityRecordUpdate }) => api.update(id, data), "Principle 9 record updated.", "Failed to update Principle 9 record.");
export const useDeleteConsumerResponsibilityRecord = () =>
  useInvalidatingMutation((id: number) => api.remove(id), "Principle 9 record deleted.", "Failed to delete Principle 9 record.");
export const useCreateConsumerComplaint = () =>
  useInvalidatingMutation(({ recordId, data }: { recordId: number; data: ConsumerComplaintFields }) => api.createComplaint(recordId, data), "Complaint row added.", "Failed to add complaint row.");
export const useUpdateConsumerComplaint = () =>
  useInvalidatingMutation(({ id, data }: { id: number; data: Partial<ConsumerComplaintFields> }) => api.updateComplaint(id, data), "Complaint row updated.", "Failed to update complaint row.");
export const useDeleteConsumerComplaint = () =>
  useInvalidatingMutation((id: number) => api.removeComplaint(id), "Complaint row deleted.", "Failed to delete complaint row.");
