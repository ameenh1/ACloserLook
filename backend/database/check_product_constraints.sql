-- Check the allowed values for product_type and status in the products table
SELECT
    con.conname AS constraint_name,
    pg_get_constraintdef(con.oid) AS check_clause
FROM pg_constraint con
JOIN pg_class rel ON rel.oid = con.conrelid
JOIN pg_namespace nsp ON nsp.oid = rel.relnamespace
WHERE rel.relname = 'products'
  AND con.contype = 'c'
ORDER BY con.conname;
