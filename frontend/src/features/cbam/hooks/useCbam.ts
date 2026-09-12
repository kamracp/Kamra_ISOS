import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { getApiErrorMessage } from "../../../utils/apiError";
import { cbamApi, type CbamGood, type CbamGoodCreate, type CbamGoodUpdate } from "../api/cbamApi";

export const CBAM_KEY = ["cbam"] as const;

export function useCbamGoods(year?: number) {
  return useQuery<CbamGood[]>({ queryKey: [...CBAM_KEY, "goods", year ?? "all"], queryFn: () => cbamApi.list(year), staleTime: 30_000 });
}

function useGoodMutation<V>(fn: (v: V) => Promise<unknown>, okMsg: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: fn,
    onSuccess: () => {
      toast.success(okMsg);
      qc.invalidateQueries({ queryKey: CBAM_KEY });
      qc.invalidateQueries({ queryKey: ["lca"] });   // SEE reads LCA; keep both fresh
    },
    onError: (e) => toast.error(getApiErrorMessage(e, "CBAM request failed")),
  });
}

export const useCreateGood = () => useGoodMutation((d: CbamGoodCreate) => cbamApi.create(d), "CBAM good created");
export const useUpdateGood = () => useGoodMutation((v: { id: number; data: CbamGoodUpdate }) => cbamApi.update(v.id, v.data), "CBAM good updated");
export const useDeleteGood = () => useGoodMutation((id: number) => cbamApi.remove(id), "CBAM good deleted");

export function useDownloadTemplate() {
  return useMutation({
    mutationFn: async (year: number) => {
      const blob = await cbamApi.downloadTemplate(year);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url; a.download = `CBAM_operator_communication_${year}.xlsx`; a.click();
      URL.revokeObjectURL(url);
    },
    onError: (e) => toast.error(getApiErrorMessage(e, "Template download failed")),
  });
}
