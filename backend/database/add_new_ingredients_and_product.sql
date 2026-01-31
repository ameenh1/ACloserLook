-- Add new ingredients to ingredients_library and seed product

-- Step 1: Insert all the new ingredients into ingredients_library
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
ON CONFLICT (name) DO NOTHING;  -- Don't insert if ingredient already exists

-- Step 2: Verify ingredients were inserted and get their IDs
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

-- Step 3: Save the IDs from the query above, then insert your product
-- Copy the IDs from the results and paste them into the ARRAY below

-- INSERT INTO products (brand_name, barcode, product_type, ingredients, coverage_score, research_count, status, created_at, updated_at)
-- VALUES (
--   'YOUR_BRAND_NAME',
--   'YOUR_BARCODE_HERE',
--   'pad',  -- or 'tampon'
--   ARRAY[ID1, ID2, ID3, ID4, ID5, ID6, ID7, ID8, ID9, ID10, ID11, ID12, ID13, ID14, ID15],  -- Paste ingredient IDs here
--   0.85,
--   15,
--   'active',
--   NOW(),
--   NOW()
-- );

-- Step 4: After inserting product, verify all ingredients show up
-- SELECT 
--   p.id,
--   p.brand_name,
--   p.barcode,
--   ARRAY_AGG(i.name ORDER BY i.name) as ingredient_names,
--   array_length(p.ingredients, 1) as total_ingredients
-- FROM products p
-- LEFT JOIN ingredients_library i ON i.id = ANY(p.ingredients)
-- WHERE p.barcode = 'YOUR_BARCODE_HERE'
-- GROUP BY p.id, p.brand_name, p.barcode;
