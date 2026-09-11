"""Seed emission_factors with DEFRA 2026 Material use (Primary material production) rows. Usage: python scripts/seed_defra_materials.py [--dry]"""
import re, sys, psycopg2
from openpyxl import load_workbook
DB = "dbname=benas user=postgres password=postgres host=127.0.0.1"
SRC = "UK Government GHG Conversion Factors for Company Reporting 2026 (DESNZ/DEFRA)"
STRIP = ["metal: ", "plastics: ", "(incl. forming)", "(excl. forming)"]
def slug(name):
    s = name.lower()
    for p in STRIP: s = s.replace(p, "")
    return ("mat_" + re.sub(r"[^a-z0-9]+", "_", s).strip("_"))[:50]
ws = load_workbook("data/defra/defra-2026-flat.xlsx", read_only=True, data_only=True)["Factors by Category"]
rows = list(ws.iter_rows(min_row=6, values_only=True))
h = [str(x).strip() if x else "" for x in rows[0]]; c = {n: h.index(n) for n in h if n}
items = []
for r in rows[1:]:
    if r and r[c["Level 1"]] == "Material use" and str(r[c["Column Text"]]).startswith("Primary") and r[c["GHG Conversion Factor 2026"]] is not None:
        ref = f"Material use > {r[c['Level 2']]} > {r[c['Level 3']]}, Primary material production, DEFRA ID {r[c['ID']]}, kgCO2e per tonne, flat file v1.2 (revised 31 Jul 2026)"
        items.append((slug(r[c["Level 3"]]), float(r[c["GHG Conversion Factor 2026"]]), ref))
print(f"{len(items)} DEFRA primary material factors read")
conn = psycopg2.connect(DB); cur = conn.cursor(); ins = skip = 0
for mt, f, ref in items:
    cur.execute("SELECT 1 FROM emission_factors WHERE meter_type=%s AND source_year=2026", (mt,))
    if cur.fetchone(): skip += 1; continue
    print(f"  {mt:40s} {f:>12.5f} kgCO2e/tonne")
    if "--dry" not in sys.argv:
        cur.execute("INSERT INTO emission_factors (meter_type, unit, factor_kgco2e_per_unit, region, source, source_year, document_reference, valid_from, is_active, notes) VALUES (%s,'tonne',%s,'UK',%s,2026,%s,'2026-01-01',true,%s)",
                    (mt, f, SRC, ref, "Cradle-to-gate (A1) material production factor, UK basis; proxy for LCA inventory where no India-specific factor exists"))
    ins += 1
conn.commit(); print(f"inserted={ins} skipped={skip} dry={'--dry' in sys.argv}")
