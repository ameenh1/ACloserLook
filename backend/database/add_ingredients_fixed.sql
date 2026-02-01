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
  ('Rayon', 'Fibers that help absorb and retain fluid, commonly used in tampons for absorbency', 'Low', NOW()),
  ('Cotton', 'Natural fibers that help absorb and retain fluid, providing softness and absorbency', 'Low', NOW()),
  ('Polypropylene', 'Synthetic fibers that help channel fluid back to the core for better absorption control', 'Medium', NOW()),
  ('Polyethylene', 'Smooth plastic fibers that help with easy and comfortable removal', 'Medium', NOW()),
  ('Polyester', 'Synthetic thread used to sew tampon components together for structural integrity', 'Medium', NOW()),
  ('Glycerin', 'Coating applied to fibers to help wick fluid efficiently for better absorption', 'Low', NOW()),
  ('Paraffin', 'Wax coating that helps keep the string clean and protected from moisture', 'Low', NOW()),
  ('Ethoxylated Fatty Acid Esters', 'Coating that helps fibers wick fluid more effectively for improved absorbency', 'Low', NOW()),
  ('PEG-100 Stearate', 'Coating agent that helps fibers wick fluid efficiently, improving overall absorbency', 'Low', NOW())
ON CONFLICT (name) DO NOTHING;

-- Step 2: Get the IDs for all 9 ingredients - COPY THESE IDS
SELECT id, name, risk_level
FROM ingredients_library
WHERE name IN (
  'Rayon',
  'Cotton',
  'Polypropylene',
  'Polyethylene',
  'Polyester',
  'Glycerin',
  'Paraffin',
  'Ethoxylated Fatty Acid Esters',
  'PEG-100 Stearate'
)
ORDER BY name;

-- ==========================================
-- Step 3: INSERT YOUR PRODUCT with the ingredient IDs
-- Note: Status must be 'pending', 'review_needed', or 'ready' (NOT 'active')
-- ==========================================

INSERT INTO products (brand_name, barcode, product_type, ingredients, coverage_score, research_count, status, created_at, updated_at)
VALUES (
  'Tampax Pearl',
  '073010719743',
  'tampon',
  ARRAY[47, 53, 51, 52, 54, 3, 32, 36, 2],  -- Cotton, Ethoxylated Fatty Acid Esters, Glycerin, Paraffin, PEG-100 Stearate, Polyester, Polyethylene, Polypropylene, Rayon
  0.85,
  9,
  'ready',
  NOW(),
  NOW()
);
