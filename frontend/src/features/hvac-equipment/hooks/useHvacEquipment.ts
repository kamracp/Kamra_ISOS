import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import hvacEquipmentApi, {
  type HvacEquipment,
  type HvacEquipmentCreate,
  type HvacEquipmentUpdate,
} from "../api/hvacEquipmentApi";
import { getApiErrorMessage } from "../../../utils/apiError";

const QUERY_KEY = ["hvac-equipment"] as const;

export function useHvacEquipment(buildingId?: number) {
  return useQuery<HvacEquipment[]>({
    queryKey: [...QUERY_KEY, buildingId ?? "all"],
    queryFn: () => hvacEquipmentApi.getAll(buildingId),
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: false,
  });
}

export function useHvacEquipmentById(id?: number) {
  return useQuery<HvacEquipment>({
    queryKey: [...QUERY_KEY, "detail", id],
    queryFn: () => hvacEquipmentApi.getById(id as number),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
  });
}

export function useCreateHvacEquipment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: HvacEquipmentCreate) => hvacEquipmentApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      toast.success("Equipment created successfully.");
    },
    onError: (error: any) => {
      toast.error(
        getApiErrorMessage(error, "Failed to create equipment.")
      );
    },
  });
}

export function useUpdateHvacEquipment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: HvacEquipmentUpdate }) =>
      hvacEquipmentApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      toast.success("Equipment updated successfully.");
    },
    onError: (error: any) => {
      toast.error(
        getApiErrorMessage(error, "Failed to update equipment.")
      );
    },
  });
}

export function useDeleteHvacEquipment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => hvacEquipmentApi.remove(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      toast.success("Equipment deleted successfully.");
    },
    onError: (error: any) => {
      toast.error(
        getApiErrorMessage(error, "Failed to delete equipment.")
      );
    },
  });
}
