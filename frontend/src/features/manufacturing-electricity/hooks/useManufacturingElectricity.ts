import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import manufacturingElectricityApi, {
  type ManufacturingElectricityRecordCreate,
  type ManufacturingElectricityRecordUpdate,
} from "../api/manufacturingElectricityApi";
import { getApiErrorMessage } from "../../../utils/apiError";

const QUERY_KEY = ["manufacturing-electricity-records"] as const;

export function useManufacturingElectricityRecords(year?: number) {
  return useQuery({
    queryKey: [...QUERY_KEY, year],
    queryFn: () => manufacturingElectricityApi.getAll(year),
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: false,
  });
}

export function useCreateManufacturingElectricityRecord() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ManufacturingElectricityRecordCreate) => manufacturingElectricityApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      toast.success("Electricity record created successfully.");
    },
    onError: (error: any) => {
      toast.error(getApiErrorMessage(error, "Failed to create electricity record."));
    },
  });
}

export function useUpdateManufacturingElectricityRecord() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: ManufacturingElectricityRecordUpdate }) =>
      manufacturingElectricityApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      toast.success("Electricity record updated successfully.");
    },
    onError: (error: any) => {
      toast.error(getApiErrorMessage(error, "Failed to update electricity record."));
    },
  });
}

export function useDeleteManufacturingElectricityRecord() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => manufacturingElectricityApi.remove(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      toast.success("Electricity record deleted successfully.");
    },
    onError: (error: any) => {
      toast.error(getApiErrorMessage(error, "Failed to delete electricity record."));
    },
  });
}
