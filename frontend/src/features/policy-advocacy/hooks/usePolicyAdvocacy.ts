import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import policyAdvocacyApi, {
  type PolicyAdvocacyRecord,
  type PolicyAdvocacyRecordCreate,
  type PolicyAdvocacyRecordUpdate,
  type TradeAssociationCreate,
  type TradeAssociationUpdate,
} from "../api/policyAdvocacyApi";
import { getApiErrorMessage } from "../../../utils/apiError";

const QUERY_KEY = ["policy-advocacy-records"] as const;

export function usePolicyAdvocacyRecords() {
  return useQuery<PolicyAdvocacyRecord[]>({
    queryKey: QUERY_KEY,
    queryFn: () => policyAdvocacyApi.getAll(),
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: false,
  });
}

export function useCreatePolicyAdvocacyRecord() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: PolicyAdvocacyRecordCreate) => policyAdvocacyApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      toast.success("Policy advocacy record created successfully.");
    },
    onError: (error: any) => {
      toast.error(getApiErrorMessage(error, "Failed to create policy advocacy record."));
    },
  });
}

export function useUpdatePolicyAdvocacyRecord() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: PolicyAdvocacyRecordUpdate }) =>
      policyAdvocacyApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      toast.success("Policy advocacy record updated successfully.");
    },
    onError: (error: any) => {
      toast.error(getApiErrorMessage(error, "Failed to update policy advocacy record."));
    },
  });
}

export function useDeletePolicyAdvocacyRecord() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => policyAdvocacyApi.remove(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      toast.success("Policy advocacy record deleted successfully.");
    },
    onError: (error: any) => {
      toast.error(getApiErrorMessage(error, "Failed to delete policy advocacy record."));
    },
  });
}

export function useCreateTradeAssociation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ recordId, data }: { recordId: number; data: TradeAssociationCreate }) =>
      policyAdvocacyApi.createAssociation(recordId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      toast.success("Trade association added successfully.");
    },
    onError: (error: any) => {
      toast.error(getApiErrorMessage(error, "Failed to add trade association."));
    },
  });
}

export function useUpdateTradeAssociation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ associationId, data }: { associationId: number; data: TradeAssociationUpdate }) =>
      policyAdvocacyApi.updateAssociation(associationId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      toast.success("Trade association updated successfully.");
    },
    onError: (error: any) => {
      toast.error(getApiErrorMessage(error, "Failed to update trade association."));
    },
  });
}

export function useDeleteTradeAssociation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (associationId: number) => policyAdvocacyApi.removeAssociation(associationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      toast.success("Trade association deleted successfully.");
    },
    onError: (error: any) => {
      toast.error(getApiErrorMessage(error, "Failed to delete trade association."));
    },
  });
}
