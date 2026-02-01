-- Supabase Vector Search Function
-- This function enables fast semantic similarity search using pgvector
-- Run this in Supabase Dashboard → SQL Editor

-- Enable pgvector extension if not already enabled
CREATE EXTENSION IF NOT EXISTS vector;

-- Create the search_ingredients function
CREATE OR REPLACE FUNCTION search_ingredients(
  query_embedding vector(1536),
  match_limit int DEFAULT 5,
  match_threshold float DEFAULT 0.1
)
RETURNS TABLE (
  id int,
  name text,
  description text,
  risk_level text,
  similarity_score float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    ingredients_library.id,
    ingredients_library.name,
    ingredients_library.description,
    ingredients_library.risk_level,
    1 - (ingredients_library.embedding <=> query_embedding) AS similarity_score
  FROM ingredients_library
  WHERE 1 - (ingredients_library.embedding <=> query_embedding) > match_threshold
  ORDER BY ingredients_library.embedding <=> query_embedding
  LIMIT match_limit;
END;
$$;

-- Test the function (optional)
-- You can test it by calling with a sample embedding:
-- SELECT * FROM search_ingredients(
--   (SELECT embedding FROM ingredients_library LIMIT 1),
--   5,
--   0.1
-- );
