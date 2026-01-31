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

-- Step 2: Get the IDs for all 15 ingredients - COPY THESE IDS
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
-- Step 3: AFTER getting IDs from above, fill in and run this:
-- ==========================================

-- INSERT INTO products (brand_name, barcode, product_type, ingredients, coverage_score, research_count, status, created_at, updated_at)
-- VALUES (
--   'YOUR_BRAND_NAME',                    
--   'YOUR_BARCODE_HERE',                  
--   'pad',                                
--   ARRAY[id1, id2, id3, id4, id5, id6, id7, id8, id9, id10, id11, id12, id13, id14, id15],  
--   0.85,                                 
--   15,                                   
--   'active',
--   NOW(),
--   NOW()
-- );
