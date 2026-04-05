import { useState } from 'react';
import { supabase } from '../lib/supabase';
import { useAuth } from '../contexts/AuthContext';
import { Send, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import toast from 'react-hot-toast';

interface ContributionFormProps {
  streetId: string;
  streetName: string;
  onSuccess?: () => void;
}

const fieldClass =
  'w-full rounded-xl border border-border bg-card px-4 py-3 text-foreground placeholder:text-muted-foreground transition-all focus:border-primary/50 focus:outline-none focus:ring-2 focus:ring-ring/40 resize-none';

export function ContributionForm({ streetId, streetName, onSuccess }: ContributionFormProps) {
  const { user } = useAuth();
  const [etymology, setEtymology] = useState('');
  const [sources, setSources] = useState('');
  const [email, setEmail] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!etymology.trim()) {
      toast.error('Please provide an etymology suggestion');
      return;
    }

    const submitterEmail = user?.email || email;
    if (!submitterEmail) {
      toast.error('Please provide your email address');
      return;
    }

    setIsSubmitting(true);

    try {
      const { error } = await supabase.from('contributions').insert({
        street_id: streetId,
        user_id: user?.id || null,
        user_email: submitterEmail,
        etymology_suggestion: etymology.trim(),
        sources: sources.trim() || null,
        status: 'pending',
      });

      if (error) throw error;

      setSubmitted(true);
      toast.success('Thank you! Your contribution has been submitted for review.');

      onSuccess?.();
    } catch (error) {
      console.error('Submission error:', error);
      toast.error('Failed to submit contribution. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (submitted) {
    return (
      <div className="rounded-xl border border-emerald-500/25 bg-emerald-500/10 p-6 text-center dark:border-emerald-500/30 dark:bg-emerald-500/15">
        <CheckCircle className="mx-auto mb-4 h-12 w-12 text-emerald-600 dark:text-emerald-400" />
        <h3 className="mb-2 text-lg font-semibold text-foreground">Contribution submitted</h3>
        <p className="text-muted-foreground">
          Thank you for your contribution to the etymology of {streetName}. Our team will review your submission
          shortly.
        </p>
        <button
          type="button"
          onClick={() => {
            setSubmitted(false);
            setEtymology('');
            setSources('');
          }}
          className="mt-4 text-sm font-medium text-primary transition-colors hover:underline"
        >
          Submit another contribution
        </button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="etymology" className="mb-1 block text-sm font-medium text-foreground">
          Etymology suggestion *
        </label>
        <textarea
          id="etymology"
          value={etymology}
          onChange={(e) => setEtymology(e.target.value)}
          rows={4}
          className={fieldClass}
          placeholder="Share your knowledge about the origin and meaning of this street name..."
          required
        />
        <p className="mt-1 text-xs text-muted-foreground">
          Include linguistic origins, historical context, and any relevant dates.
        </p>
      </div>

      <div>
        <label htmlFor="sources" className="mb-1 block text-sm font-medium text-foreground">
          Sources (optional)
        </label>
        <textarea
          id="sources"
          value={sources}
          onChange={(e) => setSources(e.target.value)}
          rows={2}
          className={fieldClass}
          placeholder="List any books, websites, or archives that support your etymology..."
        />
      </div>

      {!user && (
        <div>
          <label htmlFor="email" className="mb-1 block text-sm font-medium text-foreground">
            Your email *
          </label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className={fieldClass}
            placeholder="your@email.com"
            required
          />
          <p className="mt-1 text-xs text-muted-foreground">We will notify you when your contribution is reviewed.</p>
        </div>
      )}

      <div className="flex items-start gap-2 rounded-lg border border-border bg-accent/50 p-3 text-sm text-muted-foreground dark:bg-accent/30">
        <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-primary" />
        <p>
          All contributions are reviewed by our moderation team before being published. By submitting, you agree to our{' '}
          <a href="/terms" className="font-medium text-primary underline-offset-2 hover:underline">
            terms of service
          </a>
          .
        </p>
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className="flex w-full items-center justify-center gap-2 rounded-xl bg-primary px-6 py-3 font-medium text-primary-foreground transition-opacity disabled:opacity-50"
      >
        {isSubmitting ? (
          <>
            <Loader2 className="h-5 w-5 animate-spin" />
            <span>Submitting…</span>
          </>
        ) : (
          <>
            <Send className="h-5 w-5" />
            <span>Submit contribution</span>
          </>
        )}
      </button>
    </form>
  );
}
