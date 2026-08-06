import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";

import organizationApi, {
  type Organization,
  type OrganizationCreate,
  type OrganizationUpdate,
} from "../api/organizationApi";
import { getApiErrorMessage } from "../../../utils/apiError";

const QUERY_KEY = ["organizations"] as const;

export function useOrganizations() {
  return useQuery<Organization[]>({
    queryKey: QUERY_KEY,
    queryFn: organizationApi.getAll,
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: false,
  });
}

export function useOrganization(id?: number) {
  return useQuery<Organization>({
    queryKey: [...QUERY_KEY, id],
    queryFn: () => organizationApi.getById(id as number),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
  });
}

export function useCreateOrganization() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: OrganizationCreate) =>
      organizationApi.create(data),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: QUERY_KEY,
      });

      toast.success("Organization created successfully.");
    },

    onError: (error: any) => {
      toast.error(
        getApiErrorMessage(error, "Failed to create organization.")
      );
    },
  });
}

export function useUpdateOrganization() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: number;
      data: OrganizationUpdate;
    }) => organizationApi.update(id, data),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: QUERY_KEY,
      });

      toast.success("Organization updated successfully.");
    },

    onError: (error: any) => {
      toast.error(
        getApiErrorMessage(error, "Failed to update organization.")
      );
    },
  });
}

export function useDeleteOrganization() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) =>
      organizationApi.remove(id),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: QUERY_KEY,
      });

      toast.success("Organization deleted successfully.");
    },

    onError: (error: any) => {
      toast.error(
        getApiErrorMessage(error, "Failed to delete organization.")
      );
    },
  });
}

export function useRefreshOrganizations() {
  const queryClient = useQueryClient();

  return () =>
    queryClient.invalidateQueries({
      queryKey: QUERY_KEY,
    });
}

export function useOrganizationCache() {
  const queryClient = useQueryClient();

  return {
    getAll: () =>
      queryClient.getQueryData<Organization[]>(QUERY_KEY),

    setAll: (organizations: Organization[]) =>
      queryClient.setQueryData(QUERY_KEY, organizations),

    clear: () =>
      queryClient.removeQueries({
        queryKey: QUERY_KEY,
      }),
  };
}