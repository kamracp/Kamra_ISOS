-- LCA session 5, step 0b: bind every emission factor row to a lca_references.py id. Safe to re-run.
ALTER TABLE emission_factors ADD COLUMN IF NOT EXISTS reference_id VARCHAR(60);
UPDATE emission_factors SET reference_id = 'defra_2026_flat_v1_2'       WHERE reference_id IS NULL AND source LIKE '%2026%' AND source LIKE '%DEFRA%';
UPDATE emission_factors SET reference_id = 'defra_2025_flat'            WHERE reference_id IS NULL AND source LIKE '%2025%' AND source LIKE '%DEFRA%';
UPDATE emission_factors SET reference_id = 'ipcc_2006_vol3_ch2_ch4'     WHERE reference_id IS NULL AND source LIKE 'IPCC 2006 Guidelines Vol 3%';
UPDATE emission_factors SET reference_id = 'ipcc_2006_vol2_ch2'         WHERE reference_id IS NULL AND source LIKE 'IPCC 2006%';
UPDATE emission_factors SET reference_id = 'cea_co2_baseline_v21_2025'  WHERE reference_id IS NULL AND source LIKE 'CEA%' AND source LIKE '%21.0%';
UPDATE emission_factors SET reference_id = 'cea_co2_baseline_v20_2024'  WHERE reference_id IS NULL AND source LIKE 'CEA%' AND source LIKE '%20.0%';
-- Anything still NULL is unreferenced and must not be used: deactivate, never delete (audit trail).
UPDATE emission_factors SET is_active = false WHERE reference_id IS NULL;
