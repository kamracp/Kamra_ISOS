import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import manufacturingUnitApi, {
  type ManufacturingUnit,
  type ManufacturingUnitCreate,
  type ManufacturingUnitUpdate,
  type SecSummary,
} from "../api/manufacturingUnitApi";
import { getApiErrorMessage } from "../../../utils/apiError";

const QUERY_KEY = ["manufacturing-units"] as const;

export function useManufacturingUnits() {
  return useQuery<ManufacturingUnit[]>({
    queryKey: QUERY_KEY,
    queryFn: () => manufacturingUnitApi.getAll(),
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: false,
  });
}

export function useManufacturingUnitById(id?: number) {
  return useQuery<ManufacturingUnit>({
    queryKey: [...QUERY_KEY, "detail", id],
    queryFn: () => manufacturingUnitApi.getById(id as number),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
  });
}

export function useSecSummary(id?: number) {
  return useQuery<SecSummary>({
    queryKey: [...QUERY_KEY, "sec-summary", id],
    queryFn: () => manufacturingUnitApi.getSecSummary(id as number),
    enabled: !!id,
    staleTime: 2 * 60 * 1000,
  });
}

export function useCreateManufacturingUnit() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ManufacturingUnitCreate) => manufacturingUnitApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      toast.success("Manufacturing unit created successfully.");
    },
    onError: (error: any) => {
      toast.error(
        getApiErrorMessage(error, "Failed to create manufacturing unit.")
      );
    },
  });
}

export function useUpdateManufacturingUnit() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: ManufacturingUnitUpdate }) =>
      manufacturingUnitApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      toast.success("Manufacturing unit updated successfully.");
    },
    onError: (error: any) => {
      toast.error(
        getApiErrorMessage(error, "Failed to update manufacturing unit.")
      );
    },
  });
}

export function useDeleteManufacturingUnit() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => manufacturingUnitApi.remove(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      toast.success("Manufacturing unit deleted successfully.");
    },
    onError: (error: any) => {
      toast.error(
        getApiErrorMessage(error, "Failed to delete manufacturing unit.")
      );
    },
  });
}
