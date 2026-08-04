import { useQuery } from "@tanstack/react-query";
import esgReportApi, {
  type EsgReport,
  type ReportFramework,
} from "../api/esgReportApi";

export function useEsgReport(framework: ReportFramework, year: number) {
  return useQuery<EsgReport>({
    queryKey: ["esg-report", framework, year],
    queryFn: () => esgReportApi.getReport(framework, year),
    staleTime: 5 * 60 * 1000,
  });
}

// Kept for backward compatibility with any existing caller.
export function useBrsrPrinciple6(year: number) {
  return useEsgReport("brsr", year);
}