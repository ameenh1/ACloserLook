-- Add new ingredients safely without specifying IDs (let Postgres auto-generate)
-- This avoids the duplicate key error

-- Step 1: Insert ingredients WITHOUT specifying IDs (Postgres auto-generates them)
INSERT INTO ingredients_library (name, description, risk_level, created_at)
SELECT * FROM (VALUES
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
) AS t(name, description, risk_level, created_at)
ON CONFLICT (name) DO NOTHING;

-- Step 2: Get the IDs for all 15 ingredients you just added/already had
-- This will return all the IDs in order - COPY THESE IDS
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
-- Step 3: AFTER COPYING IDs FROM ABOVE
-- Replace YOUR_XXX values and uncomment to run
-- ==========================================

-- INSERT INTO products (brand_name, barcode, product_type, ingredients, coverage_score, research_count, status, created_at, updated_at)
-- VALUES (
--   'YOUR_BRAND_NAME',                    
--   'YOUR_BARCODE_HERE',                  
--   'pad',                                
--   ARRAY[PASTE_IDS_HERE_COMMA_SEPARATED],  
--   0.85,                                 
--   15,                                   
--   'active',
--   NOW(),
--   NOW()
-- );

-- Example after filling in:
-- INSERT INTO products (brand_name, barcode, product_type, ingredients, coverage_score, research_count, status, created_at, updated_at)
-- VALUES (
--   'Always Ultra',                    
--   '037000818052',                  
--   'pad',                                
--   ARRAY[47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61],  
--   0.92,                                 
--   20,                                   
--   'active',
--   NOW(),
--   NOW()
-- );
