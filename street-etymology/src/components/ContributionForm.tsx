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
      
      if (onSuccess) {
        onSuccess();
      }
    } catch (error) {
      console.error('Submission error:', error);
      toast.error('Failed to submit contribution. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (submitted) {
    return (
      <div className="bg-green-50 rounded-xl p-6 text-center">
        <CheckCircle className="w-12 h-12 text-green-600 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-green-800 mb-2">
          Contribution Submitted
        </h3>
        <p className="text-green-700">
          Thank you for your contribution to the etymology of {streetName}. 
          Our team will review your submission shortly.
        </p>
        <button
          onClick={() => {
            setSubmitted(false);
            setEtymology('');
            setSources('');
          }}
          className="mt-4 px-4 py-2 text-sm font-medium text-green-700 hover:text-green-800 transition-colors"
        >
          Submit another contribution
        </button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="etymology" className="block text-sm font-medium text-stone-700 mb-1">
          Etymology Suggestion *
        </label>
        <textarea
          id="etymology"
          value={etymology}
          onChange={(e) => setEtymology(e.target.value)}
          rows={4}
          className="w-full px-4 py-3 border border-stone-200 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent transition-all resize-none"
          placeholder="Share your knowledge about the origin and meaning of this street name..."
          required
        />
        <p className="mt-1 text-xs text-stone-500">
          Include linguistic origins, historical context, and any relevant dates.
        </p>
      </div>

      <div>
        <label htmlFor="sources" className="block text-sm font-medium text-stone-700 mb-1">
          Sources (Optional)
        </label>
        <textarea
          id="sources"
          value={sources}
          onChange={(e) => setSources(e.target.value)}
          rows={2}
          className="w-full px-4 py-3 border border-stone-200 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent transition-all resize-none"
          placeholder="List any books, websites, or archives that support your etymology..."
        />
      </div>

      {!user && (
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-stone-700 mb-1">
            Your Email *
          </label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-4 py-3 border border-stone-200 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent transition-all"
            placeholder="your@email.com"
            required
          />
          <p className="mt-1 text-xs text-stone-500">
            We will notify you when your contribution is reviewed.
          </p>
        </div>
      )}

      <div className="flex items-start space-x-2 text-sm text-stone-600 bg-amber-50 p-3 rounded-lg">
        <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
        <p>
          All contributions are reviewed by our moderation team before being published. 
          By submitting, you agree to our{' '}
          <a href="/terms" className="text-amber-700 hover:text-amber-800 underline">
            terms of service
          </a>.
        </p>
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full flex items-center justify-center space-x-2 px-6 py-3 bg-amber-700 hover:bg-amber-800 disabled:bg-amber-400 text-white font-medium rounded-lg transition-colors"
      >
        {isSubmitting ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            <span>Submitting...</span>
          </>
        ) : (
          <>
            <Send className="w-5 h-5" />
            <span>Submit Contribution</span>
          </>
        )}
      </button>
    </form>
  );
}
