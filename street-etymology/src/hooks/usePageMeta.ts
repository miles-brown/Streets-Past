import { useEffect } from 'react';
import { absoluteUrl, currentCanonicalUrl } from '../lib/site';

const SITE_NAME = 'Street Etymology UK';
const DEFAULT_DESCRIPTION =
  'Explore the etymological origins of UK street names — map, search, and community research.';

function setOrCreateMeta(attr: 'name' | 'property', key: string, content: string) {
  const esc = key.replace(/\\/g, '\\\\').replace(/"/g, '\\"');
  const selector = `meta[${attr}="${esc}"]`;
  let el = document.head.querySelector(selector) as HTMLMetaElement | null;
  if (!el) {
    el = document.createElement('meta');
    el.setAttribute(attr, key);
    document.head.appendChild(el);
  }
  el.setAttribute('content', content);
}

function setCanonicalLink(href: string) {
  let el = document.querySelector('link[rel="canonical"]') as HTMLLinkElement | null;
  if (!el) {
    el = document.createElement('link');
    el.rel = 'canonical';
    document.head.appendChild(el);
  }
  el.href = href;
}

export type PageMetaOptions = {
  title: string;
  description?: string;
  /** Absolute URL for OG / Twitter (defaults to site origin + path + query via `currentCanonicalUrl()`). */
  canonicalUrl?: string;
  /** When set, updates og:image / twitter:image (path or absolute URL). */
  image?: string;
  /** When true, sets meta robots to noindex,nofollow (e.g. login/register). */
  noIndex?: boolean;
};

/**
 * Sets document title and core SEO / Open Graph tags for the current view.
 * Restores the default home title when the component unmounts (SPA navigation).
 */
export function usePageMeta({ title, description, canonicalUrl, image, noIndex }: PageMetaOptions) {
  useEffect(() => {
    const fullTitle = title === SITE_NAME ? SITE_NAME : `${title} · ${SITE_NAME}`;
    document.title = fullTitle;

    const desc = description ?? DEFAULT_DESCRIPTION;
    setOrCreateMeta('name', 'description', desc);
    setOrCreateMeta('name', 'robots', noIndex ? 'noindex, nofollow' : 'index, follow');
    setOrCreateMeta('property', 'og:type', 'website');
    setOrCreateMeta('property', 'og:title', fullTitle);
    setOrCreateMeta('property', 'og:description', desc);
    setOrCreateMeta('property', 'twitter:card', 'summary_large_image');
    setOrCreateMeta('property', 'twitter:title', fullTitle);
    setOrCreateMeta('property', 'twitter:description', desc);

    const url = canonicalUrl ?? currentCanonicalUrl();
    if (url) {
      setCanonicalLink(url);
      setOrCreateMeta('property', 'og:url', url);
      setOrCreateMeta('property', 'twitter:url', url);
    }

    const resolvedImg = image ?? '/og-image.png';
    const absImg = resolvedImg.startsWith('http')
      ? resolvedImg
      : absoluteUrl(resolvedImg.startsWith('/') ? resolvedImg : `/${resolvedImg}`);
    setOrCreateMeta('property', 'og:image', absImg);
    setOrCreateMeta('property', 'twitter:image', absImg);
  }, [title, description, canonicalUrl, image, noIndex]);
}
