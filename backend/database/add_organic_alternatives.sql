-- Add organic and non-toxic alternative products to the database
-- These will be shown as safer alternatives when scanning Always pads or Tampax tampons
-- Note: ingredients column uses integer array of IDs from ingredients_library table

-- First, ensure we have "Cotton" ingredient (it should already exist)
-- Get the Cotton ingredient ID for reference
DO $$
DECLARE
    cotton_id INTEGER;
BEGIN
    -- Get Cotton ID (should already exist from previous setup)
    SELECT id INTO cotton_id FROM ingredients_library WHERE name = 'Cotton' LIMIT 1;
    
    IF cotton_id IS NULL THEN
        RAISE NOTICE 'Cotton ingredient not found. Please add it first.';
    ELSE
        RAISE NOTICE 'Cotton ingredient ID: %', cotton_id;
    END IF;
END $$;

-- ==========================================
-- ORGANIC & NON-TOXIC PADS
-- ==========================================

-- 1. Rael Organic Cotton Cover Pads
INSERT INTO products (brand_name, product_type, ingredients, barcode, coverage_score, research_count, status, created_at, updated_at)
VALUES (
    'Rael Organic Cotton Cover Pads',
    'pad',
    ARRAY[(SELECT id FROM ingredients_library WHERE name = 'Cotton' LIMIT 1)]::INTEGER[],
    'RAEL-PAD-001',
    0.95,
    5,
    'ready',
    NOW(),
    NOW()
)
ON CONFLICT (barcode) DO NOTHING;

-- 2. Cora Organic Ultra Thin Period Pads
INSERT INTO products (brand_name, product_type, ingredients, barcode, coverage_score, research_count, status, created_at, updated_at)
VALUES (
    'Cora Organic Ultra Thin Period Pads',
    'pad',
    ARRAY[(SELECT id FROM ingredients_library WHERE name = 'Cotton' LIMIT 1)]::INTEGER[],
    'CORA-PAD-001',
    0.95,
    5,
    'ready',
    NOW(),
    NOW()
)
ON CONFLICT (barcode) DO NOTHING;

-- 3. Organyc Heavy Night Pads
INSERT INTO products (brand_name, product_type, ingredients, barcode, coverage_score, research_count, status, created_at, updated_at)
VALUES (
    'Organyc Heavy Night Pads',
    'pad',
    ARRAY[(SELECT id FROM ingredients_library WHERE name = 'Cotton' LIMIT 1)]::INTEGER[],
    'ORGANYC-PAD-001',
    0.95,
    5,
    'ready',
    NOW(),
    NOW()
)
ON CONFLICT (barcode) DO NOTHING;


-- ==========================================
-- ORGANIC & NON-TOXIC TAMPONS
-- ==========================================

-- 1. Organyc Compact Tampons Super 16 Count
INSERT INTO products (brand_name, product_type, ingredients, barcode, coverage_score, research_count, status, created_at, updated_at)
VALUES (
    'Organyc Compact Tampons Super 16 Count',
    'tampon',
    ARRAY[(SELECT id FROM ingredients_library WHERE name = 'Cotton' LIMIT 1)]::INTEGER[],
    'ORGANYC-TAMP-001',
    0.95,
    5,
    'ready',
    NOW(),
    NOW()
)
ON CONFLICT (barcode) DO NOTHING;

-- 2. Cora The Comfort Fit Organic Cotton Tampons
INSERT INTO products (brand_name, product_type, ingredients, barcode, coverage_score, research_count, status, created_at, updated_at)
VALUES (
    'Cora The Comfort Fit Organic Cotton Tampons',
    'tampon',
    ARRAY[(SELECT id FROM ingredients_library WHERE name = 'Cotton' LIMIT 1)]::INTEGER[],
    'CORA-TAMP-001',
    0.95,
    5,
    'ready',
    NOW(),
    NOW()
)
ON CONFLICT (barcode) DO NOTHING;

-- 3. The Honey Pot Duo Pack Tampons
INSERT INTO products (brand_name, product_type, ingredients, barcode, coverage_score, research_count, status, created_at, updated_at)
VALUES (
    'The Honey Pot Duo Pack Tampons',
    'tampon',
    ARRAY[(SELECT id FROM ingredients_library WHERE name = 'Cotton' LIMIT 1)]::INTEGER[],
    'HONEYPOT-TAMP-001',
    0.95,
    5,
    'ready',
    NOW(),
    NOW()
)
ON CONFLICT (barcode) DO NOTHING;


-- ==========================================
-- VERIFICATION QUERIES
-- ==========================================

-- View all organic pads
SELECT id, brand_name, product_type, barcode, ingredients
FROM products
WHERE product_type = 'pad'
  AND (
    brand_name ILIKE '%rael%' OR
    brand_name ILIKE '%cora%' OR
    brand_name ILIKE '%organyc%'
  );

-- View all organic tampons
SELECT id, brand_name, product_type, barcode, ingredients
FROM products
WHERE product_type = 'tampon'
  AND (
    brand_name ILIKE '%organyc%' OR
    brand_name ILIKE '%cora%' OR
    brand_name ILIKE '%honey pot%'
  );

-- Count products by type
SELECT product_type, COUNT(*) as count
FROM products
GROUP BY product_type
ORDER BY product_type;
