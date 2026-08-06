import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import {
  netZeroTargetApi,
  decarbonizationProjectApi,
  type NetZeroTarget,
  type NetZeroTargetCreate,
  type NetZeroSummary,
  type DecarbonizationProject,
  type DecarbonizationProjectCreate,
} from "../api/netZeroApi";
import { getApiErrorMessage } from "../../../utils/apiError";

const TARGET_KEY = ["net-zero-targets"] as const;
const PROJECT_KEY = ["decarbonization-projects"] as const;

export function useNetZeroTargets() {
  return useQuery<NetZeroTarget[]>({
    queryKey: TARGET_KEY,
    queryFn: () => netZeroTargetApi.getAll(),
    staleTime: 5 * 60 * 1000,
  });
}

export function useNetZeroSummary(targetId?: number) {
  return useQuery<NetZeroSummary>({
    queryKey: [...TARGET_KEY, "summary", targetId],
    queryFn: () => netZeroTargetApi.getSummary(targetId as number),
    enabled: !!targetId,
    staleTime: 2 * 60 * 1000,
  });
}

export function useCreateNetZeroTarget() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: NetZeroTargetCreate) => netZeroTargetApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: TARGET_KEY });
      toast.success("Net Zero target created.");
    },
    onError: (error: any) => {
      toast.error(getApiErrorMessage(error, "Failed to create target."));
    },
  });
}

export function useDeleteNetZeroTarget() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => netZeroTargetApi.remove(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: TARGET_KEY });
      toast.success("Net Zero target deleted.");
    },
    onError: (error: any) => {
      toast.error(getApiErrorMessage(error, "Failed to delete target."));
    },
  });
}

export function useDecarbonizationProjects() {
  return useQuery<DecarbonizationProject[]>({
    queryKey: PROJECT_KEY,
    queryFn: () => decarbonizationProjectApi.getAll(),
    staleTime: 5 * 60 * 1000,
  });
}

export function useCreateDecarbonizationProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: DecarbonizationProjectCreate) => decarbonizationProjectApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: PROJECT_KEY });
      queryClient.invalidateQueries({ queryKey: TARGET_KEY });
      toast.success("Project added.");
    },
    onError: (error: any) => {
      toast.error(getApiErrorMessage(error, "Failed to add project."));
    },
  });
}

export function useDeleteDecarbonizationProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => decarbonizationProjectApi.remove(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: PROJECT_KEY });
      queryClient.invalidateQueries({ queryKey: TARGET_KEY });
      toast.success("Project removed.");
    },
    onError: (error: any) => {
      toast.error(getApiErrorMessage(error, "Failed to remove project."));
    },
  });
}
