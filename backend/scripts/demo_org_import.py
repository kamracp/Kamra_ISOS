"""Import a demo_org_export.py JSON into a target organization, remapping ids.

Usage:
  python scripts/demo_org_import.py --org-id 1 [--file data/demo/demo_org.json] [--commit]
  python scripts/demo_org_import.py --clone-org-from 13 --new-org-code DEMO2 --new-org-name "Demo Clone" --commit

Dry-run by default (rolled back). Tables already populated for the target org
are skipped; FKs are remapped through ids created in this run (unresolvable
NOT NULL FK -> row skipped); emission_factor_id is re-resolved by natural key.
"""
import argparse, json, sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import app.main  # noqa: F401
import sqlalchemy as sa
from sqlalchemy import select, insert, func
from app.database.base import Base
from app.database.session import SessionLocal


def _coerce(col, v):
    if v is None:
        return None
    t = col.type
    if isinstance(t, sa.Enum) and getattr(t, "enum_class", None):
        for m in t.enum_class:
            if m.value == v or m.name == v:
                return m
        raise ValueError(f"{col.table.name}.{col.name}: no enum member for {v!r}")
    if isinstance(t, sa.DateTime):
        return datetime.fromisoformat(v)
    if isinstance(t, sa.Date):
        return date.fromisoformat(v)
    return v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default="data/demo/demo_org.json")
    ap.add_argument("--org-id", type=int)
    ap.add_argument("--clone-org-from", type=int)
    ap.add_argument("--new-org-code")
    ap.add_argument("--new-org-name")
    ap.add_argument("--commit", action="store_true")
    ap.add_argument("--code-suffix", default="", help="appended to string columns that carry a GLOBAL unique index (e.g. building_code)")
    a = ap.parse_args()
    data = json.loads(Path(a.file).read_text())
    db = SessionLocal()
    T = Base.metadata.tables

    if a.clone_org_from:
        org = T["organizations"]
        src = db.execute(select(org).where(org.c.id == a.clone_org_from)).mappings().one()
        row = {k: v for k, v in src.items() if k not in ("id", "created_at", "updated_at")}
        row.update(organization_code=a.new_org_code, organization_name=a.new_org_name, legal_name=a.new_org_name)
        target = db.execute(insert(org).values(**row).returning(org.c.id)).scalar_one()
        print(f"created organization id={target} ({a.new_org_code})")
    else:
        target = a.org_id
        n = db.execute(select(func.count()).select_from(T["organizations"]).where(T["organizations"].c.id == target)).scalar()
        assert target and n == 1, "target org missing"

    ef = T["emission_factors"]
    ef_map = {}
    for old_id, key in data.get("emission_factor_refs", {}).items():
        q = select(ef.c.id).where(ef.c.meter_type == key["meter_type"], ef.c.unit == key["unit"], ef.c.region == key["region"])
        if key.get("source_year") is not None: q = q.where(ef.c.source_year == key["source_year"])
        if key.get("valid_from"): q = q.where(ef.c.valid_from == date.fromisoformat(key["valid_from"]))
        hit = db.execute(q.order_by(ef.c.id)).scalars().first()
        ef_map[int(old_id)] = hit
        if hit is None: print(f"  WARN emission factor {old_id} {key} not found on target -> NULL")

    idmap = {"emission_factors": ef_map}
    stats = []
    for tb in data["tables"]:
        t = T[tb["name"]]
        idmap.setdefault(tb["name"], {})
        existing = db.execute(select(func.count()).select_from(t).where(t.c.organization_id == target)).scalar()
        if existing:
            stats.append((tb["name"], len(tb["rows"]), 0, f"SKIPPED: target org already has {existing} rows")); continue
        # Columns under a single-column unique index/constraint -> suffix to avoid cross-org collisions.
        # Reflected from the live DB (models and DB have drifted on some indexes).
        insp = sa.inspect(db.get_bind())
        uniq = {ix["column_names"][0] for ix in insp.get_indexes(t.name) if ix.get("unique") and len(ix["column_names"]) == 1}
        uniq |= {uc["column_names"][0] for uc in insp.get_unique_constraints(t.name) if len(uc["column_names"]) == 1}
        if a.code_suffix and uniq: print(f"  {t.name}: suffixing {sorted(uniq)}")
        done = skipped = 0
        for r in tb["rows"]:
            row, drop = {}, False
            for k, v in r.items():
                if k in ("id", "created_at", "updated_at"): continue
                col = t.c[k]
                if k == "organization_id":
                    row[k] = target; continue
                if k in tb["fks"]:
                    v = idmap.get(tb["fks"][k], {}).get(v) if v is not None else None
                    if v is None and not col.nullable:
                        drop = True; break
                v = _coerce(col, v)
                if a.code_suffix and k in uniq and isinstance(v, str) and k != "organization_id":
                    v = v + a.code_suffix
                row[k] = v
            if drop:
                skipped += 1; continue
            idmap[tb["name"]][r["id"]] = db.execute(insert(t).values(**row).returning(t.c.id)).scalar_one()
            done += 1
        stats.append((tb["name"], len(tb["rows"]), done, f"{skipped} skipped (unresolvable NOT NULL FK)" if skipped else ""))

    for name, n, done, note in stats:
        print(f"{name:40s} {done:3d}/{n:<3d} {note}")
    if a.commit:
        db.commit(); print(f"\nCOMMITTED into organization {target}")
    else:
        db.rollback(); print(f"\nDRY RUN (rolled back). Re-run with --commit to write into organization {target}")


if __name__ == "__main__":
    main()
