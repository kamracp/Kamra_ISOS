import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import productionRecordApi, {
  type ProductionRecord,
  type ProductionRecordCreate,
  type ProductionRecordUpdate,
} from "../api/productionRecordApi";
import { getApiErrorMessage } from "../../../utils/apiError";

const QUERY_KEY = ["production-records"] as const;

export function useProductionRecords(manufacturingUnitId?: number) {
  return useQuery<ProductionRecord[]>({
    queryKey: [...QUERY_KEY, manufacturingUnitId ?? "all"],
    queryFn: () => productionRecordApi.getAll(manufacturingUnitId),
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: false,
  });
}

export function useCreateProductionRecord() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ProductionRecordCreate) => productionRecordApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: ["manufacturing-units"] });
      toast.success("Production record created successfully.");
    },
    onError: (error: any) => {
      toast.error(
        getApiErrorMessage(error, "Failed to create production record.")
      );
    },
  });
}

export function useUpdateProductionRecord() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: ProductionRecordUpdate }) =>
      productionRecordApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: ["manufacturing-units"] });
      toast.success("Production record updated successfully.");
    },
    onError: (error: any) => {
      toast.error(
        getApiErrorMessage(error, "Failed to update production record.")
      );
    },
  });
}

export function useDeleteProductionRecord() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => productionRecordApi.remove(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: ["manufacturing-units"] });
      toast.success("Production record deleted successfully.");
    },
    onError: (error: any) => {
      toast.error(
        getApiErrorMessage(error, "Failed to delete production record.")
      );
    },
  });
}
