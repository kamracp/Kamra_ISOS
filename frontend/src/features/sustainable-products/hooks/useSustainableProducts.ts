import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import sustainableProductsApi, {
  type SustainableProductRecord,
  type SustainableProductRecordCreate,
  type SustainableProductRecordUpdate,
  type ReclaimedMaterialCreate,
  type ReclaimedMaterialUpdate,
} from "../api/sustainableProductsApi";
import { getApiErrorMessage } from "../../../utils/apiError";

const QUERY_KEY = ["sustainable-product-records"] as const;

// One helper builds every mutation: same invalidate + toast shape as the
// other BRSR features, without seven hand-copied blocks to keep in sync.
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

export function useSustainableProductRecords() {
  return useQuery<SustainableProductRecord[]>({
    queryKey: QUERY_KEY,
    queryFn: () => sustainableProductsApi.getAll(),
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: false,
  });
}

export function useCreateSustainableProductRecord() {
  return useInvalidatingMutation(
    (data: SustainableProductRecordCreate) => sustainableProductsApi.create(data),
    "Principle 2 record created.",
    "Failed to create Principle 2 record.",
  );
}

export function useUpdateSustainableProductRecord() {
  return useInvalidatingMutation(
    ({ id, data }: { id: number; data: SustainableProductRecordUpdate }) =>
      sustainableProductsApi.update(id, data),
    "Principle 2 record updated.",
    "Failed to update Principle 2 record.",
  );
}

export function useDeleteSustainableProductRecord() {
  return useInvalidatingMutation(
    (id: number) => sustainableProductsApi.remove(id),
    "Principle 2 record deleted.",
    "Failed to delete Principle 2 record.",
  );
}

export function useCreateReclaimedMaterial() {
  return useInvalidatingMutation(
    ({ recordId, data }: { recordId: number; data: ReclaimedMaterialCreate }) =>
      sustainableProductsApi.createMaterial(recordId, data),
    "Reclaimed material row added.",
    "Failed to add reclaimed material row.",
  );
}

export function useUpdateReclaimedMaterial() {
  return useInvalidatingMutation(
    ({ materialId, data }: { materialId: number; data: ReclaimedMaterialUpdate }) =>
      sustainableProductsApi.updateMaterial(materialId, data),
    "Reclaimed material row updated.",
    "Failed to update reclaimed material row.",
  );
}

export function useDeleteReclaimedMaterial() {
  return useInvalidatingMutation(
    (materialId: number) => sustainableProductsApi.removeMaterial(materialId),
    "Reclaimed material row deleted.",
    "Failed to delete reclaimed material row.",
  );
}
