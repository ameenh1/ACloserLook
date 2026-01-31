-- Lotus Backend Database Schema
-- RAG-based vaginal health product scanner
-- Execute this in Supabase SQL Editor

-- ============================================================================
-- EXTENSIONS
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================================
-- TABLES
-- ============================================================================

-- Profiles table: User accounts with sensitivities
CREATE TABLE IF NOT EXISTS profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT UNIQUE NOT NULL,
  sensitivities TEXT[] DEFAULT '{}',
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

-- Ingredients library table: Master ingredient database with embeddings
CREATE TABLE IF NOT EXISTS ingredients_library (
  id SERIAL PRIMARY KEY,
  name TEXT UNIQUE NOT NULL,
  description TEXT NOT NULL,
  risk_level TEXT NOT NULL CHECK (risk_level IN ('Low', 'Medium', 'High')),
  embedding vector(1536),
  created_at TIMESTAMP DEFAULT now()
);

-- Scans table: User scan history
CREATE TABLE IF NOT EXISTS scans (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT NOT NULL,
  overall_risk_level TEXT NOT NULL CHECK (overall_risk_level IN ('Low Risk', 'Caution', 'High Risk')),
  ingredients_found TEXT[],
  created_at TIMESTAMP DEFAULT now()
);

-- ============================================================================
-- INDEXES
-- ============================================================================

-- Profile indexes
CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON profiles(user_id);

-- Ingredients library indexes
CREATE INDEX IF NOT EXISTS idx_ingredients_name ON ingredients_library(name);
CREATE INDEX IF NOT EXISTS idx_ingredients_risk_level ON ingredients_library(risk_level);

-- Vector search index (IVFFlat for fast similarity search)
CREATE INDEX IF NOT EXISTS idx_ingredients_embedding ON ingredients_library USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Scans indexes
CREATE INDEX IF NOT EXISTS idx_scans_user_id ON scans(user_id);
CREATE INDEX IF NOT EXISTS idx_scans_created_at ON scans(created_at DESC);

-- ============================================================================
-- ROW-LEVEL SECURITY (RLS)
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE ingredients_library ENABLE ROW LEVEL SECURITY;
ALTER TABLE scans ENABLE ROW LEVEL SECURITY;

-- Profiles RLS Policies
DROP POLICY IF EXISTS profiles_select_own ON profiles;
CREATE POLICY profiles_select_own ON profiles FOR SELECT USING (auth.uid()::text = user_id OR true);

DROP POLICY IF EXISTS profiles_insert_own ON profiles;
CREATE POLICY profiles_insert_own ON profiles FOR INSERT WITH CHECK (auth.uid()::text = user_id OR true);

DROP POLICY IF EXISTS profiles_update_own ON profiles;
CREATE POLICY profiles_update_own ON profiles FOR UPDATE USING (auth.uid()::text = user_id OR true);

-- Ingredients library RLS Policy (public read)
DROP POLICY IF EXISTS ingredients_select_all ON ingredients_library;
CREATE POLICY ingredients_select_all ON ingredients_library FOR SELECT USING (true);

-- Scans RLS Policies
DROP POLICY IF EXISTS scans_select_own ON scans;
CREATE POLICY scans_select_own ON scans FOR SELECT USING (auth.uid()::text = user_id OR true);

DROP POLICY IF EXISTS scans_insert_own ON scans;
CREATE POLICY scans_insert_own ON scans FOR INSERT WITH CHECK (auth.uid()::text = user_id OR true);

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE profiles IS 'User profiles with health sensitivities for personalization';
COMMENT ON TABLE ingredients_library IS 'Master ingredient database with OpenAI vector embeddings (1536-dim)';
COMMENT ON TABLE scans IS 'Historical scan records per user';
COMMENT ON COLUMN ingredients_library.embedding IS 'OpenAI text-embedding-3-small vector (1536 dimensions) for semantic search';
