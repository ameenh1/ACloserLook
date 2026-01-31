"""
SQL script to seed test products with barcodes
Run this directly in Supabase SQL Editor

This script:
1. Creates 5 test products with different barcodes
2. Links them to existing ingredients from ingredients_library
3. Verifies the data was inserted correctly

Usage:
1. Go to Supabase Dashboard → SQL Editor
2. Create New Query
3. Copy and paste this entire script
4. Click Run
5. Check the results
"""

-- Step 1: Insert test products with barcodes
-- These will be used for testing the barcode lookup feature

INSERT INTO products (brand_name, barcode, product_type, ingredients, coverage_score, research_count, status, created_at, updated_at)
VALUES
  ('Pure Care Organic', '012345678901', 'tampon', ARRAY[1, 2, 3], 0.95, 15, 'active', NOW(), NOW()),
  ('Nature Choice', '054321987654', 'pad', ARRAY[1, 4, 5], 0.88, 12, 'active', NOW(), NOW()),
  ('EcoFlow Tampons', '123456789012', 'tampon', ARRAY[2, 3, 6], 0.92, 18, 'active', NOW(), NOW()),
  ('Comfort Plus', '987654321098', 'pad', ARRAY[1, 2, 7], 0.78, 8, 'active', NOW(), NOW()),
  ('Gentle Wave', '555666777888', 'tampon', ARRAY[3, 4, 8], 0.85, 11, 'active', NOW(), NOW())
ON CONFLICT DO NOTHING;

-- Step 2: Verify products were inserted
SELECT 
  id,
  brand_name,
  barcode,
  product_type,
  ingredients,
  coverage_score,
  research_count,
  status,
  created_at
FROM products
WHERE barcode IN (
  '012345678901',
  '054321987654',
  '123456789012',
  '987654321098',
  '555666777888'
)
ORDER BY created_at DESC;

-- Step 3: Count total products in database
SELECT COUNT(*) as total_products FROM products;

-- Step 4: View ingredient library (to verify ingredient IDs exist)
SELECT id, name, risk_level FROM ingredients_library ORDER BY id LIMIT 10;

-- Step 5: Sample barcode lookup test
-- You can copy this query and modify the barcode value to test lookups
SELECT 
  p.id,
  p.brand_name,
  p.barcode,
  p.product_type,
  p.ingredients,
  p.coverage_score,
  p.research_count
FROM products p
WHERE p.barcode = '012345678901';

-- Step 6: Test ingredient resolution
-- This shows how the frontend would resolve ingredient IDs to names
SELECT 
  p.id,
  p.brand_name,
  p.barcode,
  ARRAY_AGG(i.name) as ingredient_names,
  p.coverage_score,
  p.research_count
FROM products p
LEFT JOIN ingredients_library i ON i.id = ANY(p.ingredients)
WHERE p.barcode IN (
  '012345678901',
  '054321987654',
  '123456789012',
  '987654321098',
  '555666777888'
)
GROUP BY p.id, p.brand_name, p.barcode, p.coverage_score, p.research_count
ORDER BY p.barcode;
