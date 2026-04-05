/** Builds `/search` URL with optional city and county query params (for Explore and street detail links). */
export function buildSearchPath(params: { city?: string | null; county?: string | null }): string {
  const sp = new URLSearchParams();
  if (params.city) sp.set('city', params.city);
  if (params.county) sp.set('county', params.county);
  const qs = sp.toString();
  return qs ? `/search?${qs}` : '/search';
}
