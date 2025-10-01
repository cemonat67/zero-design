-- Zero@Design CSV Data Import Script
-- This script imports CSV data into the normalized database structure

-- =====================================================
-- TEMPORARY STAGING TABLES
-- =====================================================

-- Staging table for konfeksiyon processes
CREATE TEMP TABLE staging_konfeksiyon (
    kategori TEXT,
    islem_adimi TEXT,
    aciklama TEXT,
    uygulanan_urun_gruplari TEXT,
    co2_range TEXT,
    not_field TEXT
);

-- Staging table for finished product operations
CREATE TEMP TABLE staging_finished_operations (
    kategori TEXT,
    islem_turu TEXT,
    aciklama TEXT,
    uygulanan_urun_gruplari TEXT
);

-- Staging table for finished product operations with CO2
CREATE TEMP TABLE staging_finished_co2 (
    ust_kategori TEXT,
    kategori TEXT,
    islem TEXT,
    aciklama TEXT,
    uygulanan_urun_gruplari TEXT,
    co2_range TEXT,
    not_field TEXT
);

-- Staging table for master konfeksiyon
CREATE TEMP TABLE staging_master (
    category TEXT,
    name TEXT,
    type TEXT,
    unit TEXT,
    stage TEXT,
    description TEXT,
    min_co2_kg TEXT,
    max_co2_kg TEXT,
    avg_co2_kg TEXT,
    source TEXT,
    source_file TEXT
);

-- Staging table for fabric data
CREATE TEMP TABLE staging_fabrics (
    gender TEXT,
    category TEXT,
    product TEXT,
    fabric_type TEXT,
    composition TEXT,
    usage_hint TEXT,
    co2_kg_per_kg TEXT
);

-- =====================================================
-- IMPORT CSV DATA INTO STAGING TABLES
-- =====================================================

-- Import konfeksiyon processes
\COPY staging_konfeksiyon FROM '/app/data/csv/konfeksiyon_surecleri_co2.csv' WITH (FORMAT CSV, HEADER true, DELIMITER ',', ENCODING 'UTF8');

-- Import finished product operations (base definitions)
\COPY staging_finished_operations FROM '/app/data/csv/bitmis_urun_islemleri_co2.csv' WITH (FORMAT CSV, HEADER true, DELIMITER ',', ENCODING 'UTF8');

-- Import finished product operations with CO2
\COPY staging_finished_co2 FROM '/app/data/csv/hazir_giyim_master_co2.csv' WITH (FORMAT CSV, HEADER true, DELIMITER ',', ENCODING 'UTF8');

-- Import master konfeksiyon data
\COPY staging_master FROM '/app/data/csv/Final_Dosyalar/Master_Konfeksiyon copy.csv' WITH (FORMAT CSV, HEADER true, DELIMITER ',', ENCODING 'UTF8');

-- Import fabric data (semicolon delimiter)
\COPY staging_fabrics FROM '/app/data/csv/Final_Dosyalar/Urun_Kumas_CO2_Listesi.csv' WITH (FORMAT CSV, HEADER true, DELIMITER ';', ENCODING 'UTF8');

-- =====================================================
-- HELPER FUNCTIONS FOR DATA PROCESSING
-- =====================================================

-- Function to parse CO2 range (e.g., "0.35-0.50" -> min: 0.35, max: 0.50)
CREATE OR REPLACE FUNCTION parse_co2_range(co2_text TEXT, OUT min_val DECIMAL, OUT max_val DECIMAL, OUT avg_val DECIMAL) AS $$
BEGIN
    IF co2_text IS NULL OR co2_text = '' THEN
        min_val := NULL;
        max_val := NULL;
        avg_val := NULL;
        RETURN;
    END IF;
    
    -- Handle range format like "0.35-0.50"
    IF co2_text ~ '^-?[0-9]+\.?[0-9]*-[0-9]+\.?[0-9]*$' THEN
        min_val := CAST(split_part(co2_text, '-', 1) AS DECIMAL);
        max_val := CAST(split_part(co2_text, '-', 2) AS DECIMAL);
        avg_val := (min_val + max_val) / 2;
    -- Handle single value
    ELSIF co2_text ~ '^-?[0-9]+\.?[0-9]*$' THEN
        min_val := CAST(co2_text AS DECIMAL);
        max_val := min_val;
        avg_val := min_val;
    ELSE
        min_val := NULL;
        max_val := NULL;
        avg_val := NULL;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- INSERT DATA INTO MAIN TABLES
-- =====================================================

-- Insert konfeksiyon processes
INSERT INTO processes (category, stage_group, process_name, description, applied_products)
SELECT DISTINCT
    kategori,
    'Konfeksiyon',
    islem_adimi,
    aciklama,
    uygulanan_urun_gruplari
FROM staging_konfeksiyon
WHERE kategori IS NOT NULL AND islem_adimi IS NOT NULL;

-- Insert emissions for konfeksiyon processes
INSERT INTO emissions (process_id, min_co2_kg, max_co2_kg, avg_co2_kg, source_file, notes)
SELECT 
    p.id,
    (parse_co2_range(s.co2_range)).min_val,
    (parse_co2_range(s.co2_range)).max_val,
    (parse_co2_range(s.co2_range)).avg_val,
    'konfeksiyon_surecleri_co2.csv',
    s.not_field
FROM staging_konfeksiyon s
JOIN processes p ON p.process_name = s.islem_adimi AND p.category = s.kategori
WHERE s.co2_range IS NOT NULL AND s.co2_range != '';

-- Insert finished product operations (base definitions)
INSERT INTO processes (category, stage_group, process_name, description, applied_products)
SELECT DISTINCT
    kategori,
    'Bitmiş Ürün İşlemleri',
    islem_turu,
    aciklama,
    uygulanan_urun_gruplari
FROM staging_finished_operations
WHERE kategori IS NOT NULL AND islem_turu IS NOT NULL
ON CONFLICT DO NOTHING;

-- Insert finished product operations with CO2 data
INSERT INTO processes (category, stage_group, process_name, description, applied_products)
SELECT DISTINCT
    kategori,
    ust_kategori,
    islem,
    aciklama,
    uygulanan_urun_gruplari
FROM staging_finished_co2
WHERE kategori IS NOT NULL AND islem IS NOT NULL
ON CONFLICT DO NOTHING;

-- Insert emissions for finished product operations
INSERT INTO emissions (process_id, min_co2_kg, max_co2_kg, avg_co2_kg, source_file, notes)
SELECT 
    p.id,
    (parse_co2_range(s.co2_range)).min_val,
    (parse_co2_range(s.co2_range)).max_val,
    (parse_co2_range(s.co2_range)).avg_val,
    'hazir_giyim_master_co2.csv',
    s.not_field
FROM staging_finished_co2 s
JOIN processes p ON p.process_name = s.islem AND p.category = s.kategori
WHERE s.co2_range IS NOT NULL AND s.co2_range != '';

-- Insert lifecycle master data
INSERT INTO lifecycle_master (
    category, process_name, unit, stage, description, 
    min_co2_kg, max_co2_kg, avg_co2_kg, source, source_file
)
SELECT 
    category,
    name,
    unit,
    stage,
    description,
    CASE WHEN min_co2_kg ~ '^-?[0-9]+\.?[0-9]*$' THEN CAST(min_co2_kg AS DECIMAL) ELSE NULL END,
    CASE WHEN max_co2_kg ~ '^-?[0-9]+\.?[0-9]*$' THEN CAST(max_co2_kg AS DECIMAL) ELSE NULL END,
    CASE WHEN avg_co2_kg ~ '^-?[0-9]+\.?[0-9]*$' THEN CAST(avg_co2_kg AS DECIMAL) ELSE NULL END,
    source,
    source_file
FROM staging_master
WHERE category IS NOT NULL AND name IS NOT NULL;

-- Insert fabric data
INSERT INTO fabrics (
    gender, category, product, fabric_type, 
    composition, usage_hint, co2_kg_per_kg
)
SELECT 
    gender,
    category,
    product,
    fabric_type,
    composition,
    usage_hint,
    CASE WHEN co2_kg_per_kg ~ '^[0-9]+\.?[0-9]*$' THEN CAST(co2_kg_per_kg AS DECIMAL) ELSE NULL END
FROM staging_fabrics
WHERE fabric_type IS NOT NULL;

-- =====================================================
-- DATA QUALITY CHECKS AND SUMMARY
-- =====================================================

-- Display import summary
SELECT 'Data Import Summary:' as info;

SELECT 
    'Processes' as table_name,
    COUNT(*) as record_count
FROM processes
UNION ALL
SELECT 
    'Emissions' as table_name,
    COUNT(*) as record_count
FROM emissions
UNION ALL
SELECT 
    'Fabrics' as table_name,
    COUNT(*) as record_count
FROM fabrics
UNION ALL
SELECT 
    'Lifecycle Master' as table_name,
    COUNT(*) as record_count
FROM lifecycle_master;

-- Check for data quality issues
SELECT 'Data Quality Checks:' as info;

SELECT 
    'Processes without emissions' as check_type,
    COUNT(*) as count
FROM processes p
LEFT JOIN emissions e ON p.id = e.process_id
WHERE e.id IS NULL;

SELECT 
    'Emissions with invalid CO2 values' as check_type,
    COUNT(*) as count
FROM emissions
WHERE avg_co2_kg < 0 OR min_co2_kg < 0 OR max_co2_kg < 0;

-- Clean up helper function
DROP FUNCTION IF EXISTS parse_co2_range(TEXT);

SELECT 'CSV Data Import Completed Successfully!' as status;