import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import humanRightsApi, {
  type ChildFields,
  type ChildKind,
  type HumanRightsRecord,
  type HumanRightsRecordCreate,
  type HumanRightsRecordUpdate,
} from "../api/humanRightsApi";
import { getApiErrorMessage } from "../../../utils/apiError";

const QUERY_KEY = ["human-rights-records"] as const;

function useInvalidatingMutation<TVars>(
  mutationFn: (vars: TVars) => Promise<unknown>,
  successMessage: string,
  errorFallback: string,
) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      toast.success(successMessage);
    },
    onError: (error: unknown) => {
      toast.error(getApiErrorMessage(error, errorFallback));
    },
  });
}

export function useHumanRightsRecords() {
  return useQuery<HumanRightsRecord[]>({
    queryKey: QUERY_KEY,
    queryFn: () => humanRightsApi.getAll(),
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: false,
  });
}

export function useCreateHumanRightsRecord() {
  return useInvalidatingMutation(
    (data: HumanRightsRecordCreate) => humanRightsApi.create(data),
    "Principle 5 record created.", "Failed to create Principle 5 record.",
  );
}
export function useUpdateHumanRightsRecord() {
  return useInvalidatingMutation(
    ({ id, data }: { id: number; data: HumanRightsRecordUpdate }) => humanRightsApi.update(id, data),
    "Principle 5 record updated.", "Failed to update Principle 5 record.",
  );
}
export function useDeleteHumanRightsRecord() {
  return useInvalidatingMutation(
    (id: number) => humanRightsApi.remove(id),
    "Principle 5 record deleted.", "Failed to delete Principle 5 record.",
  );
}

// One set of child hooks serves all three tables; `kind` travels in the vars.
export function useCreateHumanRightsChild() {
  return useInvalidatingMutation(
    ({ kind, recordId, data }: { kind: ChildKind; recordId: number; data: ChildFields }) =>
      humanRightsApi.createChild(kind, recordId, data),
    "Row added.", "Failed to add row.",
  );
}
export function useUpdateHumanRightsChild() {
  return useInvalidatingMutation(
    ({ kind, childId, data }: { kind: ChildKind; childId: number; data: Partial<ChildFields> }) =>
      humanRightsApi.updateChild(kind, childId, data),
    "Row updated.", "Failed to update row.",
  );
}
export function useDeleteHumanRightsChild() {
  return useInvalidatingMutation(
    ({ kind, childId }: { kind: ChildKind; childId: number }) => humanRightsApi.removeChild(kind, childId),
    "Row deleted.", "Failed to delete row.",
  );
}
