import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import {
  brsrProfileApi,
  type BrsrProfile,
  type BrsrProfileUpdate,
  type BrsrCompleteness,
} from "../api/brsrProfileApi";
import { getApiErrorMessage } from "../../../utils/apiError";

const BRSR_PROFILE_KEY = ["brsr-profile"] as const;

export function useBrsrProfile() {
  return useQuery<BrsrProfile | null>({
    queryKey: BRSR_PROFILE_KEY,
    queryFn: () => brsrProfileApi.get(),
    staleTime: 5 * 60 * 1000,
  });
}

export function useBrsrCompleteness() {
  return useQuery<BrsrCompleteness>({
    queryKey: [...BRSR_PROFILE_KEY, "completeness"],
    queryFn: () => brsrProfileApi.getCompleteness(),
    staleTime: 5 * 60 * 1000,
  });
}

export function useSaveBrsrProfile() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: BrsrProfileUpdate) => brsrProfileApi.save(data),
    onSuccess: () => {
      // Both keys must be invalidated: saving the profile changes the
      // completeness figures too, and React Query cannot infer that link.
      queryClient.invalidateQueries({ queryKey: BRSR_PROFILE_KEY });
      toast.success("BRSR Section A saved");
    },
    onError: (error) => {
      toast.error(getApiErrorMessage(error, "Failed to save BRSR profile"));
    },
  });
}
