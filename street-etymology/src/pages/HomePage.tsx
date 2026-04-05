import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { SearchBar } from '../components/SearchBar';
import { MapView } from '../components/MapView';
import { NewsletterSignup } from '../components/NewsletterSignup';
import { supabase, Street } from '../lib/supabase';
import { fetchRandomStreetIdWithEtymology } from '../lib/explore';
import { usePageMeta } from '../hooks/usePageMeta';
import {
  MapPin,
  BookOpen,
  Users,
  Clock,
  ArrowRight,
  ChevronRight,
  Landmark,
  Scroll,
  Shuffle,
  Loader2,
  Compass,
} from 'lucide-react';
import toast from 'react-hot-toast';

export function HomePage() {
  usePageMeta({
    title: 'Street Etymology UK',
    description:
      'Discover the linguistic heritage of UK street names — search, map, and community-sourced etymologies.',
  });

  const navigate = useNavigate();
  const [randomBusy, setRandomBusy] = useState(false);
  const [featuredStreets, setFeaturedStreets] = useState<Street[]>([]);
  const [stats, setStats] = useState({ streets: 0, contributions: 0, cities: 0 });

  useEffect(() => {
    async function loadData() {
      const { data: streets } = await supabase
        .from('streets')
        .select('*')
        .eq('etymology_verified', true)
        .not('etymology_suggestion', 'is', null)
        .limit(6);

      if (streets) setFeaturedStreets(streets);

      const { count: streetCount } = await supabase.from('streets').select('*', { count: 'exact', head: true });

      const { count: contributionCount } = await supabase
        .from('contributions')
        .select('*', { count: 'exact', head: true });

      const { data: cities } = await supabase.from('streets').select('city').not('city', 'is', null);

      const uniqueCities = new Set(cities?.map((c) => c.city)).size;

      setStats({
        streets: streetCount || 0,
        contributions: contributionCount || 0,
        cities: uniqueCities,
      });
    }

    loadData();
  }, []);

  const onSurprise = async () => {
    setRandomBusy(true);
    try {
      const sid = await fetchRandomStreetIdWithEtymology();
      if (!sid) {
        toast.error('No streets with etymology found');
        return;
      }
      navigate(`/street/${sid}`);
    } finally {
      setRandomBusy(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Hero — light: warm paper + rose wash; dark: same structure, warm charcoal (not grey-blue) */}
      <section className="relative overflow-hidden border-b border-border bg-gradient-to-b from-accent/40 via-background to-background dark:from-muted/80 dark:via-background dark:to-background">
        <div
          className="pointer-events-none absolute inset-0 bg-[length:28px_28px] bg-grid-fine opacity-[0.35] dark:opacity-25"
          aria-hidden
        />
        <div className="pointer-events-none absolute inset-0 bg-hero-mesh opacity-90 dark:opacity-100" aria-hidden />

        <div className="relative mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:px-8 lg:py-28">
          <div className="mx-auto max-w-4xl text-center">
            <div className="mb-8 inline-flex items-center gap-2 rounded-full border border-border bg-card/80 px-4 py-2 text-sm text-muted-foreground shadow-paper backdrop-blur-sm dark:bg-card/60 dark:shadow-paper-dark">
              <Scroll className="h-4 w-4 text-primary" />
              <span>British street etymology · open research</span>
            </div>

            <h1 className="mb-6 font-display text-4xl font-bold leading-[1.08] tracking-tight text-foreground sm:text-5xl lg:text-6xl">
              Discover the stories
              <span className="mt-1 block text-primary">behind every street</span>
            </h1>

            <p className="mx-auto mb-10 max-w-2xl text-lg text-muted-foreground sm:text-xl">
              Uncover the linguistic heritage in UK street names — from Roman roads to Victorian terraces — in a
              calm, editorial space built for reading.
            </p>

            <div className="mx-auto mb-10 max-w-2xl">
              <SearchBar large placeholder="Search for a street (e.g. Baker Street, Piccadilly)…" />
            </div>

            <div className="flex flex-wrap justify-center gap-3 text-sm">
              <Link
                to="/search"
                className="inline-flex items-center gap-2 rounded-xl bg-primary px-6 py-3 font-medium text-primary-foreground shadow-paper transition-opacity hover:opacity-90 dark:shadow-paper-dark"
              >
                <span>Browse all streets</span>
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link
                to="/map"
                className="inline-flex items-center gap-2 rounded-xl border border-border bg-card/90 px-6 py-3 font-medium text-foreground shadow-sm backdrop-blur-sm transition-colors hover:bg-muted/80"
              >
                <MapPin className="h-4 w-4 text-primary" />
                <span>Explore map</span>
              </Link>
              <Link
                to="/explore"
                className="inline-flex items-center gap-2 rounded-xl border border-border bg-card/90 px-6 py-3 font-medium text-foreground shadow-sm backdrop-blur-sm transition-colors hover:bg-muted/80"
              >
                <Compass className="h-4 w-4 text-primary" />
                <span>Explore hub</span>
              </Link>
              <button
                type="button"
                onClick={onSurprise}
                disabled={randomBusy}
                className="inline-flex items-center gap-2 rounded-xl border border-border bg-card/90 px-6 py-3 font-medium text-foreground shadow-sm backdrop-blur-sm transition-colors hover:bg-muted/80 disabled:opacity-60"
              >
                {randomBusy ? <Loader2 className="h-4 w-4 animate-spin text-primary" /> : <Shuffle className="h-4 w-4 text-primary" />}
                <span>Surprise me</span>
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="border-b border-border bg-muted/30 py-14 dark:bg-muted/20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-3 gap-8">
            <div className="text-center">
              <div className="mb-1 font-mono text-3xl font-semibold tabular-nums text-primary sm:text-4xl">
                {stats.streets.toLocaleString()}
              </div>
              <div className="text-sm text-muted-foreground">Streets catalogued</div>
            </div>
            <div className="text-center">
              <div className="mb-1 font-mono text-3xl font-semibold tabular-nums text-primary sm:text-4xl">
                {stats.cities}
              </div>
              <div className="text-sm text-muted-foreground">UK cities</div>
            </div>
            <div className="text-center">
              <div className="mb-1 font-mono text-3xl font-semibold tabular-nums text-primary sm:text-4xl">
                {stats.contributions}
              </div>
              <div className="text-sm text-muted-foreground">Contributions</div>
            </div>
          </div>
        </div>
      </section>

      {/* Featured */}
      <section className="py-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mb-10 flex items-center justify-between">
            <div>
              <h2 className="font-display text-2xl font-bold text-foreground sm:text-3xl">Featured etymologies</h2>
              <p className="mt-1 text-muted-foreground">Verified origins from across the UK</p>
            </div>
            <Link
              to="/search"
              className="hidden items-center gap-1 font-medium text-primary transition-opacity hover:opacity-80 sm:flex"
            >
              <span>View all</span>
              <ChevronRight className="h-4 w-4" />
            </Link>
          </div>

          <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
            {featuredStreets.map((street) => (
              <Link
                key={street.id}
                to={`/street/${street.id}`}
                className="group surface-glass rounded-2xl p-6 transition-all hover:border-primary/25 hover:shadow-paper dark:hover:border-primary/20 dark:hover:shadow-paper-dark"
              >
                <div className="mb-3 flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    <MapPin className="h-5 w-5 shrink-0 text-primary" />
                    <span className="text-sm text-muted-foreground">
                      {street.city}, {street.county}
                    </span>
                  </div>
                  <span className="rounded-full bg-emerald-500/15 px-2 py-0.5 text-xs font-medium text-emerald-800 dark:bg-emerald-500/20 dark:text-emerald-300">
                    Verified
                  </span>
                </div>

                <h3 className="mb-2 text-xl font-semibold text-foreground transition-colors group-hover:text-primary">
                  {street.name}
                </h3>

                <p className="mb-3 line-clamp-3 text-sm text-muted-foreground">{street.etymology_suggestion}</p>

                {street.first_recorded_date && (
                  <div className="flex items-center gap-1 font-mono text-xs text-muted-foreground">
                    <Clock className="h-3 w-3" />
                    <span>First recorded: {street.first_recorded_date}</span>
                  </div>
                )}
              </Link>
            ))}
          </div>

          <div className="mt-8 text-center sm:hidden">
            <Link
              to="/search"
              className="inline-flex items-center gap-2 rounded-xl border border-border bg-muted/50 px-6 py-3 font-medium text-foreground transition-colors hover:bg-muted"
            >
              <span>View all streets</span>
              <ChevronRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* Map */}
      <section className="border-y border-border bg-muted/25 py-16 dark:bg-muted/15">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mb-8 text-center">
            <h2 className="mb-2 font-display text-2xl font-bold text-foreground sm:text-3xl">Explore the UK map</h2>
            <p className="mx-auto max-w-2xl text-muted-foreground">
              Navigate geographically — markers open street detail and etymology context.
            </p>
          </div>

          <div className="overflow-hidden rounded-2xl border border-border shadow-paper dark:shadow-paper-dark">
            <MapView height="500px" />
          </div>

          <div className="mt-8 text-center">
            <Link
              to="/map"
              className="inline-flex items-center gap-2 rounded-xl bg-primary px-6 py-3 font-medium text-primary-foreground shadow-sm transition-opacity hover:opacity-90"
            >
              <MapPin className="h-5 w-5" />
              <span>Open full map</span>
            </Link>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="py-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mb-12 text-center">
            <h2 className="mb-2 font-display text-2xl font-bold text-foreground sm:text-3xl">How it works</h2>
            <p className="text-muted-foreground">Research, discover, contribute — same workflow in any theme.</p>
          </div>

          <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
            {[
              {
                icon: BookOpen,
                title: 'Research',
                body: 'Browse a growing corpus of UK streets with sourced etymologies and archival context.',
              },
              {
                icon: Landmark,
                title: 'Discover',
                body: 'Use the map to explore place and language together — geography as reading aid.',
              },
              {
                icon: Users,
                title: 'Contribute',
                body: 'Submit suggestions for review and help expand verified public knowledge.',
              },
            ].map(({ icon: Icon, title, body }) => (
              <div key={title} className="text-center">
                <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl border border-border bg-accent/60 dark:bg-accent/40">
                  <Icon className="h-8 w-8 text-primary" />
                </div>
                <h3 className="mb-2 text-lg font-semibold text-foreground">{title}</h3>
                <p className="text-sm text-muted-foreground">{body}</p>
              </div>
            ))}
          </div>

          <div className="mt-12 text-center">
            <Link
              to="/contribute"
              className="inline-flex items-center gap-2 rounded-xl border border-border bg-foreground px-6 py-3 font-medium text-background transition-opacity hover:opacity-90 dark:border-0"
            >
              <span>Start contributing</span>
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* Newsletter */}
      <section className="border-t border-border bg-muted/30 py-16 dark:bg-muted/20">
        <div className="mx-auto max-w-2xl px-4 sm:px-6 lg:px-8">
          <NewsletterSignup />
        </div>
      </section>
    </div>
  );
}
