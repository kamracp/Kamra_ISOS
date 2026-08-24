import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import csrApi, {
  type CsrRecord,
  type CsrRecordCreate,
  type CsrRecordUpdate,
  type CsrProjectCreate,
  type CsrProjectUpdate,
} from "../api/csrApi";
import { getApiErrorMessage } from "../../../utils/apiError";

const QUERY_KEY = ["csr-records"] as const;

export function useCsrRecords() {
  return useQuery<CsrRecord[]>({
    queryKey: QUERY_KEY,
    queryFn: () => csrApi.getAll(),
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: false,
  });
}

export function useCreateCsrRecord() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CsrRecordCreate) => csrApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      toast.success("CSR record created successfully.");
    },
    onError: (error: any) => {
      toast.error(getApiErrorMessage(error, "Failed to create CSR record."));
    },
  });
}

export function useUpdateCsrRecord() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: CsrRecordUpdate }) =>
      csrApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      toast.success("CSR record updated successfully.");
    },
    onError: (error: any) => {
      toast.error(getApiErrorMessage(error, "Failed to update CSR record."));
    },
  });
}

export function useDeleteCsrRecord() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => csrApi.remove(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      toast.success("CSR record deleted successfully.");
    },
    onError: (error: any) => {
      toast.error(getApiErrorMessage(error, "Failed to delete CSR record."));
    },
  });
}

export function useCreateCsrProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ recordId, data }: { recordId: number; data: CsrProjectCreate }) =>
      csrApi.createProject(recordId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      toast.success("CSR project added successfully.");
    },
    onError: (error: any) => {
      toast.error(getApiErrorMessage(error, "Failed to add CSR project."));
    },
  });
}

export function useUpdateCsrProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ projectId, data }: { projectId: number; data: CsrProjectUpdate }) =>
      csrApi.updateProject(projectId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      toast.success("CSR project updated successfully.");
    },
    onError: (error: any) => {
      toast.error(getApiErrorMessage(error, "Failed to update CSR project."));
    },
  });
}

export function useDeleteCsrProject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (projectId: number) => csrApi.removeProject(projectId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      toast.success("CSR project deleted successfully.");
    },
    onError: (error: any) => {
      toast.error(getApiErrorMessage(error, "Failed to delete CSR project."));
    },
  });
}
