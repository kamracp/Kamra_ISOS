import { useQuery } from "@tanstack/react-query";
import countriesApi, { type Country } from "../api/countriesApi";

export function useCountries() {
  return useQuery<Country[]>({
    queryKey: ["countries"],
    queryFn: () => countriesApi.getAll(),
    staleTime: 60 * 60 * 1000,
  });
}
