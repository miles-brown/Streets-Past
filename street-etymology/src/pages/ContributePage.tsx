import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { usePageMeta } from '../hooks/usePageMeta';
import { BookOpen, Search, LogIn, MapPin, CheckCircle } from 'lucide-react';

export function ContributePage() {
  const { user } = useAuth();

  usePageMeta({
    title: 'Contribute',
    description:
      'Submit well-sourced etymology for UK streets: what makes a good contribution and how to get started.',
  });

  return (
    <div className="min-h-screen bg-background py-10">
      <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
        <h1 className="mb-3 font-display text-3xl font-bold text-foreground">Contribute etymology</h1>
        <p className="mb-8 text-lg text-muted-foreground">
          Help grow verified, readable histories for UK street names. Contributions are reviewed before they appear
          publicly.
        </p>

        <div className="surface-glass mb-8 space-y-6 rounded-2xl p-6 md:p-8">
          <div className="flex gap-3">
            <div className="mt-0.5 shrink-0 rounded-lg bg-primary/10 p-2 text-primary">
              <BookOpen className="h-5 w-5" />
            </div>
            <div>
              <h2 className="mb-2 font-display text-lg font-semibold text-foreground">What makes a good submission</h2>
              <ul className="list-inside list-disc space-y-2 text-sm text-muted-foreground">
                <li>Clear explanation of the linguistic origin (language, root, meaning).</li>
                <li>Reliable sources: place-name society volumes, OED, OS maps, local histories — cite them.</li>
                <li>Distinguish evidence from guesswork; note uncertainty where sources disagree.</li>
              </ul>
            </div>
          </div>

          <div className="flex gap-3 border-t border-border pt-6">
            <div className="mt-0.5 shrink-0 rounded-lg bg-primary/10 p-2 text-primary">
              <CheckCircle className="h-5 w-5" />
            </div>
            <div>
              <h2 className="mb-2 font-display text-lg font-semibold text-foreground">How it works</h2>
              <p className="text-sm text-muted-foreground">
                Find a street, open its page, and use the contribution form in the sidebar. Signed-in users can track
                status from their profile. Moderators may ask for clearer citations before approval.
              </p>
            </div>
          </div>
        </div>

        <div className="flex flex-col gap-3 sm:flex-row sm:flex-wrap">
          <Link
            to="/search"
            className="inline-flex items-center justify-center gap-2 rounded-xl bg-primary px-6 py-3 font-medium text-primary-foreground shadow-sm transition-opacity hover:opacity-90"
          >
            <Search className="h-5 w-5" />
            Find a street
          </Link>
          <Link
            to="/explore"
            className="inline-flex items-center justify-center gap-2 rounded-xl border border-border bg-card px-6 py-3 font-medium text-foreground transition-colors hover:bg-muted/80"
          >
            <MapPin className="h-5 w-5 text-primary" />
            Explore
          </Link>
          {!user && (
            <Link
              to="/login"
              className="inline-flex items-center justify-center gap-2 rounded-xl border border-border px-6 py-3 font-medium text-foreground transition-colors hover:bg-muted/80"
            >
              <LogIn className="h-5 w-5" />
              Sign in to contribute
            </Link>
          )}
        </div>
      </div>
    </div>
  );
}
