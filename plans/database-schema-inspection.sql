-- Run this SQL script in your Supabase SQL Editor to inspect your database schema
-- Copy and paste the results back to me

-- 1. List all tables in the public schema
SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;

-- 2. Get detailed schema for each table (uncomment the ones you want to inspect)
-- Replace table_name with your actual table names (profiles, ingredients_library, products, etc.)

-- For profiles table:
-- \d+ profiles

-- For ingredients_library table:
-- \d+ ingredients_library

-- For products table (if it exists):
-- \d+ products

-- Alternative: Get column info for ALL public tables:
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable,
    column_default
FROM 
    information_schema.columns 
WHERE 
    table_schema = 'public'
ORDER BY 
    table_name, ordinal_position;

-- Alternative: Get table and column info in a readable format:
SELECT 
    t.tablename as table_name,
    a.attname as column_name,
    pg_catalog.format_type(a.atttypid, a.atttypmod) as data_type,
    CASE WHEN a.attnotnull THEN 'NOT NULL' ELSE 'nullable' END as constraints
FROM 
    pg_tables t
    JOIN pg_class c ON t.tablename = c.relname
    JOIN pg_attribute a ON c.oid = a.attrelid
WHERE 
    t.schemaname = 'public'
    AND a.attnum > 0
ORDER BY 
    t.tablename, a.attnum;
