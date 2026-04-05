/**
 * Repeatable smoke test: saved_streets table + auth round-trip (save / list / unsave).
 *
 * Usage (from street-etymology/):
 *   node --env-file=.env.local scripts/smoke-bookmarks.mjs
 *
 * Full auth test (same env file, plus):
 *   SMOKE_AUTH_EMAIL=... SMOKE_AUTH_PASSWORD=... node --env-file=.env.local scripts/smoke-bookmarks.mjs
 *
 * Exit codes: 0 success, 1 usage/config error, 2 table missing (apply migration first), 3 auth/API failure
 */
import { createClient } from '@supabase/supabase-js';

const url = process.env.VITE_SUPABASE_URL;
const anon = process.env.VITE_SUPABASE_ANON_KEY;
const email = process.env.SMOKE_AUTH_EMAIL;
const password = process.env.SMOKE_AUTH_PASSWORD;

if (!url || !anon) {
  console.error('Missing VITE_SUPABASE_URL or VITE_SUPABASE_ANON_KEY (use .env.local or export).');
  process.exit(1);
}

const supabase = createClient(url, anon);

async function assertTableExists() {
  const { error } = await supabase.from('saved_streets').select('id').limit(1);
  if (error?.code === 'PGRST205' || /Could not find the table/i.test(error?.message ?? '')) {
    console.error(
      '[smoke-bookmarks] public.saved_streets is not available. Apply supabase/migrations/20260405120000_saved_streets.sql (or scripts/apply-saved-streets.sql) on this project, then retry.',
    );
    process.exit(2);
  }
  if (error && error.code !== 'PGRST116') {
    console.warn('[smoke-bookmarks] saved_streets probe warning:', error.message);
  }
}

async function main() {
  await assertTableExists();
  console.log('[smoke-bookmarks] Table saved_streets is reachable.');

  if (!email || !password) {
    console.log(
      '[smoke-bookmarks] Set SMOKE_AUTH_EMAIL and SMOKE_AUTH_PASSWORD to run sign-in, insert, list, delete.',
    );
    return;
  }

  const { data: signInData, error: signInErr } = await supabase.auth.signInWithPassword({ email, password });
  if (signInErr || !signInData.session) {
    console.error('[smoke-bookmarks] Sign-in failed:', signInErr?.message ?? 'no session');
    process.exit(3);
  }

  const userId = signInData.session.user.id;

  const { data: streetRow, error: streetErr } = await supabase.from('streets').select('id').limit(1).maybeSingle();
  if (streetErr || !streetRow?.id) {
    console.error('[smoke-bookmarks] Could not fetch a street id:', streetErr?.message ?? 'empty');
    await supabase.auth.signOut();
    process.exit(3);
  }

  const streetId = streetRow.id;

  await supabase.from('saved_streets').delete().eq('user_id', userId).eq('street_id', streetId);

  const { data: inserted, error: insErr } = await supabase
    .from('saved_streets')
    .insert({ user_id: userId, street_id: streetId })
    .select('id')
    .single();

  if (insErr || !inserted?.id) {
    console.error('[smoke-bookmarks] Insert failed:', insErr?.message ?? 'no row');
    await supabase.auth.signOut();
    process.exit(3);
  }

  const { data: listed, error: listErr } = await supabase
    .from('saved_streets')
    .select('id, street_id')
    .eq('user_id', userId)
    .eq('street_id', streetId)
    .maybeSingle();

  if (listErr || !listed) {
    console.error('[smoke-bookmarks] Select after insert failed:', listErr?.message ?? 'no row');
    await supabase.auth.signOut();
    process.exit(3);
  }

  const { error: delErr } = await supabase.from('saved_streets').delete().eq('id', inserted.id);
  if (delErr) {
    console.error('[smoke-bookmarks] Delete failed:', delErr.message);
    await supabase.auth.signOut();
    process.exit(3);
  }

  await supabase.auth.signOut();
  console.log('[smoke-bookmarks] OK: save → verify row → unsave for street', streetId);
}

main().catch((e) => {
  console.error(e);
  process.exit(3);
});
