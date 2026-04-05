import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL?.replace(/\/$/, '');
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY?.trim();

const missingEnv = !supabaseUrl || !supabaseAnonKey;
const looksLikePlaceholder =
  supabaseAnonKey === 'your-anon-key' ||
  supabaseAnonKey === 'your_supabase_anon_key' ||
  supabaseAnonKey === 'your_supabase_anon_key_here';

if (import.meta.env.DEV && (missingEnv || looksLikePlaceholder)) {
  console.error(
    '[Streets Past] Supabase is not configured. Copy street-etymology/.env.example to .env and set VITE_SUPABASE_ANON_KEY (Dashboard → Settings → API → anon public).'
  );
} else if (!import.meta.env.DEV && missingEnv) {
  console.warn('Supabase env missing: VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY must be set at build time.');
}

export const supabase = createClient(supabaseUrl ?? '', supabaseAnonKey ?? '', {
  auth: {
    flowType: 'pkce',
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: true,
  },
});

export interface Profile {
  user_id: string;
  email: string | null;
  full_name: string | null;
  role: string | null;
  contribution_count: number | null;
  updated_at?: string | null;
}

export interface Street {
  id: string;
  name: string;
  city: string | null;
  county: string | null;
  postcode_area: string | null;
  latitude: number | null;
  longitude: number | null;
  etymology_suggestion: string | null;
  etymology_verified: boolean | null;
  etymology_source: string | null;
  first_recorded_date: string | null;
  historical_notes: string | null;
  updated_at?: string | null;
}

export interface Contribution {
  id: string;
  street_id: string;
  user_id: string | null;
  user_email: string;
  etymology_suggestion: string;
  sources: string | null;
  status: 'pending' | 'approved' | 'rejected';
  created_at: string;
  reviewed_at: string | null;
}
