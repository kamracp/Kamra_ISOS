-- LCA session 5, step 1: industry key + declared product mass per functional unit. Safe to re-run.
ALTER TABLE lca_products
  ADD COLUMN IF NOT EXISTS industry VARCHAR(30),
  ADD COLUMN IF NOT EXISTS fu_mass_kg DOUBLE PRECISION;
