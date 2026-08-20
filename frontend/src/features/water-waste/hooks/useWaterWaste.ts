import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import {
  waterWasteApi,
  type WaterRecord,
  type WaterRecordCreate,
  type WasteRecord,
  type WasteRecordCreate,
  type WaterRecordUpdate,
  type WasteRecordUpdate,
  type WaterWasteSummary,
} from "../api/waterWasteApi";
import { getApiErrorMessage } from "../../../utils/apiError";

const WATER_WASTE_KEY = ["water-waste"] as const;

export function useWaterWasteSummary(year?: number) {
  return useQuery<WaterWasteSummary>({
    queryKey: [...WATER_WASTE_KEY, "summary", year ?? "all"],
    queryFn: () => waterWasteApi.getSummary(year),
    staleTime: 5 * 60 * 1000,
  });
}

export function useWaterRecords(year?: number) {
  return useQuery<WaterRecord[]>({
    queryKey: [...WATER_WASTE_KEY, "water", year ?? "all"],
    queryFn: () => waterWasteApi.getWater(year),
    staleTime: 5 * 60 * 1000,
  });
}

export function useWasteRecords(year?: number) {
  return useQuery<WasteRecord[]>({
    queryKey: [...WATER_WASTE_KEY, "waste", year ?? "all"],
    queryFn: () => waterWasteApi.getWaste(year),
    staleTime: 5 * 60 * 1000,
  });
}

export function useCreateWaterRecord() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: WaterRecordCreate) => waterWasteApi.createWater(data),
    onSuccess: () => {
      // Prefix match refreshes the list AND the summary, which is derived
      // from the same records.
      queryClient.invalidateQueries({ queryKey: WATER_WASTE_KEY });
      toast.success("Water record saved");
    },
    onError: (error) =>
      toast.error(getApiErrorMessage(error, "Failed to save water record")),
  });
}

export function useUpdateWaterRecord() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: WaterRecordUpdate }) =>
      waterWasteApi.updateWater(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: WATER_WASTE_KEY });
      toast.success("Water record updated");
    },
    onError: (error) =>
      toast.error(getApiErrorMessage(error, "Failed to update water record")),
  });
}

export function useUpdateWasteRecord() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: WasteRecordUpdate }) =>
      waterWasteApi.updateWaste(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: WATER_WASTE_KEY });
      toast.success("Waste record updated");
    },
    onError: (error) =>
      toast.error(getApiErrorMessage(error, "Failed to update waste record")),
  });
}

export function useDeleteWaterRecord() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => waterWasteApi.removeWater(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: WATER_WASTE_KEY });
      toast.success("Water record deleted");
    },
    onError: (error) =>
      toast.error(getApiErrorMessage(error, "Failed to delete water record")),
  });
}

export function useCreateWasteRecord() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: WasteRecordCreate) => waterWasteApi.createWaste(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: WATER_WASTE_KEY });
      toast.success("Waste record saved");
    },
    onError: (error) =>
      toast.error(getApiErrorMessage(error, "Failed to save waste record")),
  });
}

export function useDeleteWasteRecord() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => waterWasteApi.removeWaste(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: WATER_WASTE_KEY });
      toast.success("Waste record deleted");
    },
    onError: (error) =>
      toast.error(getApiErrorMessage(error, "Failed to delete waste record")),
  });
}
