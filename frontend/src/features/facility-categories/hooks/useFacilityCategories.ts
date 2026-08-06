import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import facilityCategoryApi, {
  type FacilityCategory,
  type FacilityCategoryCreate,
} from "../api/facilityCategoryApi";
import { getApiErrorMessage } from "../../../utils/apiError";

export function useFacilityCategories(segment: "benas" | "manufacturing") {
  return useQuery<FacilityCategory[]>({
    queryKey: ["facility-categories", segment],
    queryFn: () => facilityCategoryApi.getBySegment(segment),
    staleTime: 5 * 60 * 1000,
  });
}

export function useCreateFacilityCategory(segment: "benas" | "manufacturing") {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: FacilityCategoryCreate) => facilityCategoryApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["facility-categories", segment] });
    },
    onError: (error: any) => {
      toast.error(getApiErrorMessage(error, "Failed to add category."));
    },
  });
}

export function useDeleteFacilityCategory(segment: "benas" | "manufacturing") {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => facilityCategoryApi.remove(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["facility-categories", segment] });
    },
    onError: (error: any) => {
      toast.error(getApiErrorMessage(error, "Failed to remove category."));
    },
  });
}
