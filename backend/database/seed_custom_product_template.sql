-- Custom Product Seeding Template
-- Fill in YOUR product details and run in Supabase SQL Editor

-- Step 1: First, find the ingredient IDs for your ingredients
-- Run this query to see all available ingredients:
SELECT id, name, risk_level FROM ingredients_library ORDER BY name;

-- Step 2: Once you have the ingredient IDs, fill in this INSERT statement
-- Replace the values in ALL CAPS with your actual data

INSERT INTO products (
  brand_name, 
  barcode, 
  product_type, 
  ingredients, 
  coverage_score, 
  research_count, 
  status, 
  created_at, 
  updated_at
)
VALUES (
  'Always',                    -- e.g., 'Kotex Natural'
  '037000561538',                  -- e.g., '012345678901' (must be unique)
  'pad',                  -- e.g., 'tampon' or 'pad'
  ARRAY[ID1, ID2, ID3, ID4],            -- e.g., ARRAY[1, 5, 12, 45] (ingredient IDs found above)
  YOUR_COVERAGE_SCORE,                  -- e.g., 0.85 (float between 0 and 1)
  YOUR_RESEARCH_COUNT,                  -- e.g., 15 (integer, number of research studies)
  'active',
  NOW(),
  NOW()
);

-- Step 3: Verify your product was inserted
-- Replace 'YOUR_BARCODE_HERE' with your actual barcode
SELECT 
  id,
  brand_name,
  barcode,
  product_type,
  ingredients,
  coverage_score,
  research_count,
  created_at
FROM products
WHERE barcode = 'YOUR_BARCODE_HERE';

-- Step 4: View ingredient names for your product (optional)
-- This shows what the frontend will display
SELECT 
  p.id,
  p.brand_name,
  p.barcode,
  ARRAY_AGG(i.name ORDER BY i.name) as ingredient_names,
  p.coverage_score,
  p.research_count
FROM products p
LEFT JOIN ingredients_library i ON i.id = ANY(p.ingredients)
WHERE p.barcode = 'YOUR_BARCODE_HERE'
GROUP BY p.id, p.brand_name, p.barcode, p.coverage_score, p.research_count;


-- ============================================================
-- EXAMPLE: How to use this template
-- ============================================================

/*
Say you have a product with these details:
  Brand: "Always Infinity"
  Barcode: "037000818052"
  Type: "pad"
  Ingredients: Organic Cotton (id=1), Viscose (id=4), Polyester (id=8)
  Coverage: 92%
  Research Studies: 20

And you ran the ingredient lookup query and found:
  - Organic Cotton = id 1
  - Viscose = id 4
  - Polyester = id 8

Then your INSERT statement would be:

INSERT INTO products (
  brand_name, 
  barcode, 
  product_type, 
  ingredients, 
  coverage_score, 
  research_count, 
  status, 
  created_at, 
  updated_at
)
VALUES (
  'Always Infinity',
  '037000818052',
  'pad',
  ARRAY[1, 4, 8],
  0.92,
  20,
  'active',
  NOW(),
  NOW()
);

Then to verify, you'd run:

SELECT 
  p.id,
  p.brand_name,
  p.barcode,
  ARRAY_AGG(i.name ORDER BY i.name) as ingredient_names,
  p.coverage_score,
  p.research_count
FROM products p
LEFT JOIN ingredients_library i ON i.id = ANY(p.ingredients)
WHERE p.barcode = '037000818052'
GROUP BY p.id, p.brand_name, p.barcode, p.coverage_score, p.research_count;

Expected result:
  id: 123
  brand_name: Always Infinity
  barcode: 037000818052
  ingredient_names: {Organic Cotton, Polyester, Viscose}
  coverage_score: 0.92
  research_count: 20
*/
