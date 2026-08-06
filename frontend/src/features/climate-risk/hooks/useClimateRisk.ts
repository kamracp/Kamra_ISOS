import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";

import {
  climateRiskApi,
  type ClimateRisk,
  type ClimateRiskCreate,
  type ClimateRiskSummary,
} from "../api/climateRiskApi";
import { getApiErrorMessage } from "../../../utils/apiError";

const RISK_KEY = ["climate-risks"] as const;

export function useClimateRisks() {
  return useQuery<ClimateRisk[]>({
    queryKey: RISK_KEY,
    queryFn: () => climateRiskApi.getAll(),
    staleTime: 5 * 60 * 1000,
  });
}

export function useClimateRiskSummary() {
  return useQuery<ClimateRiskSummary>({
    queryKey: [...RISK_KEY, "summary"],
    queryFn: () => climateRiskApi.getSummary(),
    staleTime: 2 * 60 * 1000,
  });
}

export function useCreateClimateRisk() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ClimateRiskCreate) => climateRiskApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: RISK_KEY });
      toast.success("Climate risk added.");
    },
    onError: (error: any) => {
      toast.error(getApiErrorMessage(error, "Failed to add climate risk."));
    },
  });
}

export function useDeleteClimateRisk() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => climateRiskApi.remove(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: RISK_KEY });
      toast.success("Climate risk removed.");
    },
    onError: (error: any) => {
      toast.error(getApiErrorMessage(error, "Failed to remove climate risk."));
    },
  });
}
