-- Add 'supplement' as an allowed product_type
-- Current allowed types: 'pad', 'tampon', 'liner'
-- This adds 'supplement' to the list

-- Step 1: Drop the existing constraint
ALTER TABLE products DROP CONSTRAINT products_product_type_check;

-- Step 2: Add the updated constraint with 'supplement' included
ALTER TABLE products ADD CONSTRAINT products_product_type_check 
CHECK (product_type = ANY (ARRAY['pad'::text, 'tampon'::text, 'liner'::text, 'supplement'::text]));

-- Step 3: Verify the constraint was updated
SELECT 
    con.conname AS constraint_name,
    pg_get_constraintdef(con.oid) AS check_clause
FROM pg_constraint con
JOIN pg_class rel ON rel.oid = con.conrelid
JOIN pg_namespace nsp ON nsp.oid = rel.relnamespace
WHERE rel.relname = 'products'
  AND con.contype = 'c'
  AND con.conname = 'products_product_type_check';
