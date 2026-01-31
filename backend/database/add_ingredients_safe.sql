-- Add new ingredients to ingredients_library (if not already present) and seed product

-- Step 1: Insert only new ingredients (using ON CONFLICT to skip duplicates)
INSERT INTO ingredients_library (name, description, risk_level, created_at)
VALUES
  ('Cellulose', 'Natural plant-based fiber from wood pulp', 'Low', NOW()),
  ('Polyethylene', 'Common plastic polymer used in product structure', 'Medium', NOW()),
  ('Polyester', 'Synthetic fiber for absorbency and durability', 'Medium', NOW()),
  ('Sodium Polyacrylate', 'Super-absorbent polymer for fluid retention', 'Medium', NOW()),
  ('Hot Melt Adhesive', 'Thermoplastic adhesive for material bonding', 'Low', NOW()),
  ('Polypropylene', 'Plastic polymer for structural support', 'Medium', NOW()),
  ('Titanium Dioxide', 'White pigment and opacity enhancer', 'Low', NOW()),
  ('Ethylene Vinyl Acetate Copolymer', 'Flexible polymer copolymer for comfort', 'Medium', NOW()),
  ('Pigment Red 122', 'Synthetic red colorant', 'Medium', NOW()),
  ('PEG-7 Glyceryl Cocoate', 'Plant-derived emulsifier and conditioning agent', 'Low', NOW()),
  ('Pigment Blue 15', 'Synthetic blue colorant', 'Medium', NOW()),
  ('PEG-10 Cocoate', 'Plant-derived conditioning and emollient agent', 'Low', NOW()),
  ('Polyoxyalkylene Substituted Chromophore', 'Advanced color compound for pigmentation', 'Medium', NOW()),
  ('PEG Sorbitol Hexaoleate', 'Plant-derived emulsifier and conditioning agent', 'Low', NOW()),
  ('PEG Hydrogenated Castor Oil Trilaurate', 'Plant-derived conditioning agent derived from castor oil', 'Low', NOW())
ON CONFLICT (name) DO NOTHING;

-- Step 2: Verify ingredients exist and get their IDs
-- Copy all the IDs from the results below
SELECT id, name, risk_level 
FROM ingredients_library 
WHERE name IN (
  'Cellulose',
  'Polyethylene',
  'Polyester',
  'Sodium Polyacrylate',
  'Hot Melt Adhesive',
  'Polypropylene',
  'Titanium Dioxide',
  'Ethylene Vinyl Acetate Copolymer',
  'Pigment Red 122',
  'PEG-7 Glyceryl Cocoate',
  'Pigment Blue 15',
  'PEG-10 Cocoate',
  'Polyoxyalkylene Substituted Chromophore',
  'PEG Sorbitol Hexaoleate',
  'PEG Hydrogenated Castor Oil Trilaurate'
)
ORDER BY name;

-- ==========================================
-- Step 3: INSERT YOUR PRODUCT
-- Replace the values in CAPS with your actual data
-- Then uncomment and run this query
-- ==========================================

-- INSERT INTO products (brand_name, barcode, product_type, ingredients, coverage_score, research_count, status, created_at, updated_at)
-- VALUES (
--   'YOUR_BRAND_NAME',                    -- Replace with your brand name
--   'YOUR_BARCODE_HERE',                  -- Replace with your unique barcode
--   'pad',                                -- Replace with 'tampon' or 'pad'
--   ARRAY[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],  -- Replace with actual ingredient IDs from Step 2
--   0.85,                                 -- Replace with your coverage score
--   15,                                   -- Replace with research count
--   'active',
--   NOW(),
--   NOW()
-- );

-- ==========================================
-- Step 4: VERIFY YOUR PRODUCT
-- Replace 'YOUR_BARCODE_HERE' with your actual barcode
-- Then uncomment and run this query
-- ==========================================

-- SELECT 
--   p.id,
--   p.brand_name,
--   p.barcode,
--   p.product_type,
--   ARRAY_AGG(i.name ORDER BY i.name) as ingredient_names,
--   array_length(p.ingredients, 1) as total_ingredients,
--   p.coverage_score,
--   p.research_count
-- FROM products p
-- LEFT JOIN ingredients_library i ON i.id = ANY(p.ingredients)
-- WHERE p.barcode = 'YOUR_BARCODE_HERE'
-- GROUP BY p.id, p.brand_name, p.barcode, p.product_type, p.coverage_score, p.research_count;
