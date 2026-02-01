-- FIXED: Add new ingredients safely by resetting sequence first
-- This fixes the "duplicate key" error

-- Step 0: First, reset the sequence to the max existing ID + 1
-- This ensures new auto-generated IDs don't conflict with existing ones
SELECT setval(
  pg_get_serial_sequence('ingredients_library', 'id'),
  COALESCE((SELECT MAX(id) FROM ingredients_library), 0) + 1,
  false
);

-- Step 1: Now insert ingredients - Postgres will use the correct IDs
INSERT INTO ingredients_library (name, description, risk_level, created_at)
VALUES
  ('Boric Acid (NF Grade)', 'Pharmaceutical grade boric acid used for vaginal pH balance and yeast infection treatment', 'Medium', NOW()),
  ('Gelatin Capsule', 'Natural gelatin capsule shell used to contain and deliver active ingredients', 'Low', NOW())
ON CONFLICT (name) DO NOTHING;

-- Step 2: Get the IDs for all 2 ingredients - COPY THESE IDS
SELECT id, name, risk_level 
FROM ingredients_library 
WHERE name IN (
  'Boric Acid (NF Grade)',
  'Gelatin Capsule'
)
ORDER BY name;

-- ==========================================
-- Step 3: INSERT YOUR PRODUCT with the ingredient IDs
-- Note: Status must be 'pending', 'review_needed', or 'ready' (NOT 'active')
-- ==========================================

INSERT INTO products (brand_name, barcode, product_type, ingredients, coverage_score, research_count, status, created_at, updated_at)
VALUES (
  'YOUR_BRAND_NAME',
  'YOUR_BARCODE_HERE',
  'supplement',                         -- FIRST run add_supplement_product_type.sql to enable this type
  ARRAY[55, 56],                        -- Boric Acid (NF Grade), Gelatin Capsule
  0.85,
  2,
  'ready',
  NOW(),
  NOW()
);
