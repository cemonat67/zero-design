-- Zero@Design CO2 Database Schema
-- PostgreSQL 16 compatible
-- Normalized schema with practical views

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- MAIN TABLES (Normalized Structure)
-- =====================================================

-- Processes table: All manufacturing and finishing processes
CREATE TABLE processes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category VARCHAR(100) NOT NULL,
    stage_group VARCHAR(100),
    stage VARCHAR(100),
    process_name VARCHAR(200) NOT NULL,
    unit VARCHAR(50),
    description TEXT,
    applied_products TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Emissions table: CO2 data linked to processes
CREATE TABLE emissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    process_id UUID NOT NULL REFERENCES processes(id) ON DELETE CASCADE,
    min_co2_kg DECIMAL(10,4),
    max_co2_kg DECIMAL(10,4),
    avg_co2_kg DECIMAL(10,4),
    source VARCHAR(200),
    source_file VARCHAR(200),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fabrics table: Fabric types and their CO2 footprint
CREATE TABLE fabrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    gender VARCHAR(20),
    category VARCHAR(100),
    product VARCHAR(100),
    fabric_type VARCHAR(100) NOT NULL,
    fiber_combo VARCHAR(200),
    composition VARCHAR(200),
    gsm_range VARCHAR(50),
    use_case TEXT,
    usage_hint TEXT,
    co2_kg_per_kg DECIMAL(10,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Accessories table: Accessory items and their CO2 impact
CREATE TABLE accessories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    gender VARCHAR(20),
    category VARCHAR(100),
    product VARCHAR(100),
    accessory_name VARCHAR(200) NOT NULL,
    material VARCHAR(100),
    composition VARCHAR(200),
    unit VARCHAR(50),
    usage_hint TEXT,
    co2_kg_per_kg DECIMAL(10,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Lifecycle Master table: Complete lifecycle data
CREATE TABLE lifecycle_master (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    upper_category VARCHAR(100),
    category VARCHAR(100),
    stage_group VARCHAR(100),
    stage VARCHAR(100),
    process_name VARCHAR(200) NOT NULL,
    input_material VARCHAR(200),
    unit VARCHAR(50),
    description TEXT,
    applied_products TEXT,
    min_co2_kg DECIMAL(10,4),
    max_co2_kg DECIMAL(10,4),
    avg_co2_kg DECIMAL(10,4),
    notes TEXT,
    source VARCHAR(200),
    source_file VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Processes indexes
CREATE INDEX idx_processes_category ON processes(category);
CREATE INDEX idx_processes_stage_group ON processes(stage_group);
CREATE INDEX idx_processes_process_name ON processes(process_name);

-- Emissions indexes
CREATE INDEX idx_emissions_process_id ON emissions(process_id);
CREATE INDEX idx_emissions_avg_co2 ON emissions(avg_co2_kg);

-- Fabrics indexes
CREATE INDEX idx_fabrics_fabric_type ON fabrics(fabric_type);
CREATE INDEX idx_fabrics_gender_category ON fabrics(gender, category);
CREATE INDEX idx_fabrics_co2 ON fabrics(co2_kg_per_kg);

-- Accessories indexes
CREATE INDEX idx_accessories_accessory_name ON accessories(accessory_name);
CREATE INDEX idx_accessories_gender_category ON accessories(gender, category);

-- Lifecycle master indexes
CREATE INDEX idx_lifecycle_category ON lifecycle_master(category);
CREATE INDEX idx_lifecycle_stage_group ON lifecycle_master(stage_group);
CREATE INDEX idx_lifecycle_process_name ON lifecycle_master(process_name);

-- =====================================================
-- PRACTICAL VIEWS (For easy querying)
-- =====================================================

-- Manufacturing processes view (combines processes and emissions)
CREATE VIEW manufacturing_processes AS
SELECT 
    p.id,
    p.category,
    p.stage_group,
    p.stage,
    p.process_name,
    p.unit,
    p.description,
    p.applied_products,
    e.min_co2_kg,
    e.max_co2_kg,
    e.avg_co2_kg,
    e.source,
    e.source_file,
    e.notes,
    p.created_at,
    p.updated_at
FROM processes p
LEFT JOIN emissions e ON p.id = e.process_id
WHERE p.stage_group IN ('Kesim', 'Dikiş', 'Bitirme', 'Konfeksiyon');

-- Finished product operations view (printing, embroidery, etc.)
CREATE VIEW finished_product_operations AS
SELECT 
    p.id,
    p.category,
    p.stage_group,
    p.stage,
    p.process_name,
    p.unit,
    p.description,
    p.applied_products,
    e.min_co2_kg,
    e.max_co2_kg,
    e.avg_co2_kg,
    e.source,
    e.source_file,
    e.notes,
    p.created_at,
    p.updated_at
FROM processes p
LEFT JOIN emissions e ON p.id = e.process_id
WHERE p.category IN ('Baskı Teknikleri', 'Nakış & Süsleme', 'Aksesuar Eklemeler', 'Yüzey İşlemleri');

-- Fabric CO2 data view (direct mapping to fabrics table)
CREATE VIEW fabric_co2_data AS
SELECT 
    id,
    gender,
    category,
    product,
    fabric_type,
    fiber_combo,
    composition,
    usage_hint,
    co2_kg_per_kg,
    created_at,
    updated_at
FROM fabrics;

-- Master operations view (direct mapping to lifecycle_master table)
CREATE VIEW master_operations AS
SELECT 
    id,
    upper_category,
    category,
    stage_group,
    stage,
    process_name,
    input_material,
    unit,
    description,
    applied_products,
    min_co2_kg,
    max_co2_kg,
    avg_co2_kg,
    notes,
    source,
    source_file,
    created_at,
    updated_at
FROM lifecycle_master;

-- =====================================================
-- UTILITY FUNCTIONS
-- =====================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_processes_updated_at BEFORE UPDATE ON processes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_emissions_updated_at BEFORE UPDATE ON emissions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_fabrics_updated_at BEFORE UPDATE ON fabrics FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_accessories_updated_at BEFORE UPDATE ON accessories FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_lifecycle_master_updated_at BEFORE UPDATE ON lifecycle_master FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- INITIAL DATA VALIDATION
-- =====================================================

-- Add constraints for data quality
ALTER TABLE emissions ADD CONSTRAINT check_co2_positive CHECK (
    (min_co2_kg IS NULL OR min_co2_kg >= 0) AND
    (max_co2_kg IS NULL OR max_co2_kg >= 0) AND
    (avg_co2_kg IS NULL OR avg_co2_kg >= 0)
);

ALTER TABLE fabrics ADD CONSTRAINT check_fabric_co2_positive CHECK (
    co2_kg_per_kg IS NULL OR co2_kg_per_kg >= 0
);

ALTER TABLE accessories ADD CONSTRAINT check_accessory_co2_positive CHECK (
    co2_kg_per_kg IS NULL OR co2_kg_per_kg >= 0
);

-- Schema creation completed
SELECT 'Zero@Design CO2 Database Schema created successfully!' as status;