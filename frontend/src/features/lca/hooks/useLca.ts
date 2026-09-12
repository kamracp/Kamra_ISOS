import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { lcaApi, type LcaProduct, type LcaProductSummary, type LcaProductCreate, type LcaProductUpdate,
  type LcaItemCreate, type LcaItemUpdate, type FuelLibraryEntry, type EmissionFactorOption } from "../api/lcaApi";
import { countriesApi, type Country } from "../../countries/api/countriesApi";
import { getApiErrorMessage } from "../../../utils/apiError";

const LCA_KEY = ["lca"] as const;

export function useLcaProducts() {
  return useQuery<LcaProductSummary[]>({ queryKey: [...LCA_KEY, "products"], queryFn: lcaApi.list, staleTime: 60_000 });
}
export function useLcaProduct(id: number | null) {
  return useQuery<LcaProduct>({ queryKey: [...LCA_KEY, "product", id], queryFn: () => lcaApi.get(id as number), enabled: id !== null });
}
export function useFuelLibrary() {
  return useQuery<FuelLibraryEntry[]>({ queryKey: ["fuel-library"], queryFn: lcaApi.fuelLibrary, staleTime: Infinity });
}
export function useEmissionFactorOptions() {
  return useQuery<EmissionFactorOption[]>({ queryKey: ["emission-factors", "all"], queryFn: lcaApi.emissionFactors, staleTime: 5 * 60_000 });
}
export function useCountryOptions() {
  return useQuery<Country[]>({ queryKey: ["countries"], queryFn: countriesApi.getAll, staleTime: Infinity });
}

function useProductMutation<TVars>(fn: (v: TVars) => Promise<LcaProduct>, okMsg: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: fn,
    onSuccess: (product) => {
      qc.setQueryData([...LCA_KEY, "product", product.id], product);
      qc.invalidateQueries({ queryKey: [...LCA_KEY, "products"] });
      toast.success(okMsg);
    },
    onError: (e) => toast.error(getApiErrorMessage(e, "Request failed")),
  });
}
export const useCreateProduct = () => useProductMutation((d: LcaProductCreate) => lcaApi.create(d), "Product created");
export const useUpdateProduct = () => useProductMutation((v: { id: number; data: LcaProductUpdate }) => lcaApi.update(v.id, v.data), "Product updated");
export const useAddItem = () => useProductMutation((v: { pid: number; data: LcaItemCreate }) => lcaApi.addItem(v.pid, v.data), "Item added");
export const useUpdateItem = () => useProductMutation((v: { pid: number; itemId: number; data: LcaItemUpdate }) => lcaApi.updateItem(v.pid, v.itemId, v.data), "Item updated");

export function useDeleteProduct() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => lcaApi.remove(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: LCA_KEY }); toast.success("Product deleted"); },
    onError: (e) => toast.error(getApiErrorMessage(e, "Delete failed")),
  });
}
export function useDeleteItem() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (v: { pid: number; itemId: number }) => lcaApi.removeItem(v.pid, v.itemId),
    onSuccess: (_r, v) => { qc.invalidateQueries({ queryKey: [...LCA_KEY, "product", v.pid] }); qc.invalidateQueries({ queryKey: [...LCA_KEY, "products"] }); toast.success("Item removed"); },
    onError: (e) => toast.error(getApiErrorMessage(e, "Delete failed")),
  });
}
export function useDownloadPdf() {
  return useMutation({
    mutationFn: (v: { pid: number; name: string }) => lcaApi.downloadPdf(v.pid, v.name),
    onSuccess: () => toast.success("PLCA report PDF downloaded"),
    onError: (e) => toast.error(getApiErrorMessage(e, "PDF export failed")),
  });
}

export function useDownloadOpenLca() {
  return useMutation({
    mutationFn: (v: { pid: number; name: string }) => lcaApi.downloadOpenLca(v.pid, v.name),
    onSuccess: () => toast.success("openLCA JSON-LD zip downloaded"),
    onError: (e) => toast.error(getApiErrorMessage(e, "Export failed")),
  });
}
