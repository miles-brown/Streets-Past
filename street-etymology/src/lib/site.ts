/**
 * Canonical public site origin for SEO (OG, JSON-LD, sitemap).
 * Override in `.env.local` when testing share previews: VITE_SITE_ORIGIN=https://streetetymology.co.uk
 */
export function getSiteOrigin(): string {
  const fromEnv = import.meta.env.VITE_SITE_ORIGIN as string | undefined;
  if (fromEnv && /^https?:\/\//.test(fromEnv)) {
    return fromEnv.replace(/\/$/, '');
  }
  if (typeof window !== 'undefined') {
    return window.location.origin;
  }
  return 'https://streetetymology.co.uk';
}

export function absoluteUrl(path: string): string {
  const base = getSiteOrigin();
  const p = path.startsWith('/') ? path : `/${path}`;
  return `${base}${p}`;
}

/** Current page URL using configured site origin (for canonical / OG when `VITE_SITE_ORIGIN` is set). */
export function currentCanonicalUrl(): string {
  if (typeof window === 'undefined') return '';
  return `${getSiteOrigin()}${window.location.pathname}${window.location.search}`;
}
