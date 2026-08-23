import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import patEnergyApi, {
  type PatCycleTarget,
  type PatCycleTargetCreate,
  type PatCycleTargetUpdate,
  type PatSummary,
} from "../api/patEnergyApi";
import { getApiErrorMessage } from "../../../utils/apiError";

const TARGETS_KEY = ["pat-cycle-targets"] as const;
const SUMMARY_KEY = ["pat-summary"] as const;

export function usePatCycleTargets(unitId?: number) {
  return useQuery<PatCycleTarget[]>({
    queryKey: [...TARGETS_KEY, unitId ?? "none"],
    queryFn: () => patEnergyApi.getTargets(unitId as number),
    enabled: !!unitId,
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: false,
  });
}

export function useCreatePatCycleTarget() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ unitId, data }: { unitId: number; data: PatCycleTargetCreate }) =>
      patEnergyApi.createTarget(unitId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: TARGETS_KEY });
      queryClient.invalidateQueries({ queryKey: SUMMARY_KEY });
      toast.success("PAT cycle target created successfully.");
    },
    onError: (error: any) => {
      toast.error(getApiErrorMessage(error, "Failed to create PAT cycle target."));
    },
  });
}

export function useUpdatePatCycleTarget() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ targetId, data }: { targetId: number; data: PatCycleTargetUpdate }) =>
      patEnergyApi.updateTarget(targetId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: TARGETS_KEY });
      queryClient.invalidateQueries({ queryKey: SUMMARY_KEY });
      toast.success("PAT cycle target updated successfully.");
    },
    onError: (error: any) => {
      toast.error(getApiErrorMessage(error, "Failed to update PAT cycle target."));
    },
  });
}

export function useDeletePatCycleTarget() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (targetId: number) => patEnergyApi.deleteTarget(targetId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: TARGETS_KEY });
      queryClient.invalidateQueries({ queryKey: SUMMARY_KEY });
      toast.success("PAT cycle target deleted successfully.");
    },
    onError: (error: any) => {
      toast.error(getApiErrorMessage(error, "Failed to delete PAT cycle target."));
    },
  });
}

export function usePatSummary(unitId?: number, year?: number) {
  return useQuery<PatSummary>({
    queryKey: [...SUMMARY_KEY, unitId ?? "none", year ?? "none"],
    queryFn: () => patEnergyApi.getPatSummary(unitId as number, year as number),
    enabled: !!unitId && !!year,
    staleTime: 2 * 60 * 1000,
    refetchOnWindowFocus: false,
  });
}
