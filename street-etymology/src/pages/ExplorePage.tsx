import { useState, useEffect, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { supabase, Street } from '../lib/supabase';
import { fetchRandomStreetIdWithEtymology } from '../lib/explore';
import { buildSearchPath } from '../lib/searchUrl';
import { usePageMeta } from '../hooks/usePageMeta';
import {
  MapPin,
  Search,
  Shuffle,
  Clock,
  Map as MapIcon,
  Loader2,
  ArrowRight,
  ChevronRight,
} from 'lucide-react';
import toast from 'react-hot-toast';

const RECENT_LIMIT = 10;
const COUNTY_SAMPLE = 2000;

type ExploreRecentRow = Pick<
  Street,
  'id' | 'name' | 'city' | 'county' | 'etymology_suggestion' | 'updated_at' | 'first_recorded_date'
>;

export function ExplorePage() {
  usePageMeta({
    title: 'Explore',
    description: 'Discover UK streets at random, see recent updates, and jump to search or the map.',
  });

  const navigate = useNavigate();
  const [recent, setRecent] = useState<ExploreRecentRow[]>([]);
  const [countyLinks, setCountyLinks] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [randomBusy, setRandomBusy] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const { data: recentRows, error: recentErr } = await supabase
        .from('streets')
        .select('id,name,city,county,etymology_suggestion,updated_at,first_recorded_date')
        .order('updated_at', { ascending: false, nullsFirst: false })
        .limit(RECENT_LIMIT);

      if (recentErr) throw recentErr;
      setRecent(recentRows || []);

      const { data: countyRows, error: countyErr } = await supabase
        .from('streets')
        .select('county')
        .not('county', 'is', null)
        .limit(COUNTY_SAMPLE);

      if (countyErr) throw countyErr;
      const uniq = [...new Set((countyRows || []).map((r) => r.county).filter(Boolean))] as string[];
      uniq.sort((a, b) => a.localeCompare(b));
      setCountyLinks(uniq.slice(0, 14));
    } catch (e) {
      console.error(e);
      toast.error('Could not load explore data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const onSurprise = async () => {
    setRandomBusy(true);
    try {
      const id = await fetchRandomStreetIdWithEtymology();
      if (!id) {
        toast.error('No streets with etymology found');
        return;
      }
      navigate(`/street/${id}`);
    } finally {
      setRandomBusy(false);
    }
  };

  return (
    <div className="min-h-screen bg-background py-10">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mb-10">
          <h1 className="mb-2 font-display text-3xl font-bold text-foreground">Explore</h1>
          <p className="max-w-2xl text-muted-foreground">
            Pick a random researched street, browse recent catalogue updates, or narrow by county — then open search
            or the full map.
          </p>
        </div>

        <div className="mb-10 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <Link
            to="/search"
            className="group surface-glass flex flex-col justify-between rounded-2xl p-6 transition-all hover:border-primary/25 hover:shadow-paper dark:hover:shadow-paper-dark"
          >
            <div>
              <div className="mb-3 inline-flex rounded-lg bg-primary/10 p-2 text-primary">
                <Search className="h-6 w-6" />
              </div>
              <h2 className="mb-1 font-display text-xl font-semibold text-foreground">Search streets</h2>
              <p className="text-sm text-muted-foreground">Filter by name, city, county, and verification status.</p>
            </div>
            <span className="mt-4 inline-flex items-center gap-1 text-sm font-medium text-primary">
              Open search
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
            </span>
          </Link>

          <Link
            to="/map"
            className="group surface-glass flex flex-col justify-between rounded-2xl p-6 transition-all hover:border-primary/25 hover:shadow-paper dark:hover:shadow-paper-dark"
          >
            <div>
              <div className="mb-3 inline-flex rounded-lg bg-primary/10 p-2 text-primary">
                <MapIcon className="h-6 w-6" />
              </div>
              <h2 className="mb-1 font-display text-xl font-semibold text-foreground">UK map</h2>
              <p className="text-sm text-muted-foreground">Pan the map, open markers, and read etymology in context.</p>
            </div>
            <span className="mt-4 inline-flex items-center gap-1 text-sm font-medium text-primary">
              Open map
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
            </span>
          </Link>

          <div className="surface-glass flex flex-col justify-between rounded-2xl p-6 md:col-span-2 lg:col-span-1">
            <div>
              <div className="mb-3 inline-flex rounded-lg bg-primary/10 p-2 text-primary">
                <Shuffle className="h-6 w-6" />
              </div>
              <h2 className="mb-1 font-display text-xl font-semibold text-foreground">Surprise me</h2>
              <p className="text-sm text-muted-foreground">
                Jump to a random street that already has an etymology suggestion.
              </p>
            </div>
            <button
              type="button"
              onClick={onSurprise}
              disabled={randomBusy}
              className="mt-4 inline-flex items-center justify-center gap-2 rounded-xl bg-primary px-4 py-3 text-sm font-medium text-primary-foreground transition-opacity disabled:opacity-60"
            >
              {randomBusy ? <Loader2 className="h-5 w-5 animate-spin" /> : <Shuffle className="h-5 w-5" />}
              {randomBusy ? 'Picking…' : 'Random street'}
            </button>
          </div>
        </div>

        <div className="mb-10">
          <h2 className="mb-3 font-display text-xl font-semibold text-foreground">Browse by county</h2>
          <p className="mb-4 text-sm text-muted-foreground">
            Sample of counties from the catalogue (opens search with that filter).
          </p>
          {loading ? (
            <div className="flex py-8">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          ) : (
            <div className="flex flex-wrap gap-2">
              {countyLinks.map((c) => (
                <Link
                  key={c}
                  to={buildSearchPath({ county: c })}
                  className="rounded-full border border-border bg-card/80 px-3 py-1.5 text-sm text-foreground transition-colors hover:border-primary/30 hover:bg-muted/60"
                >
                  {c}
                </Link>
              ))}
            </div>
          )}
        </div>

        <div>
          <div className="mb-4 flex items-center gap-2">
            <Clock className="h-5 w-5 text-primary" />
            <h2 className="font-display text-xl font-semibold text-foreground">Recently updated</h2>
          </div>
          {loading ? (
            <div className="flex justify-center py-16">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          ) : recent.length === 0 ? (
            <p className="text-muted-foreground">No streets to show yet.</p>
          ) : (
            <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
              {recent.map((s) => (
                <Link
                  key={s.id}
                  to={`/street/${s.id}`}
                  className="group flex items-center justify-between gap-3 rounded-2xl border border-border bg-card/50 px-4 py-3 transition-colors hover:border-primary/25 hover:bg-muted/40"
                >
                  <div className="min-w-0">
                    <div className="mb-0.5 flex items-center gap-2 text-xs text-muted-foreground">
                      <MapPin className="h-3.5 w-3.5 shrink-0 text-primary" />
                      <span className="truncate">{[s.city, s.county].filter(Boolean).join(', ') || 'UK'}</span>
                    </div>
                    <div className="truncate font-medium text-foreground group-hover:text-primary">{s.name}</div>
                  </div>
                  <ChevronRight className="h-4 w-4 shrink-0 text-muted-foreground group-hover:text-primary" />
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
