# Deployment History

Record of every production deployment to the Kamra ClimateOS backend
(shared by BENAS and ManufactureOS) on the AWS Lightsail instance
(13.206.51.94). See /docs/ROLLBACK_RUNBOOK.md for rollback steps.

---

## 2026-08-24 — ManufactureOS Phase A/B/C: PAT Energy, Net Zero (unit-scoped), ESG Report verification

**Commits deployed:** `02340a2..947ba25` (9 commits)
- `8dd5a2c` BRSR Filing Validator
- `1364c6e` + `f29a3d4` PAT SEC Energy tracking (course-corrected: removed
  duplicate EnergyProductionRecord, reused existing ProductionRecord +
  sec_calculation_service)
- `47c52f3` PAT Energy frontend
- `8a51e71` + `c43ec95` Net Zero unit-scoped targets/MACC (backend + frontend)
- `947ba25` ESG Report duplicate /trend endpoint cleanup

**Pre-deploy backup:** `/home/ubuntu/benas_backup_20260824_053606.dump`
(117,725 bytes, verified via `pg_restore --list`, 318 objects listed)

**Schema changes:**
- New table `pat_cycle_targets`, auto-created via `Base.metadata.create_all`
  on app import (no manual migration needed -- new table, not new columns
  on an existing one).

**Steps performed:**
1. `git pull origin main` on `/opt/kamra-climateos` -- fast-forward, no conflicts.
2. Verified `python3 -c "from app.main import app"` -- confirmed new table
   auto-created.
3. `sudo systemctl restart kamra-climateos-benas.service` -- active, no errors.
4. `npm install` (node_modules did not exist on prod, first-time install).
5. Built frontend twice via `.env.benas` -> `dist-benas` and
   `.env.manufactureos` -> `dist-manufactureos` (Vite `--outDir`).
6. Backed up both web roots (`/var/www/{benas,manufactureos}...bak_<timestamp>`)
   before overwrite.
7. `rsync -a --delete` both dist folders into their web roots.
8. `sudo nginx -t` -- passed.
9. Verified both domains return HTTP 200, and the new
   `/api/v1/pat-energy/targets/{id}` endpoint returns 401 (not 404) when
   called without a token -- confirms the route is registered and live.

**Unrelated pre-existing bug found and fixed during this deploy:**
Login/organization load broke in production ("Could not load organization")
after the routine backend restart. Root cause: `organizations.employee_count`
and `organizations.annual_revenue_inr` columns existed in the SQLAlchemy
model but were never added to the production table (a gap from an earlier,
unrelated session -- not caused by this deploy's commits). Fixed via:
```sql
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS employee_count INTEGER;
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS annual_revenue_inr NUMERIC(18,2);
```
Verified against the full `Organization` model field list (18/18 columns
now match). Backend restarted again; login confirmed working by the user
in browser immediately after.

**Post-deploy browser verification (both domains, logged in as the real
production org "Kamra Engineering Solutions", code 1904):**
- BENAS (`benas.kamraengineeringsolution.com`): Organization profile page
  loads correctly, Employee Count / Annual Revenue fields visible.
- ManufactureOS (`manufactureos.kamraengineeringsolution.com`):
  - PAT Energy page: manufacturing unit dropdown populated with the real
    unit ("athena natural"), correct empty-state messaging (no data yet
    for this newly-launched feature).
  - Net Zero page: "Manufacturing Unit (optional)" dropdown present on
    both Target and Project forms, defaulting to Organization-wide.
  - ESG Reports page: loads without error, correctly shows 0 tCO2e
    (no production data for this org yet -- expected, not a bug).

**Status:** Deployed and verified working. No rollback needed.
