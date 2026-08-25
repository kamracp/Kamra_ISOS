import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import stakeholderEngagementApi, {
  type StakeholderEngagementRecord,
  type StakeholderEngagementRecordCreate,
  type StakeholderEngagementRecordUpdate,
  type StakeholderGroupCreate,
  type StakeholderGroupUpdate,
} from "../api/stakeholderEngagementApi";
import { getApiErrorMessage } from "../../../utils/apiError";

const QUERY_KEY = ["stakeholder-engagement-records"] as const;

export function useStakeholderEngagementRecords() {
  return useQuery<StakeholderEngagementRecord[]>({
    queryKey: QUERY_KEY,
    queryFn: () => stakeholderEngagementApi.getAll(),
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: false,
  });
}

export function useCreateStakeholderEngagementRecord() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: StakeholderEngagementRecordCreate) => stakeholderEngagementApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      toast.success("Stakeholder engagement record created successfully.");
    },
    onError: (error: any) => {
      toast.error(getApiErrorMessage(error, "Failed to create stakeholder engagement record."));
    },
  });
}

export function useUpdateStakeholderEngagementRecord() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: StakeholderEngagementRecordUpdate }) =>
      stakeholderEngagementApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      toast.success("Stakeholder engagement record updated successfully.");
    },
    onError: (error: any) => {
      toast.error(getApiErrorMessage(error, "Failed to update stakeholder engagement record."));
    },
  });
}

export function useDeleteStakeholderEngagementRecord() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => stakeholderEngagementApi.remove(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      toast.success("Stakeholder engagement record deleted successfully.");
    },
    onError: (error: any) => {
      toast.error(getApiErrorMessage(error, "Failed to delete stakeholder engagement record."));
    },
  });
}

export function useCreateStakeholderGroup() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ recordId, data }: { recordId: number; data: StakeholderGroupCreate }) =>
      stakeholderEngagementApi.createGroup(recordId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      toast.success("Stakeholder group added successfully.");
    },
    onError: (error: any) => {
      toast.error(getApiErrorMessage(error, "Failed to add stakeholder group."));
    },
  });
}

export function useUpdateStakeholderGroup() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ groupId, data }: { groupId: number; data: StakeholderGroupUpdate }) =>
      stakeholderEngagementApi.updateGroup(groupId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      toast.success("Stakeholder group updated successfully.");
    },
    onError: (error: any) => {
      toast.error(getApiErrorMessage(error, "Failed to update stakeholder group."));
    },
  });
}

export function useDeleteStakeholderGroup() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (groupId: number) => stakeholderEngagementApi.removeGroup(groupId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      toast.success("Stakeholder group deleted successfully.");
    },
    onError: (error: any) => {
      toast.error(getApiErrorMessage(error, "Failed to delete stakeholder group."));
    },
  });
}
