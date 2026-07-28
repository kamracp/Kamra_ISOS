import { useQuery } from "@tanstack/react-query";
import esgReportApi, { type BrsrReport } from "../api/esgReportApi";

export function useBrsrPrinciple6(year: number) {
  return useQuery<BrsrReport>({
    queryKey: ["esg-brsr-principle6", year],
    queryFn: () => esgReportApi.getBrsrPrinciple6(year),
    staleTime: 5 * 60 * 1000,
  });
}