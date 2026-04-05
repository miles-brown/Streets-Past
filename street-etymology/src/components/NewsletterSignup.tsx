import { useState } from 'react';
import { supabase } from '../lib/supabase';
import { Mail, Loader2, CheckCircle } from 'lucide-react';
import toast from 'react-hot-toast';

export function NewsletterSignup() {
  const [email, setEmail] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [subscribed, setSubscribed] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email.trim()) {
      toast.error('Please enter your email address');
      return;
    }

    setIsSubmitting(true);

    try {
      const { error } = await supabase.from('newsletter_subscribers').insert({
        email: email.trim().toLowerCase(),
      });

      if (error) {
        if (error.code === '23505') {
          toast.error('This email is already subscribed');
        } else {
          throw error;
        }
      } else {
        setSubscribed(true);
        toast.success('Thank you for subscribing!');
      }
    } catch (error) {
      console.error('Subscription error:', error);
      toast.error('Failed to subscribe. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (subscribed) {
    return (
      <div className="surface-glass rounded-2xl p-6 text-center">
        <CheckCircle className="mx-auto mb-3 h-10 w-10 text-primary" />
        <h3 className="mb-1 font-display text-lg font-semibold text-foreground">Subscribed</h3>
        <p className="text-sm text-muted-foreground">
          You will receive occasional updates on etymology and new features.
        </p>
      </div>
    );
  }

  return (
    <div className="surface-glass rounded-2xl p-6">
      <div className="mb-4 flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-border bg-accent/80">
          <Mail className="h-5 w-5 text-primary" />
        </div>
        <div>
          <h3 className="font-display font-semibold text-foreground">Newsletter</h3>
          <p className="text-sm text-muted-foreground">Quiet updates — no clutter.</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-3 sm:flex-row">
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Your email"
          className="flex-1 rounded-xl border border-border bg-background px-4 py-2.5 text-foreground placeholder:text-muted-foreground focus:border-primary/40 focus:outline-none focus:ring-2 focus:ring-ring/30"
          required
        />
        <button
          type="submit"
          disabled={isSubmitting}
          className="inline-flex items-center justify-center gap-2 rounded-xl bg-primary px-6 py-2.5 font-medium text-primary-foreground transition-opacity disabled:opacity-50"
        >
          {isSubmitting ? <Loader2 className="h-5 w-5 animate-spin" /> : <span>Subscribe</span>}
        </button>
      </form>

      <p className="mt-3 text-xs text-muted-foreground">Unsubscribe any time. We keep data minimal.</p>
    </div>
  );
}
