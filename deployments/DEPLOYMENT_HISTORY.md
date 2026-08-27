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

---

## 2026-08-24 (later) — BRSR Principle 8 (CSR) production deploy

**Commits deployed:** `947ba25..da0dc5d`
- `fb03960` CSR backend (CsrRecord + CsrProject, full CRUD, derived percent-spent/total-project-spend)
- `b3d1149` CSR frontend (CsrPage, forms, sidebar/router entries)
- `da0dc5d` CSR wired into BRSR Principle 8 ESG report section

**Pre-deploy backup:** `/home/ubuntu/benas_backup_pre_csr_20260824_174723.dump`
(122,977 bytes, verified via `pg_restore --list`, 331 objects listed)

**Note:** production repo had uncommitted dist-* changes from the prior
manual deploy session (never committed back) -- discarded via
`git checkout -- .` + `git clean -fd` before pulling, since fresh
builds were being made anyway.

**Schema changes:** new tables `csr_records` + `csr_projects`,
auto-created via `Base.metadata.create_all` on app import (no manual
migration -- new tables, not new columns).

**Steps:** git pull (fast-forward, no conflicts) -> verified app import
created both tables -> restarted backend service -> built both frontend
targets (.env.benas -> dist-benas, .env.manufactureos -> dist-manufactureos)
-> backed up both web roots -> rsync deployed -> verified HTTPS 200 on
both domains and 401 (not 404) on `/api/v1/csr-records/`.

**Post-deploy browser verification:** logged into BENAS, created a real
CSR record for 2025 (budget 20,00,000, spent 18,50,000 -> correctly
showed 92.50%) with one project (Community Health Camp, Health,
Bhilwara Rajasthan, 800 beneficiaries) -- Total Project Spend correctly
matched the project's own amount, confirming the derivation logic works
identically in production. Kept as demo data.

**Status:** Deployed and verified working. No rollback needed.

---

## 2026-08-25 — BRSR Principle 1 (Ethics) production deploy

**Commits deployed:** fa90a18..666369e
- Ethics backend (EthicsRecord model, full CRUD, derived training-coverage percentages)
- Ethics frontend (EthicsPage, sidebar/router entries)
- generate_brsr_principle1() wired into ESG report, new endpoint GET /esg-reports/brsr-principle1

**Pre-deploy backup:** /home/ubuntu/benas_backup_pre_p1_25aug26.dump (130,311 bytes)

**Note:** production repo had uncommitted DEPLOYMENT_HISTORY.md changes and stray
dist-* artifacts from the prior manual deploy session (never committed back) --
discarded via git checkout -- . + git clean -fd before pulling, since fresh
builds were being made anyway. Verified via diff first that nothing new was
being lost (it was the already-committed CSR entry).

**Schema changes:** new table ethics_records, auto-created via
Base.metadata.create_all on app import (no manual migration -- new table,
not new columns). Confirmed via \d ethics_records post-restart.

**Steps:** pg_dump backup -> git checkout/clean -> git pull (fa90a18..666369e)
-> restart backend service (confirmed ethics_records table created in logs
and via psql) -> built both frontend targets (.env.benas -> dist-benas,
.env.manufactureos -> dist-manufactureos) -> rsync deployed both -> verified
401 (not 404) on /api/v1/esg-reports/brsr-principle1 and 200 on both domains.

**Status:** Deployed and verified working. No rollback needed.

---

## 2026-08-25 — BRSR Principle 1 (Ethics) production deploy

**Commits deployed:** fa90a18..666369e
- Ethics backend (EthicsRecord model, full CRUD, derived training-coverage percentages)
- Ethics frontend (EthicsPage, sidebar/router entries)
- generate_brsr_principle1() wired into ESG report, new endpoint GET /esg-reports/brsr-principle1

**Pre-deploy backup:** /home/ubuntu/benas_backup_pre_p1_25aug26.dump (130,311 bytes)

**Note:** production repo had uncommitted DEPLOYMENT_HISTORY.md changes and stray
dist-* artifacts from the prior manual deploy session (never committed back) --
discarded via git checkout -- . + git clean -fd before pulling, since fresh
builds were being made anyway. Verified via diff first that nothing new was
being lost (it was the already-committed CSR entry).

**Schema changes:** new table ethics_records, auto-created via
Base.metadata.create_all on app import (no manual migration -- new table,
not new columns). Confirmed via \d ethics_records post-restart.

**Steps:** pg_dump backup -> git checkout/clean -> git pull (fa90a18..666369e)
-> restart backend service (confirmed ethics_records table created in logs
and via psql) -> built both frontend targets (.env.benas -> dist-benas,
.env.manufactureos -> dist-manufactureos) -> rsync deployed both -> verified
401 (not 404) on /api/v1/esg-reports/brsr-principle1 and 200 on both domains.

**Status:** Deployed and verified working. No rollback needed.

---

## 2026-08-25 (later) — BRSR Principle 7 (Policy Advocacy) production deploy

**Commits deployed:** 666369e..d8249a3
- Policy advocacy backend (PolicyAdvocacyRecord + TradeAssociation, full CRUD)
- Policy advocacy frontend (PolicyAdvocacyPage, sidebar/router entries)
- generate_brsr_principle7() wired into ESG report, new endpoint GET /esg-reports/brsr-principle7

**Pre-deploy backup:** /home/ubuntu/benas_backup_pre_p7_25aug26.dump (135,039 bytes)

**Note:** production repo had a duplicate-appended P1 deployment log entry and
stray dist-* artifacts from the prior manual deploy session (never committed
back) -- discarded via git checkout -- . + git clean -fd before pulling.
Verified via diff first that nothing new was being lost.

**Schema changes:** new tables policy_advocacy_records + trade_associations,
auto-created via Base.metadata.create_all on app import (no manual migration
-- new tables, not new columns). Confirmed via \dt post-restart.

**Steps:** pg_dump backup -> git checkout/clean -> git pull (666369e..d8249a3,
17 files) -> restart backend service (confirmed both tables created in logs
and via \dt) -> built both frontend targets (.env.benas -> dist-benas,
.env.manufactureos -> dist-manufactureos) -> rsync deployed both -> verified
401 (not 404) on /api/v1/esg-reports/brsr-principle7 and
/api/v1/policy-advocacy-records/, and 200 on both domains.

**Status:** Deployed and verified working. No rollback needed.

---

## 2026-08-25 (later still) — BRSR Principle 4 (Stakeholder Responsiveness) production deploy

**Commits deployed:** d8249a3..b187318
- Stakeholder engagement backend (StakeholderEngagementRecord + StakeholderGroup, full CRUD)
- Stakeholder engagement frontend (StakeholderEngagementPage, sidebar/router entries)
- generate_brsr_principle4() wired into ESG report, new endpoint GET /esg-reports/brsr-principle4

**Pre-deploy backup:** /home/ubuntu/benas_backup_pre_p4_25aug26.dump (142,887 bytes)

**Note:** production repo again had stray dist-* artifacts and an already-
committed DEPLOYMENT_HISTORY.md entry (the P7 deploy log) from the prior
manual build session -- discarded via git checkout -- . + git clean -fd
before pulling. Verified via diff first that nothing new was being lost.

**Schema changes:** new tables stakeholder_engagement_records +
stakeholder_groups, auto-created via Base.metadata.create_all on app
import (no manual migration -- new tables, not new columns). Confirmed
via \dt post-restart.

**Steps:** pg_dump backup -> git checkout/clean -> git pull (d8249a3..b187318,
17 files) -> restart backend service (confirmed both tables created in logs
and via \dt) -> built both frontend targets (.env.benas -> dist-benas,
.env.manufactureos -> dist-manufactureos) -> rsync deployed both -> verified
401 (not 404) on /api/v1/esg-reports/brsr-principle4 and
/api/v1/stakeholder-engagement-records/, and 200 on both domains.

**Status:** Deployed and verified working. No rollback needed.

---

## 2026-08-27 -- Global Scope 2 electricity tracking, ManufactureOS-only deploy

**Commits deployed:** b187318..0b62b5f

**Strategic context:** BENAS is on hold per the 25 Aug 2026 pivot -- this
deploy built and rsynced ONLY dist-manufactureos, deliberately leaving
BENAS production bundle untouched, since this feature is Manufacturing
segment only and safe to skip for BENAS.

- country_config.py: added US and Australia grid factors, registry now
  covers 14 countries. New Region enum values NORTH_AMERICA, OCEANIA.
- ManufacturingElectricityRecord: Scope 2 counterpart to
  ManufacturingEmissionRecord Scope 1. CO2e is derived at read time via
  the unit country_code lookup, never stored.
- Full CRUD API at /manufacturing-electricity-records.
- Frontend: features/manufacturing-electricity, route
  /manufacturing-electricity, sidebar entry Electricity Scope 2.

**Pre-deploy backup:** /home/ubuntu/benas_backup_pre_scope2_27aug26.dump, 151217 bytes

**Schema changes:** new table manufacturing_electricity_records, auto
created via create_all on app import.

**Steps:** pg_dump backup, git pull to 0b62b5f, restart backend service,
confirmed table created, built ONLY dist-manufactureos, rsync deployed
ONLY to manufactureos domain, verified 401 on the new endpoint and 200
on the domain. dist-benas intentionally NOT touched this deploy.

**Status:** Deployed and verified working, ManufactureOS only. No rollback needed.
