-- Migration: Add settings table and user preferences
-- Date: 2024-01-XX
-- Description: Add settings table for system configuration and preferences column to users table

-- Settings table for system-wide configuration
CREATE TABLE IF NOT EXISTS settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT NOT NULL,
    description TEXT,
    data_type VARCHAR(20) DEFAULT 'string', -- string, number, boolean, json
    is_public BOOLEAN DEFAULT FALSE, -- Whether setting can be accessed by non-admin users
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add preferences column to users table (for SQLite compatibility)
-- Note: This will be handled differently for PostgreSQL vs SQLite
-- For PostgreSQL: ALTER TABLE users ADD COLUMN IF NOT EXISTS preferences JSONB DEFAULT '{}';
-- For SQLite: We'll handle this in the application code

-- Insert default CO2 threshold setting
INSERT INTO settings (key, value, description, data_type, is_public) 
VALUES (
    'co2_threshold', 
    '1000', 
    'CO₂ emission threshold in kg. When exceeded, alerts will be shown on dashboard.', 
    'number', 
    TRUE
) ON CONFLICT (key) DO NOTHING;

-- Insert other default settings
INSERT INTO settings (key, value, description, data_type, is_public) 
VALUES 
    ('alert_color', '#D51635', 'Brand red color for alerts and warnings', 'string', TRUE),
    ('dashboard_refresh_interval', '30', 'Dashboard auto-refresh interval in seconds', 'number', FALSE),
    ('max_export_records', '10000', 'Maximum number of records allowed in export files', 'number', FALSE),
    ('enable_email_alerts', 'true', 'Enable email notifications for threshold alerts', 'boolean', FALSE)
ON CONFLICT (key) DO NOTHING;

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_settings_key ON settings(key);
CREATE INDEX IF NOT EXISTS idx_settings_is_public ON settings(is_public);

-- Update trigger for settings table
CREATE OR REPLACE FUNCTION update_settings_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_settings_updated_at 
    BEFORE UPDATE ON settings 
    FOR EACH ROW 
    EXECUTE FUNCTION update_settings_updated_at();