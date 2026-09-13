-- LCA session 4: benchmark key + MCI inputs. IF NOT EXISTS -> safe to re-run on every environment.
ALTER TABLE lca_products
  ADD COLUMN IF NOT EXISTS benchmark_key VARCHAR(40),
  ADD COLUMN IF NOT EXISTS eol_recycling_fraction DOUBLE PRECISION,
  ADD COLUMN IF NOT EXISTS eol_reuse_fraction DOUBLE PRECISION,
  ADD COLUMN IF NOT EXISTS recycling_efficiency_input DOUBLE PRECISION,
  ADD COLUMN IF NOT EXISTS recycling_efficiency_eol DOUBLE PRECISION,
  ADD COLUMN IF NOT EXISTS lifetime_years DOUBLE PRECISION,
  ADD COLUMN IF NOT EXISTS industry_avg_lifetime_years DOUBLE PRECISION;
ALTER TABLE lca_inventory_items
  ADD COLUMN IF NOT EXISTS recycled_content_fraction DOUBLE PRECISION,
  ADD COLUMN IF NOT EXISTS reused_content_fraction DOUBLE PRECISION;
