import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import api, { type ManufacturingFuelRecordCreate, type ManufacturingFuelRecordUpdate } from "../api/manufacturingFuelsApi";
import { getApiErrorMessage } from "../../../utils/apiError";

const QUERY_KEY = ["manufacturing-fuel-records"] as const;

function useInvalidatingMutation<TVars>(mutationFn: (v: TVars) => Promise<unknown>, ok: string, fail: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn,
    onSuccess: () => {
      // Energy balance and PAT SEC read the same records -- refresh them too.
      qc.invalidateQueries({ queryKey: QUERY_KEY });
      qc.invalidateQueries({ queryKey: ["pat-energy"] });
      toast.success(ok);
    },
    onError: (error: unknown) => { toast.error(getApiErrorMessage(error, fail)); },
  });
}

export function useFuelLibrary() {
  return useQuery({ queryKey: ["fuel-library"], queryFn: () => api.library(), staleTime: Infinity });
}
export function useManufacturingFuelRecords(year?: number) {
  return useQuery({ queryKey: [...QUERY_KEY, year], queryFn: () => api.getAll(year), staleTime: 5 * 60 * 1000, refetchOnWindowFocus: false });
}
export const useCreateManufacturingFuelRecord = () =>
  useInvalidatingMutation((d: ManufacturingFuelRecordCreate) => api.create(d), "Fuel record created.", "Failed to create fuel record.");
export const useUpdateManufacturingFuelRecord = () =>
  useInvalidatingMutation(({ id, data }: { id: number; data: ManufacturingFuelRecordUpdate }) => api.update(id, data), "Fuel record updated.", "Failed to update fuel record.");
export const useDeleteManufacturingFuelRecord = () =>
  useInvalidatingMutation((id: number) => api.remove(id), "Fuel record deleted.", "Failed to delete fuel record.");
