import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import {
  brsrPolicyApi,
  type BrsrPolicyDisclosure,
  type BrsrPolicyDisclosureUpdate,
  type BrsrPolicyCompleteness,
  type PrincipleLabel,
} from "../api/brsrPolicyApi";
import { getApiErrorMessage } from "../../../utils/apiError";

const BRSR_POLICY_KEY = ["brsr-policy"] as const;

export function useBrsrPolicyDisclosures() {
  return useQuery<BrsrPolicyDisclosure[]>({
    queryKey: BRSR_POLICY_KEY,
    queryFn: () => brsrPolicyApi.getAll(),
    staleTime: 5 * 60 * 1000,
  });
}

export function useBrsrPolicyCompleteness() {
  return useQuery<BrsrPolicyCompleteness>({
    queryKey: [...BRSR_POLICY_KEY, "completeness"],
    queryFn: () => brsrPolicyApi.getCompleteness(),
    staleTime: 5 * 60 * 1000,
  });
}

export function usePrincipleLabels() {
  return useQuery<PrincipleLabel[]>({
    queryKey: [...BRSR_POLICY_KEY, "principles"],
    queryFn: () => brsrPolicyApi.getPrinciples(),
    // The nine SEBI names never change within a session.
    staleTime: Infinity,
  });
}

export function useSaveBrsrPolicy() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (disclosures: BrsrPolicyDisclosureUpdate[]) =>
      brsrPolicyApi.save(disclosures),
    onSuccess: () => {
      // Prefix match also refreshes the completeness subkey.
      queryClient.invalidateQueries({ queryKey: BRSR_POLICY_KEY });
      toast.success("BRSR Section B saved");
    },
    onError: (error) => {
      toast.error(getApiErrorMessage(error, "Failed to save BRSR Section B"));
    },
  });
}
