-- Step 1: Find ingredient IDs in your database
-- Run this query first to get the IDs for all your ingredients

SELECT id, name 
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

-- If some ingredients don't exist, you'll need to add them first:
-- INSERT INTO ingredients_library (name, description, risk_level)
-- VALUES ('Ingredient Name', 'Description', 'Low');

-- Step 2: After you have all the IDs, fill them into the ARRAY below
-- Copy the IDs from the query results above

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
  'YOUR_BRAND_NAME',           -- Replace with your product brand
  'YOUR_BARCODE_HERE',         -- Replace with your product barcode (must be unique)
  'pad',                       -- or 'tampon' if applicable
  ARRAY[
    -- Replace the numbers below with the actual IDs from the query above
    -- Example: ARRAY[1, 5, 12, 45, 67, 89, 102, 115, 128, 140, 155, 168, 180, 195, 210]
    ID1, ID2, ID3, ID4, ID5, ID6, ID7, ID8, ID9, ID10, ID11, ID12, ID13, ID14, ID15
  ],
  0.85,                        -- Coverage score (0-1)
  15,                          -- Number of research studies
  'active',
  NOW(),
  NOW()
);

-- Step 3: Verify your product was inserted with all ingredients
-- Replace 'YOUR_BARCODE_HERE' with your actual barcode

SELECT 
  p.id,
  p.brand_name,
  p.barcode,
  p.product_type,
  ARRAY_AGG(i.name ORDER BY i.name) as ingredient_names,
  array_length(p.ingredients, 1) as total_ingredients,
  p.coverage_score,
  p.research_count,
  p.created_at
FROM products p
LEFT JOIN ingredients_library i ON i.id = ANY(p.ingredients)
WHERE p.barcode = 'YOUR_BARCODE_HERE'
GROUP BY p.id, p.brand_name, p.barcode, p.product_type, p.coverage_score, p.research_count, p.created_at;

-- Step 4: Test barcode lookup via the API
-- After inserting, test with: curl -X POST http://localhost:8000/api/scan/barcode \
--   -H "Content-Type: application/json" \
--   -d '{"barcode": "YOUR_BARCODE_HERE"}'
