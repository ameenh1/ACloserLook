-- Phase 5: RPC Functions for Optimized Database Operations
-- Supabase PostgreSQL functions for vector search and analytics

-- ============================================
-- FUNCTION: match_ingredients
-- ============================================
-- Performs vector similarity search for ingredient matching
-- Uses cosine similarity for semantic comparison
-- Parameters:
--   query_embedding: vector(1536) - Query embedding from ingredient name/description
--   match_threshold: float - Similarity threshold (0.0-1.0), recommended 0.7+
--   match_count: int - Maximum number of results to return
CREATE OR REPLACE FUNCTION match_ingredients(
  query_embedding vector(1536),
  match_threshold float DEFAULT 0.7,
  match_count int DEFAULT 10
)
RETURNS TABLE (
  id int,
  name text,
  description text,
  risk_level text,
  similarity float
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    ingredients_library.id,
    ingredients_library.name,
    ingredients_library.description,
    ingredients_library.risk_level,
    (1 - (ingredients_library.embedding <=> query_embedding))::float AS similarity
  FROM ingredients_library
  WHERE ingredients_library.embedding IS NOT NULL
  ORDER BY ingredients_library.embedding <=> query_embedding
  LIMIT match_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- FUNCTION: get_user_scan_history
-- ============================================
-- Retrieves recent scan history for a specific user
-- Optimized for pagination and analytics
-- Parameters:
--   p_user_id: text - User ID (from auth)
--   p_limit: int - Number of records to return (default 50)
-- Optional: p_offset for pagination
CREATE OR REPLACE FUNCTION get_user_scan_history(
  p_user_id text,
  p_limit int DEFAULT 50,
  p_offset int DEFAULT 0
)
RETURNS TABLE (
  id uuid,
  overall_risk_level text,
  ingredients_found text[],
  created_at timestamp,
  days_ago int
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    scans.id,
    scans.overall_risk_level,
    scans.ingredients_found,
    scans.created_at,
    EXTRACT(DAY FROM (now() - scans.created_at))::int AS days_ago
  FROM scans
  WHERE scans.user_id = p_user_id
  ORDER BY scans.created_at DESC
  LIMIT p_limit
  OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- FUNCTION: upsert_ingredient
-- ============================================
-- Safely inserts or updates ingredient in library
-- Prevents duplicate entries and tracks updates
CREATE OR REPLACE FUNCTION upsert_ingredient(
  p_name text,
  p_description text,
  p_risk_level text,
  p_embedding vector(1536)
)
RETURNS TABLE (
  id int,
  name text,
  operation text
) AS $$
DECLARE
  v_id int;
BEGIN
  INSERT INTO ingredients_library (name, description, risk_level, embedding)
  VALUES (p_name, p_description, p_risk_level, p_embedding)
  ON CONFLICT (name) DO UPDATE
  SET description = p_description,
      risk_level = p_risk_level,
      embedding = p_embedding
  RETURNING ingredients_library.id INTO v_id;
  
  RETURN QUERY SELECT v_id, p_name, 'upserted'::text;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- FUNCTION: get_risk_statistics
-- ============================================
-- Generates risk statistics for user dashboard
CREATE OR REPLACE FUNCTION get_risk_statistics(
  p_user_id text
)
RETURNS TABLE (
  total_scans int,
  high_risk_scans int,
  medium_risk_scans int,
  low_risk_scans int,
  last_scan_date timestamp,
  average_risk_level text
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    COUNT(*)::int AS total_scans,
    COUNT(CASE WHEN scans.overall_risk_level = 'high' THEN 1 END)::int AS high_risk_scans,
    COUNT(CASE WHEN scans.overall_risk_level = 'medium' THEN 1 END)::int AS medium_risk_scans,
    COUNT(CASE WHEN scans.overall_risk_level = 'low' THEN 1 END)::int AS low_risk_scans,
    MAX(scans.created_at) AS last_scan_date,
    MODE() WITHIN GROUP (ORDER BY scans.overall_risk_level) AS average_risk_level
  FROM scans
  WHERE scans.user_id = p_user_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- FUNCTION: record_scan
-- ============================================
-- Atomically records a scan and updates profile
CREATE OR REPLACE FUNCTION record_scan(
  p_user_id text,
  p_overall_risk_level text,
  p_ingredients_found text[]
)
RETURNS TABLE (
  scan_id uuid,
  success boolean,
  message text
) AS $$
DECLARE
  v_scan_id uuid;
  v_profile_exists boolean;
BEGIN
  -- Check if profile exists
  SELECT EXISTS(SELECT 1 FROM profiles WHERE profiles.user_id = p_user_id)
  INTO v_profile_exists;
  
  -- Create profile if it doesn't exist
  IF NOT v_profile_exists THEN
    INSERT INTO profiles (user_id) VALUES (p_user_id)
    ON CONFLICT (user_id) DO NOTHING;
  END IF;
  
  -- Record scan
  INSERT INTO scans (user_id, overall_risk_level, ingredients_found)
  VALUES (p_user_id, p_overall_risk_level, p_ingredients_found)
  RETURNING scans.id INTO v_scan_id;
  
  RETURN QUERY SELECT v_scan_id, true, 'Scan recorded successfully'::text;
  
EXCEPTION WHEN OTHERS THEN
  RETURN QUERY SELECT NULL::uuid, false, 'Error recording scan: ' || SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- GRANTS FOR AUTHENTICATED USERS
-- ============================================
-- Allow authenticated users to call RPC functions
GRANT EXECUTE ON FUNCTION match_ingredients(vector, float, int) TO authenticated;
GRANT EXECUTE ON FUNCTION get_user_scan_history(text, int, int) TO authenticated;
GRANT EXECUTE ON FUNCTION upsert_ingredient(text, text, text, vector) TO authenticated;
GRANT EXECUTE ON FUNCTION get_risk_statistics(text) TO authenticated;
GRANT EXECUTE ON FUNCTION record_scan(text, text, text[]) TO authenticated;
