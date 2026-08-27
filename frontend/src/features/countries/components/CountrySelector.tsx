import { useCountries } from "../hooks/useCountries";
import type { Country, Region } from "../api/countriesApi";

interface CountrySelectorProps {
  value: string;
  onChange: (code: string) => void;
  label?: string;
}

const REGION_LABELS: Record<Region, string> = {
  india: "India",
  asia: "Asia",
  middle_east: "Middle East",
  europe: "Europe",
  north_america: "North America",
  oceania: "Oceania",
};

const REGION_ORDER: Region[] = ["india", "asia", "middle_east", "europe", "north_america", "oceania"];

export default function CountrySelector({ value, onChange, label }: CountrySelectorProps) {
  const { data: countries, isLoading } = useCountries();

  if (isLoading) return <div className="text-sm text-gray-500">Loading countries...</div>;
  if (!countries) return null;

  const byRegion: Record<Region, Country[]> = {
    india: [], asia: [], middle_east: [], europe: [], north_america: [], oceania: [],
  };
  countries.forEach((c) => {
    if (!byRegion[c.region]) byRegion[c.region] = [];
    byRegion[c.region].push(c);
  });

  return (
    <div className="flex flex-col gap-1">
      {label && <label className="text-sm font-medium text-gray-700">{label}</label>}
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <option value="">Select a country...</option>
        {REGION_ORDER.map((region) =>
          byRegion[region].length > 0 ? (
            <optgroup key={region} label={REGION_LABELS[region]}>
              {byRegion[region].map((c) => (
                <option key={c.code} value={c.code}>
                  {c.name}
                  {c.needs_verification ? "  (\u26a0 factor pending)" : ""}
                </option>
              ))}
            </optgroup>
          ) : null
        )}
      </select>
    </div>
  );
}
