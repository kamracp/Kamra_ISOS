import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { getApiErrorMessage } from "../../../utils/apiError";
import { scope3Api, type Scope3Record, type Scope3RecordCreate, type Scope3RecordUpdate, type Scope3Summary } from "../api/scope3Api";

export const SCOPE3_KEY = ["scope3"] as const;

export function useScope3Summary(year: number) {
  return useQuery<Scope3Summary>({ queryKey: [...SCOPE3_KEY, "summary", year], queryFn: () => scope3Api.summary(year), staleTime: 30_000 });
}
export function useScope3Records(year: number, category?: number) {
  return useQuery<Scope3Record[]>({ queryKey: [...SCOPE3_KEY, "records", year, category ?? "all"], queryFn: () => scope3Api.records(year, category), staleTime: 30_000 });
}
function useRecordMutation<V>(fn: (v: V) => Promise<unknown>, okMsg: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: fn,
    onSuccess: () => { toast.success(okMsg); qc.invalidateQueries({ queryKey: SCOPE3_KEY }); },
    onError: (e) => toast.error(getApiErrorMessage(e, "Scope 3 request failed")),
  });
}
export const useCreateScope3Record = () => useRecordMutation((d: Scope3RecordCreate) => scope3Api.create(d), "Record added");
export const useUpdateScope3Record = () => useRecordMutation((v: { id: number; data: Scope3RecordUpdate }) => scope3Api.update(v.id, v.data), "Record updated");
export const useDeleteScope3Record = () => useRecordMutation((id: number) => scope3Api.remove(id), "Record deleted");
