import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Types for our database
export interface UserProfile {
  id?: string
  user_id: string
  skin_type: string
  allergies: string[]
  conditions: string[]
  other_condition?: string
  preferences: string[]
  created_at?: string
  updated_at?: string
}
