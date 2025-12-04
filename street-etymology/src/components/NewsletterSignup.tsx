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
      <div className="bg-green-50 rounded-xl p-6 text-center">
        <CheckCircle className="w-10 h-10 text-green-600 mx-auto mb-3" />
        <h3 className="text-lg font-semibold text-green-800 mb-1">
          Successfully Subscribed
        </h3>
        <p className="text-green-700 text-sm">
          You will receive updates about new etymological discoveries and features.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-br from-amber-50 to-orange-50 rounded-xl p-6 border border-amber-200">
      <div className="flex items-center space-x-3 mb-4">
        <div className="w-10 h-10 bg-amber-100 rounded-lg flex items-center justify-center">
          <Mail className="w-5 h-5 text-amber-700" />
        </div>
        <div>
          <h3 className="font-semibold text-stone-800">Etymology Newsletter</h3>
          <p className="text-sm text-stone-600">Stay updated on street name discoveries</p>
        </div>
      </div>
      
      <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3">
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Enter your email"
          className="flex-1 px-4 py-2 border border-amber-200 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent transition-all bg-white"
          required
        />
        <button
          type="submit"
          disabled={isSubmitting}
          className="px-6 py-2 bg-amber-700 hover:bg-amber-800 disabled:bg-amber-400 text-white font-medium rounded-lg transition-colors flex items-center justify-center space-x-2"
        >
          {isSubmitting ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <span>Subscribe</span>
          )}
        </button>
      </form>
      
      <p className="mt-3 text-xs text-stone-500">
        We respect your privacy. Unsubscribe at any time.
      </p>
    </div>
  );
}
