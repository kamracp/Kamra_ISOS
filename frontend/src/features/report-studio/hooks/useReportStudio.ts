import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import {
  reportStudioApi,
  type NarrativeCompleteness,
  type ReportNarrative,
  type ReportNarrativeUpdate,
  type SdgLabel,
} from "../api/reportStudioApi";
import { getApiErrorMessage } from "../../../utils/apiError";

const KEY = ["report-studio"] as const;

// year is part of the key: switching year must never show another year's text.
export function useReportNarrative(year: number) {
  return useQuery<ReportNarrative | null>({
    queryKey: [...KEY, "narrative", year],
    queryFn: () => reportStudioApi.getNarrative(year),
    staleTime: 5 * 60 * 1000,
  });
}

export function useNarrativeCompleteness(year: number) {
  return useQuery<NarrativeCompleteness>({
    queryKey: [...KEY, "completeness", year],
    queryFn: () => reportStudioApi.getCompleteness(year),
    staleTime: 5 * 60 * 1000,
  });
}

export function useNarrativeYears() {
  return useQuery<number[]>({
    queryKey: [...KEY, "years"],
    queryFn: () => reportStudioApi.getYears(),
    staleTime: 5 * 60 * 1000,
  });
}

export function useSdgLabels() {
  return useQuery<SdgLabel[]>({
    queryKey: [...KEY, "sdgs"],
    queryFn: () => reportStudioApi.getSdgs(),
    staleTime: Infinity, // static list
  });
}

export function useSaveNarrative(year: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: ReportNarrativeUpdate) => reportStudioApi.saveNarrative(year, payload),
    onSuccess: () => {
      // Prefix match invalidates narrative + completeness + years together.
      qc.invalidateQueries({ queryKey: KEY });
      toast.success("Report narrative saved");
    },
    onError: (err) => toast.error(getApiErrorMessage(err, "Could not save narrative")),
  });
}

export function useDownloadCompletePdf() {
  return useMutation({
    mutationFn: (year: number) => reportStudioApi.downloadCompletePdf(year),
    onError: (err) => toast.error(getApiErrorMessage(err, "Could not download the PDF")),
  });
}
