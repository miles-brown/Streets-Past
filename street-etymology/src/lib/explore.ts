import { supabase } from './supabase';

/**
 * Picks a random street id among rows with a non-null etymology suggestion.
 * Uses count + range for a single lightweight row (no full-table client fetch).
 */
export async function fetchRandomStreetIdWithEtymology(): Promise<string | null> {
  const { count, error: countError } = await supabase
    .from('streets')
    .select('*', { count: 'exact', head: true })
    .not('etymology_suggestion', 'is', null);

  if (countError || !count || count < 1) {
    console.error('random street count:', countError);
    return null;
  }

  const offset = Math.floor(Math.random() * count);

  const { data, error } = await supabase
    .from('streets')
    .select('id')
    .not('etymology_suggestion', 'is', null)
    .range(offset, offset)
    .maybeSingle();

  if (error) {
    console.error('random street pick:', error);
    return null;
  }

  return data?.id ?? null;
}
