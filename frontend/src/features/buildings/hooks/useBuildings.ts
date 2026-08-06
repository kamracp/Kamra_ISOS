import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import buildingApi, {
  type Building,
  type BuildingCreate,
  type BuildingUpdate,
} from "../api/buildingApi";
import { getApiErrorMessage } from "../../../utils/apiError";

const QUERY_KEY = ["buildings"] as const;

export function useBuildings() {
  return useQuery<Building[]>({
    queryKey: QUERY_KEY,
    queryFn: buildingApi.getAll,
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: false,
  });
}

export function useBuilding(id?: number) {
  return useQuery<Building>({
    queryKey: [...QUERY_KEY, id],
    queryFn: () => buildingApi.getById(id as number),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
  });
}

export function useCreateBuilding() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: BuildingCreate) => buildingApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      toast.success("Building created successfully.");
    },
    onError: (error: any) => {
      toast.error(
        getApiErrorMessage(error, "Failed to create building.")
      );
    },
  });
}

export function useUpdateBuilding() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: BuildingUpdate }) =>
      buildingApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      toast.success("Building updated successfully.");
    },
    onError: (error: any) => {
      toast.error(
        getApiErrorMessage(error, "Failed to update building.")
      );
    },
  });
}

export function useDeleteBuilding() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => buildingApi.remove(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      toast.success("Building deleted successfully.");
    },
    onError: (error: any) => {
      toast.error(
        getApiErrorMessage(error, "Failed to delete building.")
      );
    },
  });
}
