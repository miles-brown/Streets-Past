import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { supabase, Street } from '../lib/supabase';
import { Search, MapPin, Filter, Clock, ChevronDown, Loader2, ArrowUpDown, CheckCircle } from 'lucide-react';

export function SearchPage() {
  const [streets, setStreets] = useState<Street[]>([]);
  const [filteredStreets, setFilteredStreets] = useState<Street[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCounty, setSelectedCounty] = useState('');
  const [selectedCity, setSelectedCity] = useState('');
  const [verifiedOnly, setVerifiedOnly] = useState(false);
  const [sortBy, setSortBy] = useState<'name' | 'city' | 'date'>('name');
  const [counties, setCounties] = useState<string[]>([]);
  const [cities, setCities] = useState<string[]>([]);
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    async function loadStreets() {
      setIsLoading(true);
      try {
        const { data, error } = await supabase.from('streets').select('*').order('name');

        if (error) throw error;

        setStreets(data || []);
        setFilteredStreets(data || []);

        const uniqueCounties = [...new Set(data?.map((s) => s.county).filter(Boolean))] as string[];
        const uniqueCities = [...new Set(data?.map((s) => s.city).filter(Boolean))] as string[];

        setCounties(uniqueCounties.sort());
        setCities(uniqueCities.sort());
      } catch (error) {
        console.error('Error loading streets:', error);
      } finally {
        setIsLoading(false);
      }
    }

    loadStreets();
  }, []);

  useEffect(() => {
    let result = [...streets];

    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      result = result.filter(
        (s) =>
          s.name.toLowerCase().includes(query) || s.etymology_suggestion?.toLowerCase().includes(query)
      );
    }

    if (selectedCounty) {
      result = result.filter((s) => s.county === selectedCounty);
    }

    if (selectedCity) {
      result = result.filter((s) => s.city === selectedCity);
    }

    if (verifiedOnly) {
      result = result.filter((s) => s.etymology_verified);
    }

    result.sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'city':
          return (a.city || '').localeCompare(b.city || '');
        case 'date':
          return (a.first_recorded_date || '').localeCompare(b.first_recorded_date || '');
        default:
          return 0;
      }
    });

    setFilteredStreets(result);
  }, [streets, searchQuery, selectedCounty, selectedCity, verifiedOnly, sortBy]);

  const clearFilters = () => {
    setSearchQuery('');
    setSelectedCounty('');
    setSelectedCity('');
    setVerifiedOnly(false);
    setSortBy('name');
  };

  const activeFilterCount = [selectedCounty, selectedCity, verifiedOnly].filter(Boolean).length;

  return (
    <div className="min-h-screen bg-background py-8">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="mb-2 font-display text-3xl font-bold text-foreground">Search UK streets</h1>
          <p className="text-muted-foreground">Browse and filter street names and etymologies.</p>
        </div>

        <div className="surface-glass mb-6 rounded-2xl p-4">
          <div className="flex flex-col gap-4 lg:flex-row">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by street name or etymology…"
                className="w-full rounded-lg border border-border bg-background py-3 pl-10 pr-4 text-foreground placeholder:text-muted-foreground focus:border-primary/40 focus:outline-none focus:ring-2 focus:ring-ring/30"
              />
            </div>

            <button
              type="button"
              onClick={() => setShowFilters(!showFilters)}
              className={`flex items-center gap-2 rounded-lg border px-4 py-3 transition-colors ${
                showFilters || activeFilterCount > 0
                  ? 'border-primary/30 bg-accent text-accent-foreground'
                  : 'border-border text-muted-foreground hover:bg-muted/80'
              }`}
            >
              <Filter className="h-5 w-5" />
              <span>Filters</span>
              {activeFilterCount > 0 && (
                <span className="flex h-5 w-5 items-center justify-center rounded-full bg-primary text-xs text-primary-foreground">
                  {activeFilterCount}
                </span>
              )}
              <ChevronDown className={`h-4 w-4 transition-transform ${showFilters ? 'rotate-180' : ''}`} />
            </button>

            <div className="relative">
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
                className="w-full appearance-none rounded-lg border border-border bg-background py-3 pl-10 pr-10 text-foreground focus:border-primary/40 focus:outline-none focus:ring-2 focus:ring-ring/30 lg:w-auto"
              >
                <option value="name">Sort by name</option>
                <option value="city">Sort by city</option>
                <option value="date">Sort by date</option>
              </select>
              <ArrowUpDown className="pointer-events-none absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
            </div>
          </div>

          {showFilters && (
            <div className="mt-4 grid grid-cols-1 gap-4 border-t border-border pt-4 sm:grid-cols-2 lg:grid-cols-4">
              <div>
                <label className="mb-1 block text-sm font-medium text-foreground">County</label>
                <select
                  value={selectedCounty}
                  onChange={(e) => setSelectedCounty(e.target.value)}
                  className="w-full rounded-lg border border-border bg-background px-3 py-2 text-foreground focus:border-primary/40 focus:outline-none focus:ring-2 focus:ring-ring/30"
                >
                  <option value="">All counties</option>
                  {counties.map((county) => (
                    <option key={county} value={county}>
                      {county}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="mb-1 block text-sm font-medium text-foreground">City</label>
                <select
                  value={selectedCity}
                  onChange={(e) => setSelectedCity(e.target.value)}
                  className="w-full rounded-lg border border-border bg-background px-3 py-2 text-foreground focus:border-primary/40 focus:outline-none focus:ring-2 focus:ring-ring/30"
                >
                  <option value="">All cities</option>
                  {cities.map((city) => (
                    <option key={city} value={city}>
                      {city}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex items-end">
                <label className="flex cursor-pointer items-center gap-2">
                  <input
                    type="checkbox"
                    checked={verifiedOnly}
                    onChange={(e) => setVerifiedOnly(e.target.checked)}
                    className="h-5 w-5 rounded border-border text-primary focus:ring-ring/40"
                  />
                  <span className="text-sm text-foreground">Verified only</span>
                </label>
              </div>

              <div className="flex items-end">
                <button
                  type="button"
                  onClick={clearFilters}
                  className="w-full rounded-lg px-4 py-2 text-sm text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
                >
                  Clear all filters
                </button>
              </div>
            </div>
          )}
        </div>

        <div className="mb-4 flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            Showing {filteredStreets.length} of {streets.length} streets
          </p>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        ) : filteredStreets.length === 0 ? (
          <div className="surface-glass rounded-2xl py-20 text-center">
            <Search className="mx-auto mb-4 h-16 w-16 text-muted-foreground/40" />
            <h3 className="mb-2 text-lg font-semibold text-foreground">No streets found</h3>
            <p className="mb-4 text-muted-foreground">Try adjusting your search or filters.</p>
            <button type="button" onClick={clearFilters} className="font-medium text-primary hover:opacity-90">
              Clear all filters
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            {filteredStreets.map((street) => (
              <Link
                key={street.id}
                to={`/street/${street.id}`}
                className="group surface-glass rounded-2xl p-5 transition-all hover:border-primary/25 hover:shadow-paper dark:hover:shadow-paper-dark"
              >
                <div className="mb-2 flex items-start justify-between">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <MapPin className="h-4 w-4 shrink-0 text-primary" />
                    <span>{street.city || street.county}</span>
                  </div>
                  {street.etymology_verified && (
                    <CheckCircle className="h-5 w-5 shrink-0 text-emerald-600 dark:text-emerald-400" />
                  )}
                </div>

                <h3 className="mb-2 text-lg font-semibold text-foreground transition-colors group-hover:text-primary">
                  {street.name}
                </h3>

                {street.etymology_suggestion ? (
                  <p className="mb-3 line-clamp-2 text-sm text-muted-foreground">{street.etymology_suggestion}</p>
                ) : (
                  <p className="mb-3 text-sm italic text-muted-foreground/70">Etymology not yet researched</p>
                )}

                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  {street.first_recorded_date && (
                    <div className="flex items-center gap-1 font-mono">
                      <Clock className="h-3 w-3" />
                      <span>{street.first_recorded_date}</span>
                    </div>
                  )}
                  {street.postcode_area && (
                    <span className="rounded bg-muted px-2 py-0.5 font-mono">{street.postcode_area}</span>
                  )}
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
