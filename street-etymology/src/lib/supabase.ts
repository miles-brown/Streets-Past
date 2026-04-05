import { createClient, SupabaseClient } from '@supabase/supabase-js';

/**
 * @supabase/supabase-js throws if createClient gets an empty URL or key ("supabaseUrl is required").
 * Missing VITE_* vars on Vercel used to crash the bundle at import time → blank page.
 * We only call createClient with non-empty strings; missing env uses inert placeholders + loud console warning.
 */
const FALLBACK_URL = 'https://configure-env-vars.supabase.co';
const FALLBACK_KEY = 'configure-vite-supabase-env-vars';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL?.replace(/\/$/, '');
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY?.trim();

const looksLikePlaceholder =
  supabaseAnonKey === 'your-anon-key' ||
  supabaseAnonKey === 'your_supabase_anon_key' ||
  supabaseAnonKey === 'your_supabase_anon_key_here' ||
  supabaseAnonKey === '<your-supabase-anon-key>';

const missingEnv =
  !supabaseUrl ||
  !supabaseAnonKey ||
  looksLikePlaceholder;

const resolvedUrl = missingEnv ? FALLBACK_URL : supabaseUrl;
const resolvedKey = missingEnv ? FALLBACK_KEY : supabaseAnonKey;

if (missingEnv) {
  console.error(
    '[Streets Past] Supabase env missing or placeholder. Set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY in .env locally, and in Vercel → Project → Settings → Environment Variables for Production & Preview, then redeploy. The anon key must be available at build time (Vite inlines VITE_*).'
  );
}

const authOptions = {
  flowType: 'pkce' as const,
  persistSession: true,
  autoRefreshToken: true,
  detectSessionInUrl: true,
};

let client: SupabaseClient | null = null;

function getClient(): SupabaseClient {
  if (!client) {
    client = createClient(resolvedUrl, resolvedKey, { auth: authOptions });
  }
  return client;
}

/** True when real project URL and anon key are present (not fallback / placeholder). */
export function isSupabaseConfigured(): boolean {
  return !missingEnv;
}

export const supabase = new Proxy({} as SupabaseClient, {
  get(_target, prop, receiver) {
    const c = getClient();
    const value = Reflect.get(c, prop, receiver);
    return typeof value === 'function' ? value.bind(c) : value;
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
