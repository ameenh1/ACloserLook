-- Insert your product with all 15 ingredient IDs
-- Fill in YOUR_BRAND_NAME and YOUR_BARCODE_HERE, then run

INSERT INTO products (brand_name, barcode, product_type, ingredients, coverage_score, research_count, status, created_at, updated_at)
VALUES (
  'YOUR_BRAND_NAME',                    -- Replace with your brand name
  'YOUR_BARCODE_HERE',                  -- Replace with your product barcode
  'pad',                                -- Change to 'tampon' if needed
  ARRAY[31, 38, 35, 45, 44, 42, 40, 41, 39, 3, 32, 43, 36, 13, 10],  -- All 15 ingredient IDs
  0.85,                                 -- Coverage score
  15,                                   -- Research count
  'ready',                              -- Must be: 'pending', 'review_needed', or 'ready'
  NOW(),
  NOW()
);

-- Verify your product was inserted correctly
SELECT 
  p.id,
  p.brand_name,
  p.barcode,
  p.product_type,
  ARRAY_AGG(i.name ORDER BY i.name) as ingredient_names,
  array_length(p.ingredients, 1) as total_ingredients,
  p.coverage_score,
  p.research_count
FROM products p
LEFT JOIN ingredients_library i ON i.id = ANY(p.ingredients)
WHERE p.barcode = 'YOUR_BARCODE_HERE'  -- Use same barcode as above
GROUP BY p.id, p.brand_name, p.barcode, p.product_type, p.coverage_score, p.research_count;
