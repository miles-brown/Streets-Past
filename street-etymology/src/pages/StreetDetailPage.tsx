import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { supabase, Street, Contribution } from '../lib/supabase';
import { MapView } from '../components/MapView';
import { ContributionForm } from '../components/ContributionForm';
import { useAuth } from '../contexts/AuthContext';
import {
  MapPin,
  Clock,
  BookOpen,
  ChevronRight,
  Share2,
  Loader2,
  CheckCircle,
  XCircle,
  AlertCircle,
  Sparkles,
  Download,
} from 'lucide-react';
import toast from 'react-hot-toast';

export function StreetDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const [street, setStreet] = useState<Street | null>(null);
  const [contributions, setContributions] = useState<Contribution[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isGeneratingAI, setIsGeneratingAI] = useState(false);
  const [aiSuggestion, setAiSuggestion] = useState<string | null>(null);

  useEffect(() => {
    async function loadStreet() {
      if (!id) return;

      setIsLoading(true);
      try {
        const { data: streetData, error: streetError } = await supabase
          .from('streets')
          .select('*')
          .eq('id', id)
          .maybeSingle();

        if (streetError) throw streetError;
        setStreet(streetData);

        const { data: contributionsData } = await supabase
          .from('contributions')
          .select('*')
          .eq('street_id', id)
          .eq('status', 'approved')
          .order('created_at', { ascending: false });

        setContributions(contributionsData || []);
      } catch (error) {
        console.error('Error loading street:', error);
        toast.error('Failed to load street details');
      } finally {
        setIsLoading(false);
      }
    }

    loadStreet();
  }, [id]);

  const generateAISuggestion = async () => {
    if (!street) return;

    setIsGeneratingAI(true);
    try {
      const { data, error } = await supabase.functions.invoke('suggest-etymology', {
        body: { streetName: street.name },
      });

      if (error) throw error;

      if (data?.data?.etymology) {
        setAiSuggestion(data.data.etymology);
        toast.success('AI suggestion generated');
      }
    } catch (error) {
      console.error('AI suggestion error:', error);
      toast.error('Failed to generate AI suggestion');
    } finally {
      setIsGeneratingAI(false);
    }
  };

  const shareStreet = async () => {
    const url = window.location.href;
    const text = `Discover the etymology of ${street?.name} in the UK`;

    if (navigator.share) {
      try {
        await navigator.share({ title: street?.name, text, url });
      } catch {
        /* noop */
      }
    } else {
      await navigator.clipboard.writeText(url);
      toast.success('Link copied to clipboard');
    }
  };

  const exportData = () => {
    if (!street) return;

    const data = {
      name: street.name,
      location: {
        city: street.city,
        county: street.county,
        postcode_area: street.postcode_area,
        coordinates: {
          latitude: street.latitude,
          longitude: street.longitude,
        },
      },
      etymology: street.etymology_suggestion,
      verified: street.etymology_verified,
      first_recorded: street.first_recorded_date,
      historical_notes: street.historical_notes,
      exported_at: new Date().toISOString(),
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    const safeName = String(street.name ?? 'street').replace(/\s+/g, '_');
    a.download = `${safeName}_etymology.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <Loader2 className="h-10 w-10 animate-spin text-primary" />
      </div>
    );
  }

  if (!street) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background px-4">
        <div className="text-center">
          <XCircle className="mx-auto mb-4 h-16 w-16 text-muted-foreground/40" />
          <h2 className="mb-2 text-xl font-semibold text-foreground">Street not found</h2>
          <p className="mb-4 text-muted-foreground">The requested street could not be found.</p>
          <Link
            to="/search"
            className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 font-medium text-primary-foreground transition-opacity hover:opacity-90"
          >
            <span>Back to search</span>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="border-b border-border bg-card/50">
        <div className="mx-auto max-w-7xl px-4 py-3 sm:px-6 lg:px-8">
          <nav className="flex items-center gap-2 text-sm text-muted-foreground">
            <Link to="/" className="transition-colors hover:text-foreground">
              Home
            </Link>
            <ChevronRight className="h-4 w-4 shrink-0 opacity-60" />
            <Link to="/search" className="transition-colors hover:text-foreground">
              Search
            </Link>
            <ChevronRight className="h-4 w-4 shrink-0 opacity-60" />
            <span className="font-medium text-foreground">{street.name}</span>
          </nav>
        </div>
      </div>

      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
          <div className="space-y-6 lg:col-span-2">
            <div className="surface-glass rounded-2xl p-6">
              <div className="mb-4 flex items-start justify-between gap-4">
                <div>
                  <div className="mb-2 flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
                    <MapPin className="h-4 w-4 shrink-0 text-primary" />
                    <span>{[street.city, street.county].filter(Boolean).join(', ')}</span>
                    {street.postcode_area && (
                      <span className="rounded-full bg-muted px-2 py-0.5 font-mono text-xs text-muted-foreground">
                        {street.postcode_area}
                      </span>
                    )}
                  </div>
                  <h1 className="font-display text-3xl font-bold text-foreground">{street.name}</h1>
                </div>

                <div className="flex shrink-0 items-center gap-2">
                  {street.etymology_verified ? (
                    <span className="flex items-center gap-1 rounded-full bg-emerald-500/15 px-3 py-1 text-sm font-medium text-emerald-800 dark:text-emerald-300">
                      <CheckCircle className="h-4 w-4" />
                      <span>Verified</span>
                    </span>
                  ) : (
                    <span className="flex items-center gap-1 rounded-full bg-accent px-3 py-1 text-sm font-medium text-accent-foreground">
                      <AlertCircle className="h-4 w-4" />
                      <span>Unverified</span>
                    </span>
                  )}
                </div>
              </div>

              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={shareStreet}
                  className="flex items-center gap-1 rounded-lg px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
                >
                  <Share2 className="h-4 w-4" />
                  <span>Share</span>
                </button>
                <button
                  type="button"
                  onClick={exportData}
                  className="flex items-center gap-1 rounded-lg px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
                >
                  <Download className="h-4 w-4" />
                  <span>Export</span>
                </button>
              </div>
            </div>

            <div className="surface-glass rounded-2xl p-6">
              <div className="mb-4 flex items-center gap-2">
                <BookOpen className="h-5 w-5 text-primary" />
                <h2 className="text-xl font-semibold text-foreground">Etymology</h2>
              </div>

              {street.etymology_suggestion ? (
                <div className="prose prose-sm max-w-none dark:prose-invert">
                  <p className="whitespace-pre-line leading-relaxed text-muted-foreground">{street.etymology_suggestion}</p>
                </div>
              ) : (
                <div className="rounded-xl border border-border bg-muted/40 p-4 text-center">
                  <p className="mb-4 text-muted-foreground">The etymology of this street has not yet been researched.</p>
                  <button
                    type="button"
                    onClick={generateAISuggestion}
                    disabled={isGeneratingAI}
                    className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 font-medium text-primary-foreground transition-opacity disabled:opacity-50"
                  >
                    {isGeneratingAI ? (
                      <Loader2 className="h-5 w-5 animate-spin" />
                    ) : (
                      <Sparkles className="h-5 w-5" />
                    )}
                    <span>Generate AI suggestion</span>
                  </button>
                </div>
              )}

              {street.etymology_source && (
                <div className="mt-4 border-t border-border pt-4">
                  <p className="text-sm text-muted-foreground">
                    <span className="font-medium text-foreground">Source:</span> {street.etymology_source}
                  </p>
                </div>
              )}
            </div>

            {aiSuggestion && (
              <div className="rounded-2xl border border-primary/20 bg-accent/60 p-6 dark:bg-accent/30">
                <div className="mb-4 flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-primary" />
                  <h3 className="text-lg font-semibold text-foreground">AI-generated etymology</h3>
                </div>
                <p className="whitespace-pre-line leading-relaxed text-muted-foreground">{aiSuggestion}</p>
                <p className="mt-4 text-xs text-muted-foreground">
                  This suggestion was generated by AI and may require verification.
                </p>
              </div>
            )}

            {street.historical_notes && (
              <div className="surface-glass rounded-2xl p-6">
                <h2 className="mb-4 text-xl font-semibold text-foreground">Historical notes</h2>
                <p className="leading-relaxed text-muted-foreground">{street.historical_notes}</p>
              </div>
            )}

            {street.first_recorded_date && (
              <div className="surface-glass rounded-2xl p-6">
                <div className="flex items-center gap-2">
                  <Clock className="h-5 w-5 text-primary" />
                  <span className="text-muted-foreground">
                    <span className="font-medium text-foreground">First recorded:</span>{' '}
                    <span className="font-mono text-sm">{street.first_recorded_date}</span>
                  </span>
                </div>
              </div>
            )}

            {contributions.length > 0 && (
              <div className="surface-glass rounded-2xl p-6">
                <h2 className="mb-4 text-xl font-semibold text-foreground">Community contributions</h2>
                <div className="space-y-4">
                  {contributions.map((contribution) => (
                    <div key={contribution.id} className="rounded-xl border border-border bg-muted/30 p-4">
                      <p className="mb-2 text-muted-foreground">{contribution.etymology_suggestion}</p>
                      {contribution.sources && (
                        <p className="text-sm text-muted-foreground">
                          <span className="font-medium text-foreground">Sources:</span> {contribution.sources}
                        </p>
                      )}
                      <p className="mt-2 text-xs text-muted-foreground/80">
                        Contributed on {new Date(contribution.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="space-y-6">
            {street.latitude && street.longitude && (
              <div className="surface-glass overflow-hidden rounded-2xl">
                <MapView selectedStreet={street} height="300px" />
                <div className="border-t border-border p-4">
                  <p className="text-sm text-muted-foreground">
                    <span className="font-medium text-foreground">Coordinates:</span>{' '}
                    <span className="font-mono text-xs">
                      {street.latitude.toFixed(4)}, {street.longitude.toFixed(4)}
                    </span>
                  </p>
                </div>
              </div>
            )}

            <div className="surface-glass rounded-2xl p-6">
              <h3 className="mb-4 text-lg font-semibold text-foreground">Contribute etymology</h3>
              <p className="mb-4 text-sm text-muted-foreground">
                Share your knowledge about the origin of this street name.
                {!user && ' Sign in for faster submissions.'}
              </p>
              <ContributionForm streetId={street.id} streetName={street.name} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
