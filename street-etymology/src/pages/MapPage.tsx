import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { MapView } from '../components/MapView';
import { SearchBar } from '../components/SearchBar';
import { ThemeToggle } from '../components/ThemeToggle';
import { Street } from '../lib/supabase';
import { usePageMeta } from '../hooks/usePageMeta';
import { MapPin, List, Grid, X, Clock, ChevronRight, CheckCircle } from 'lucide-react';

export function MapPage() {
  usePageMeta({
    title: 'UK street map',
    description: 'Interactive map of UK streets — open markers to read names and etymology.',
  });

  const navigate = useNavigate();
  const [selectedStreet, setSelectedStreet] = useState<Street | null>(null);
  const [showSidebar, setShowSidebar] = useState(true);

  const handleStreetSelect = (street: Street) => {
    setSelectedStreet(street);
    setShowSidebar(true);
  };

  return (
    <div className="flex h-screen flex-col">
      <div className="border-b border-border bg-card/90 p-4 backdrop-blur-md">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4">
          <Link to="/" className="flex shrink-0 items-center gap-2 text-foreground hover:opacity-80">
            <MapPin className="h-6 w-6 text-primary" />
            <h1 className="font-display text-xl font-bold">UK street map</h1>
          </Link>

          <div className="max-w-xl flex-1">
            <SearchBar onSelect={handleStreetSelect} placeholder="Search for a street…" />
          </div>

          <div className="hidden items-center gap-2 md:flex">
            <ThemeToggle />
            <button
              type="button"
              onClick={() => setShowSidebar(!showSidebar)}
              className={`rounded-lg p-2 transition-colors ${
                showSidebar ? 'bg-accent text-accent-foreground' : 'text-muted-foreground hover:bg-muted'
              }`}
              title={showSidebar ? 'Hide sidebar' : 'Show sidebar'}
            >
              <List className="h-5 w-5" />
            </button>
          </div>

          <div className="flex md:hidden">
            <ThemeToggle />
          </div>
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden">
        <div className="relative flex-1">
          <MapView
            selectedStreet={selectedStreet}
            onStreetSelect={handleStreetSelect}
            height="100%"
          />

          {selectedStreet && (
            <div className="absolute bottom-4 left-4 right-4 surface-glass rounded-xl p-4 md:hidden">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="mb-1 flex items-center gap-2 text-sm text-muted-foreground">
                    <MapPin className="h-4 w-4 text-primary" />
                    <span>
                      {selectedStreet.city}, {selectedStreet.county}
                    </span>
                  </div>
                  <h3 className="text-lg font-semibold text-foreground">{selectedStreet.name}</h3>
                  {selectedStreet.etymology_suggestion && (
                    <p className="mt-1 line-clamp-2 text-sm text-muted-foreground">
                      {selectedStreet.etymology_suggestion}
                    </p>
                  )}
                  <button
                    type="button"
                    onClick={() => navigate(`/street/${selectedStreet.id}`)}
                    className="mt-3 flex items-center gap-1 text-sm font-medium text-primary"
                  >
                    <span>View details</span>
                    <ChevronRight className="h-4 w-4" />
                  </button>
                </div>
                <button
                  type="button"
                  onClick={() => setSelectedStreet(null)}
                  className="p-1 text-muted-foreground hover:text-foreground"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
            </div>
          )}
        </div>

        {showSidebar && (
          <div className="hidden w-96 overflow-y-auto border-l border-border bg-card md:block">
            {selectedStreet ? (
              <div className="p-6">
                <div className="mb-4 flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    {selectedStreet.etymology_verified ? (
                      <span className="flex items-center gap-1 rounded-full bg-emerald-500/15 px-2 py-0.5 text-xs font-medium text-emerald-800 dark:bg-emerald-500/20 dark:text-emerald-300">
                        <CheckCircle className="h-3 w-3" />
                        <span>Verified</span>
                      </span>
                    ) : (
                      <span className="rounded-full bg-accent px-2 py-0.5 text-xs font-medium text-accent-foreground">
                        Unverified
                      </span>
                    )}
                  </div>
                  <button
                    type="button"
                    onClick={() => setSelectedStreet(null)}
                    className="p-1 text-muted-foreground hover:text-foreground"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>

                <div className="mb-2 flex items-center gap-2 text-sm text-muted-foreground">
                  <MapPin className="h-4 w-4 text-primary" />
                  <span>{[selectedStreet.city, selectedStreet.county].filter(Boolean).join(', ')}</span>
                </div>

                <h2 className="mb-4 font-display text-2xl font-bold text-foreground">{selectedStreet.name}</h2>

                {selectedStreet.etymology_suggestion ? (
                  <div className="prose prose-sm mb-4 max-w-none">
                    <p className="leading-relaxed text-muted-foreground">{selectedStreet.etymology_suggestion}</p>
                  </div>
                ) : (
                  <p className="mb-4 italic text-muted-foreground">Etymology not yet researched</p>
                )}

                {selectedStreet.first_recorded_date && (
                  <div className="mb-4 flex items-center gap-2 border-b border-border pb-4 text-sm text-muted-foreground">
                    <Clock className="h-4 w-4" />
                    <span>First recorded: {selectedStreet.first_recorded_date}</span>
                  </div>
                )}

                {selectedStreet.latitude && selectedStreet.longitude && (
                  <div className="mb-6 font-mono text-sm text-muted-foreground">
                    <span className="font-sans font-medium text-foreground">Coordinates:</span>{' '}
                    {selectedStreet.latitude.toFixed(5)}, {selectedStreet.longitude.toFixed(5)}
                  </div>
                )}

                <button
                  type="button"
                  onClick={() => navigate(`/street/${selectedStreet.id}`)}
                  className="flex w-full items-center justify-center gap-2 rounded-lg bg-primary px-4 py-3 font-medium text-primary-foreground transition-opacity hover:opacity-90"
                >
                  <span>View full details</span>
                  <ChevronRight className="h-4 w-4" />
                </button>
              </div>
            ) : (
              <div className="p-6">
                <div className="py-12 text-center">
                  <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl border border-border bg-muted/50">
                    <Grid className="h-8 w-8 text-muted-foreground" />
                  </div>
                  <h3 className="mb-2 text-lg font-semibold text-foreground">Select a street</h3>
                  <p className="text-sm text-muted-foreground">
                    Click a marker or search to load etymology in this panel.
                  </p>
                </div>

                <div className="mt-8">
                  <h4 className="mb-3 text-sm font-semibold uppercase tracking-wider text-foreground">Quick tips</h4>
                  <ul className="space-y-3 text-sm text-muted-foreground">
                    <li className="flex items-start gap-2">
                      <MapPin className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
                      <span>Markers open street context here.</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <MapPin className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
                      <span>Scroll to zoom; drag to pan.</span>
                    </li>
                  </ul>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
