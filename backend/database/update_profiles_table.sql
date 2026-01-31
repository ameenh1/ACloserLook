-- Run this in Supabase SQL Editor to update the profiles table
-- This adds the new columns needed for health profile saving

-- First, add the new columns to the existing profiles table
ALTER TABLE profiles 
ADD COLUMN IF NOT EXISTS skin_type TEXT DEFAULT '',
ADD COLUMN IF NOT EXISTS allergies JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS conditions JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS preferences JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS price_range TEXT DEFAULT '';

-- Update the RLS policies to ensure users can access their own data
DROP POLICY IF EXISTS profiles_select_own ON profiles;
CREATE POLICY profiles_select_own ON profiles FOR SELECT USING (auth.uid()::text = user_id);

DROP POLICY IF EXISTS profiles_insert_own ON profiles;
CREATE POLICY profiles_insert_own ON profiles FOR INSERT WITH CHECK (auth.uid()::text = user_id);

DROP POLICY IF EXISTS profiles_update_own ON profiles;
CREATE POLICY profiles_update_own ON profiles FOR UPDATE USING (auth.uid()::text = user_id);

-- Allow upsert operations
DROP POLICY IF EXISTS profiles_upsert_own ON profiles;
CREATE POLICY profiles_upsert_own ON profiles FOR ALL USING (auth.uid()::text = user_id);

-- Verify the table structure
SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'profiles';
