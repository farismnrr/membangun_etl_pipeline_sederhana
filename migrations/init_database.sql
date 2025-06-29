-- =============================================================================
-- Complete Database Initialization Script
-- =============================================================================
-- Project: Membangun ETL Pipeline Sederhana
-- Description: Single file to create database, user, and all tables
-- Author: Faris Munir Mahdi
-- Created: 2025-06-29
-- =============================================================================

-- =============================================================================
-- 1. Create Database (if not exists)
-- =============================================================================

-- Note: CREATE DATABASE IF NOT EXISTS is not supported in PostgreSQL
-- We'll handle this in the script logic

-- =============================================================================
-- 2. Create User (if not exists)
-- =============================================================================

-- Create developer user if not exists
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'developer') THEN
        CREATE ROLE developer LOGIN PASSWORD 'supersecretpassword';
        RAISE NOTICE 'User developer created successfully';
    ELSE
        RAISE NOTICE 'User developer already exists';
    END IF;
END
$$;

-- Grant necessary privileges
DO $$
BEGIN
    -- Grant basic database privileges
    EXECUTE 'GRANT CONNECT ON DATABASE ' || current_database() || ' TO developer';
    EXECUTE 'GRANT CREATE ON DATABASE ' || current_database() || ' TO developer';
    
    -- Grant schema privileges
    GRANT ALL ON SCHEMA public TO developer;
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO developer;
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO developer;
    
    -- Set default privileges for future objects
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO developer;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO developer;
    
    RAISE NOTICE 'Privileges granted to developer user';
END
$$;

-- =============================================================================
-- 3. Create Fashion Products Table (if not exists)
-- =============================================================================

-- Drop existing table if you want to recreate (uncomment next line)
-- DROP TABLE IF EXISTS fashion_products CASCADE;

-- Create main table
CREATE TABLE IF NOT EXISTS fashion_products (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    price DECIMAL(12,2) NOT NULL CHECK (price >= 0),
    rating DECIMAL(3,2) CHECK (rating >= 0 AND rating <= 5.0),
    colors INTEGER CHECK (colors >= 0),
    size VARCHAR(10) NOT NULL CHECK (size IN ('XS', 'S', 'M', 'L', 'XL', 'XXL')),
    gender VARCHAR(20) NOT NULL CHECK (gender IN ('Men', 'Women', 'Unisex')),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- 4. Create Indexes (if not exists)
-- =============================================================================

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_fashion_products_price ON fashion_products(price);
CREATE INDEX IF NOT EXISTS idx_fashion_products_rating ON fashion_products(rating);
CREATE INDEX IF NOT EXISTS idx_fashion_products_size ON fashion_products(size);
CREATE INDEX IF NOT EXISTS idx_fashion_products_gender ON fashion_products(gender);
CREATE INDEX IF NOT EXISTS idx_fashion_products_timestamp ON fashion_products(timestamp);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_fashion_products_gender_size ON fashion_products(gender, size);
CREATE INDEX IF NOT EXISTS idx_fashion_products_price_rating ON fashion_products(price, rating);

-- =============================================================================
-- 5. Add Table Comments and Constraints
-- =============================================================================

-- Add table and column comments
COMMENT ON TABLE fashion_products IS 'Fashion products data from ETL pipeline';
COMMENT ON COLUMN fashion_products.id IS 'Unique identifier for each product';
COMMENT ON COLUMN fashion_products.title IS 'Product name/title';
COMMENT ON COLUMN fashion_products.price IS 'Product price in Rupiah';
COMMENT ON COLUMN fashion_products.rating IS 'Product rating from 0.0 to 5.0';
COMMENT ON COLUMN fashion_products.colors IS 'Number of available color variants';
COMMENT ON COLUMN fashion_products.size IS 'Product size (XS, S, M, L, XL, XXL)';
COMMENT ON COLUMN fashion_products.gender IS 'Target gender (Men, Women, Unisex)';
COMMENT ON COLUMN fashion_products.timestamp IS 'Data extraction timestamp';

-- =============================================================================
-- 6. Create Trigger Function for Updated Timestamp (if not exists)
-- =============================================================================

-- Function to update timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.timestamp = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger if not exists
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_fashion_products_timestamp') THEN
        CREATE TRIGGER update_fashion_products_timestamp
            BEFORE UPDATE ON fashion_products
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        RAISE NOTICE 'Trigger update_fashion_products_timestamp created';
    ELSE
        RAISE NOTICE 'Trigger update_fashion_products_timestamp already exists';
    END IF;
END
$$;

-- =============================================================================
-- 7. Create Views for Common Queries (if not exists)
-- =============================================================================

-- Summary view by gender and size
CREATE OR REPLACE VIEW fashion_products_summary AS
SELECT 
    gender,
    size,
    COUNT(*) as total_products,
    AVG(price) as avg_price,
    AVG(rating) as avg_rating,
    MIN(price) as min_price,
    MAX(price) as max_price,
    MIN(rating) as min_rating,
    MAX(rating) as max_rating
FROM fashion_products
GROUP BY gender, size
ORDER BY gender, size;

-- Recent products view (last 30 days)
CREATE OR REPLACE VIEW recent_fashion_products AS
SELECT *
FROM fashion_products
WHERE timestamp >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY timestamp DESC;

-- Top rated products view
CREATE OR REPLACE VIEW top_rated_products AS
SELECT *
FROM fashion_products
WHERE rating >= 4.0
ORDER BY rating DESC, price ASC;

-- =============================================================================
-- 8. Create Useful Functions (if not exists)
-- =============================================================================

-- Function to get product statistics by category
CREATE OR REPLACE FUNCTION get_product_stats_by_category(category_name VARCHAR)
RETURNS TABLE(
    gender VARCHAR,
    total_products BIGINT,
    avg_price NUMERIC,
    avg_rating NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        fp.gender,
        COUNT(*)::BIGINT,
        AVG(fp.price),
        AVG(fp.rating)
    FROM fashion_products fp
    WHERE fp.gender = category_name
    GROUP BY fp.gender;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- 9. Grant Permissions to Developer User
-- =============================================================================

-- Grant permissions to all created objects
DO $$
BEGIN
    -- Grant table permissions
    GRANT ALL PRIVILEGES ON TABLE fashion_products TO developer;
    GRANT ALL PRIVILEGES ON SEQUENCE fashion_products_id_seq TO developer;
    
    -- Grant view permissions
    GRANT SELECT ON fashion_products_summary TO developer;
    GRANT SELECT ON recent_fashion_products TO developer;
    GRANT SELECT ON top_rated_products TO developer;
    
    -- Grant function permissions
    GRANT EXECUTE ON FUNCTION get_product_stats_by_category(VARCHAR) TO developer;
    GRANT EXECUTE ON FUNCTION update_updated_at_column() TO developer;
    
    RAISE NOTICE 'All permissions granted to developer user';
END
$$;

-- =============================================================================
-- 10. Insert Sample Data (optional - uncomment if needed)
-- =============================================================================

/*
-- Sample data for testing
INSERT INTO fashion_products (title, price, rating, colors, size, gender) VALUES
    ('Sample T-Shirt', 150000.00, 4.5, 3, 'M', 'Men'),
    ('Sample Dress', 250000.00, 4.2, 2, 'L', 'Women'),
    ('Sample Jacket', 450000.00, 4.8, 4, 'L', 'Unisex')
ON CONFLICT DO NOTHING;
*/

-- =============================================================================
-- 11. Verification and Success Message
-- =============================================================================

-- Display success message and basic stats
DO $$
DECLARE
    table_exists BOOLEAN;
    user_exists BOOLEAN;
    record_count INTEGER;
BEGIN
    -- Check if table exists
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'fashion_products'
    ) INTO table_exists;
    
    -- Check if user exists
    SELECT EXISTS (
        SELECT FROM pg_catalog.pg_roles 
        WHERE rolname = 'developer'
    ) INTO user_exists;
    
    -- Get record count
    IF table_exists THEN
        SELECT COUNT(*) INTO record_count FROM fashion_products;
    ELSE
        record_count := 0;
    END IF;
    
    -- Display results
    RAISE NOTICE '===============================================';
    RAISE NOTICE 'Database Initialization Complete!';
    RAISE NOTICE '===============================================';
    RAISE NOTICE 'Database: %', current_database();
    RAISE NOTICE 'User "developer" exists: %', user_exists;
    RAISE NOTICE 'Table "fashion_products" exists: %', table_exists;
    RAISE NOTICE 'Current record count: %', record_count;
    RAISE NOTICE '===============================================';
    RAISE NOTICE 'Ready for ETL Pipeline!';
    RAISE NOTICE '===============================================';
END
$$;
