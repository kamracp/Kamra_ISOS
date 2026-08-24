import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import ethicsApi, {
  type EthicsRecord,
  type EthicsRecordCreate,
  type EthicsRecordUpdate,
} from "../api/ethicsApi";
import { getApiErrorMessage } from "../../../utils/apiError";

const QUERY_KEY = ["ethics-records"] as const;

export function useEthicsRecords() {
  return useQuery<EthicsRecord[]>({
    queryKey: QUERY_KEY,
    queryFn: () => ethicsApi.getAll(),
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: false,
  });
}

export function useCreateEthicsRecord() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: EthicsRecordCreate) => ethicsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      toast.success("Ethics record created successfully.");
    },
    onError: (error: any) => {
      toast.error(getApiErrorMessage(error, "Failed to create ethics record."));
    },
  });
}

export function useUpdateEthicsRecord() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: EthicsRecordUpdate }) =>
      ethicsApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      toast.success("Ethics record updated successfully.");
    },
    onError: (error: any) => {
      toast.error(getApiErrorMessage(error, "Failed to update ethics record."));
    },
  });
}

export function useDeleteEthicsRecord() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => ethicsApi.remove(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      toast.success("Ethics record deleted successfully.");
    },
    onError: (error: any) => {
      toast.error(getApiErrorMessage(error, "Failed to delete ethics record."));
    },
  });
}
