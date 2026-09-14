import { useQuery } from "@tanstack/react-query";
import { carbonApi } from "../api/carbonApi";

export function useCarbonSummary(year?: number) {
  return useQuery({
    queryKey: ["carbon-summary", year ?? "all"],
    queryFn: () => carbonApi.getSummary(year),
  });
}
