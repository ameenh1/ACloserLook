-- Update Always Infinity product to show "Ultra Thin Pads" instead of "pad"
-- This barcode 037000818052 is the Always Infinity pads

UPDATE products
SET product_type = 'Ultra Thin Pads'
WHERE barcode = '037000818052'
  OR (brand_name ILIKE 'Always%' AND product_type = 'pad');

-- Verify the update
SELECT 
  id,
  brand_name,
  barcode,
  product_type,
  coverage_score,
  research_count,
  status
FROM products
WHERE brand_name ILIKE 'Always%';
