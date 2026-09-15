"""Export every organization-scoped row of one org to JSON (for demo_org_import.py).

Usage: python scripts/demo_org_export.py --org-id 13 [--out data/demo/demo_org.json]
Tables are written in FK-dependency order (Base.metadata.sorted_tables) so the
importer can remap ids as it goes. 'organizations' and 'users' are never exported.
"""
import argparse, json, sys
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import app.main  # noqa: F401  (registers all models)
from sqlalchemy import select
from app.database.base import Base
from app.database.session import SessionLocal

SKIP = {"organizations", "users"}


def _j(v):
    if isinstance(v, (date, datetime)): return v.isoformat()
    if isinstance(v, Decimal): return float(v)
    if isinstance(v, Enum): return v.value
    return v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--org-id", type=int, required=True)
    ap.add_argument("--out", default="data/demo/demo_org.json")
    a = ap.parse_args()
    db = SessionLocal()
    out = {"source_org_id": a.org_id, "tables": []}
    for t in Base.metadata.sorted_tables:
        if t.name in SKIP or "organization_id" not in t.c:
            continue
        rows = db.execute(select(t).where(t.c.organization_id == a.org_id).order_by(t.c.id)).mappings().all()
        if not rows:
            continue
        fks = {fk.parent.name: fk.column.table.name for fk in t.foreign_keys}
        out["tables"].append({"name": t.name, "fks": fks, "rows": [{k: _j(v) for k, v in r.items()} for r in rows]})
        print(f"{t.name:40s} {len(rows):3d} rows  fks={fks}")
    ef = Base.metadata.tables["emission_factors"]
    ids = {r[c] for tb in out["tables"] for c, tgt in tb["fks"].items() if tgt == "emission_factors"
           for r in tb["rows"] if r.get(c) is not None}
    out["emission_factor_refs"] = {}
    for r in db.execute(select(ef).where(ef.c.id.in_(ids))).mappings().all() if ids else []:
        out["emission_factor_refs"][str(r["id"])] = {k: _j(r[k]) for k in ("meter_type", "unit", "region", "source_year", "valid_from")}
    print(f"emission factors referenced: {len(out['emission_factor_refs'])}")
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(out, indent=1))
    print(f"\nwrote {a.out}: {len(out['tables'])} tables")


if __name__ == "__main__":
    main()
