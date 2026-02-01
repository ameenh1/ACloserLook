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
  -- URO Vaginal Probiotic ingredients
  ('Lactobacillus acidophilus', 'Beneficial probiotic bacteria that supports vaginal health by maintaining healthy pH balance', 'Low', NOW()),
  ('Lactobacillus rhamnosus', 'Probiotic strain that helps maintain vaginal microbiome balance and supports immune function', 'Low', NOW()),
  ('Lactobacillus reuteri', 'Probiotic bacteria that promotes vaginal health and helps prevent harmful bacterial growth', 'Low', NOW()),
  ('Lactobacillus fermentum', 'Probiotic strain that supports vaginal flora balance and produces antimicrobial compounds', 'Low', NOW()),
  ('Xylooligosaccharides', 'Prebiotic fiber (XOS) that feeds beneficial bacteria and supports gut and vaginal health', 'Low', NOW()),
  ('Maltodextrin', 'Carbohydrate filler used as a carrier for probiotic cultures in supplements', 'Low', NOW()),
  ('Cellulose', 'Plant-based fiber used to create vegetarian capsule shells', 'Low', NOW()),
  ('Natural Color', 'Plant-derived coloring agents used for aesthetic purposes in supplements', 'Low', NOW())
ON CONFLICT (name) DO NOTHING;

-- Step 2: Get the IDs for all ingredients - COPY THESE IDS
SELECT id, name, risk_level
FROM ingredients_library
WHERE name IN (
  'Lactobacillus acidophilus',
  'Lactobacillus rhamnosus',
  'Lactobacillus reuteri',
  'Lactobacillus fermentum',
  'Xylooligosaccharides',
  'Maltodextrin',
  'Cellulose',
  'Natural Color'
)
ORDER BY name;

-- ==========================================
-- Step 3: INSERT YOUR PRODUCT with the ingredient IDs
-- Note: Status must be 'pending', 'review_needed', or 'ready' (NOT 'active')
-- ==========================================

INSERT INTO products (brand_name, barcode, product_type, ingredients, coverage_score, research_count, status, created_at, updated_at)
VALUES (
  'URO Vaginal Probiotic',
  '860008361769',
  'supplement',
  ARRAY[31, 57, 60, 59, 58, 62, 64, 61],  -- Cellulose, Lactobacillus acidophilus, Lactobacillus fermentum, Lactobacillus reuteri, Lactobacillus rhamnosus, Maltodextrin, Natural Color, Xylooligosaccharides
  1.0,
  8,
  'ready',
  NOW(),
  NOW()
);
