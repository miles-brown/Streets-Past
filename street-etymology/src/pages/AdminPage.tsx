import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { supabase, Contribution, Street } from '../lib/supabase';
import { usePageMeta } from '../hooks/usePageMeta';
import { Shield, CheckCircle, XCircle, Clock, Loader2, Eye, MapPin } from 'lucide-react';
import toast from 'react-hot-toast';

type ContributionWithStreet = Contribution & { street?: Street };

export function AdminPage() {
  usePageMeta({
    title: 'Admin',
    description: 'Moderation dashboard for pending street etymology contributions.',
    noIndex: true,
  });

  const { isAdmin, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  const [contributions, setContributions] = useState<ContributionWithStreet[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState<'pending' | 'approved' | 'rejected' | 'all'>('pending');
  const [processingId, setProcessingId] = useState<string | null>(null);

  useEffect(() => {
    if (!authLoading && !isAdmin) {
      toast.error('Access denied. Admin privileges required.');
      navigate('/');
    }
  }, [isAdmin, authLoading, navigate]);

  useEffect(() => {
    loadContributions();
  }, [filter]);

  async function loadContributions() {
    setIsLoading(true);
    try {
      let query = supabase.from('contributions').select('*').order('created_at', { ascending: false });

      if (filter !== 'all') {
        query = query.eq('status', filter);
      }

      const { data: contributionsData, error } = await query;

      if (error) throw error;

      if (contributionsData && contributionsData.length > 0) {
        const streetIds = [...new Set(contributionsData.map((c) => c.street_id))];
        const { data: streets } = await supabase
          .from('streets')
          .select('id, name, city, county')
          .in('id', streetIds);

        const contributionsWithStreets = contributionsData.map((c) => ({
          ...c,
          street: streets?.find((s) => s.id === c.street_id),
        }));

        setContributions(contributionsWithStreets);
      } else {
        setContributions([]);
      }
    } catch (error) {
      console.error('Error loading contributions:', error);
      toast.error('Failed to load contributions');
    } finally {
      setIsLoading(false);
    }
  }

  async function handleApprove(contribution: ContributionWithStreet) {
    setProcessingId(contribution.id);
    try {
      const { error: updateError } = await supabase
        .from('contributions')
        .update({
          status: 'approved',
          reviewed_at: new Date().toISOString(),
        })
        .eq('id', contribution.id);

      if (updateError) throw updateError;

      if (contribution.street_id) {
        await supabase
          .from('streets')
          .update({
            etymology_suggestion: contribution.etymology_suggestion,
            updated_at: new Date().toISOString(),
          })
          .eq('id', contribution.street_id);
      }

      toast.success('Contribution approved');
      loadContributions();
    } catch (error) {
      console.error('Error approving contribution:', error);
      toast.error('Failed to approve contribution');
    } finally {
      setProcessingId(null);
    }
  }

  async function handleReject(contribution: ContributionWithStreet) {
    setProcessingId(contribution.id);
    try {
      const { error } = await supabase
        .from('contributions')
        .update({
          status: 'rejected',
          reviewed_at: new Date().toISOString(),
        })
        .eq('id', contribution.id);

      if (error) throw error;

      toast.success('Contribution rejected');
      loadContributions();
    } catch (error) {
      console.error('Error rejecting contribution:', error);
      toast.error('Failed to reject contribution');
    } finally {
      setProcessingId(null);
    }
  }

  const statusCounts = {
    pending: contributions.filter((c) => c.status === 'pending').length,
    approved: contributions.filter((c) => c.status === 'approved').length,
    rejected: contributions.filter((c) => c.status === 'rejected').length,
  };

  if (authLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <Loader2 className="h-10 w-10 animate-spin text-primary" />
      </div>
    );
  }

  if (!isAdmin) {
    return null;
  }

  return (
    <div className="min-h-screen bg-background py-8">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <div className="mb-2 flex items-center gap-3">
            <Shield className="h-8 w-8 text-primary" />
            <h1 className="font-display text-3xl font-bold text-foreground">Admin dashboard</h1>
          </div>
          <p className="text-muted-foreground">Review and moderate community contributions.</p>
        </div>

        <div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div className="surface-glass rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Pending (this view)</p>
                <p className="font-mono text-3xl font-bold text-primary">{statusCounts.pending}</p>
              </div>
              <Clock className="h-10 w-10 text-primary/30" />
            </div>
          </div>
          <div className="surface-glass rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Approved (this view)</p>
                <p className="font-mono text-3xl font-bold text-emerald-600 dark:text-emerald-400">
                  {statusCounts.approved}
                </p>
              </div>
              <CheckCircle className="h-10 w-10 text-emerald-500/30" />
            </div>
          </div>
          <div className="surface-glass rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Rejected (this view)</p>
                <p className="font-mono text-3xl font-bold text-red-600 dark:text-red-400">{statusCounts.rejected}</p>
              </div>
              <XCircle className="h-10 w-10 text-red-500/30" />
            </div>
          </div>
        </div>

        <div className="surface-glass mb-6 rounded-xl p-4">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-sm font-medium text-foreground">Filter:</span>
            <div className="flex flex-wrap gap-2">
              {(['pending', 'approved', 'rejected', 'all'] as const).map((status) => (
                <button
                  key={status}
                  type="button"
                  onClick={() => setFilter(status)}
                  className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
                    filter === status
                      ? 'bg-accent text-accent-foreground'
                      : 'text-muted-foreground hover:bg-muted'
                  }`}
                >
                  {status.charAt(0).toUpperCase() + status.slice(1)}
                </button>
              ))}
            </div>
          </div>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        ) : contributions.length === 0 ? (
          <div className="surface-glass rounded-xl py-20 text-center">
            <CheckCircle className="mx-auto mb-4 h-16 w-16 text-muted-foreground/40" />
            <h3 className="mb-2 text-lg font-semibold text-foreground">All caught up</h3>
            <p className="text-muted-foreground">No contributions in this filter.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {contributions.map((contribution) => (
              <div key={contribution.id} className="surface-glass rounded-xl p-6">
                <div className="mb-4 flex items-start justify-between gap-4">
                  <div>
                    <div className="mb-1 flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
                      <MapPin className="h-4 w-4 shrink-0 text-primary" />
                      <span>{contribution.street?.name || 'Unknown street'}</span>
                      {contribution.street?.city && (
                        <>
                          <span className="text-border">|</span>
                          <span>{contribution.street.city}</span>
                        </>
                      )}
                    </div>
                    <p className="text-xs text-muted-foreground/80">
                      Submitted by {contribution.user_email} on{' '}
                      {new Date(contribution.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <span
                    className={`shrink-0 rounded-full px-3 py-1 text-xs font-medium ${
                      contribution.status === 'pending'
                        ? 'bg-accent text-accent-foreground'
                        : contribution.status === 'approved'
                          ? 'bg-emerald-500/15 text-emerald-800 dark:text-emerald-300'
                          : 'bg-red-500/15 text-red-800 dark:text-red-300'
                    }`}
                  >
                    {contribution.status}
                  </span>
                </div>

                <div className="mb-4 rounded-lg border border-border bg-muted/50 p-4">
                  <h4 className="mb-2 text-sm font-medium text-foreground">Etymology suggestion</h4>
                  <p className="whitespace-pre-line text-muted-foreground">{contribution.etymology_suggestion}</p>
                  {contribution.sources && (
                    <div className="mt-3 border-t border-border pt-3">
                      <h4 className="mb-1 text-sm font-medium text-foreground">Sources</h4>
                      <p className="text-sm text-muted-foreground">{contribution.sources}</p>
                    </div>
                  )}
                </div>

                {contribution.status === 'pending' && (
                  <div className="flex flex-wrap items-center justify-end gap-3">
                    <button
                      type="button"
                      onClick={() => navigate(`/street/${contribution.street_id}`)}
                      className="flex items-center gap-1 rounded-lg px-4 py-2 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
                    >
                      <Eye className="h-4 w-4" />
                      <span>View street</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => handleReject(contribution)}
                      disabled={processingId === contribution.id}
                      className="flex items-center gap-1 rounded-lg px-4 py-2 text-red-600 transition-colors hover:bg-red-500/10 disabled:opacity-50 dark:text-red-400"
                    >
                      {processingId === contribution.id ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <XCircle className="h-4 w-4" />
                      )}
                      <span>Reject</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => handleApprove(contribution)}
                      disabled={processingId === contribution.id}
                      className="flex items-center gap-1 rounded-lg bg-emerald-600 px-4 py-2 font-medium text-white transition-opacity hover:opacity-90 disabled:opacity-50 dark:bg-emerald-700"
                    >
                      {processingId === contribution.id ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <CheckCircle className="h-4 w-4" />
                      )}
                      <span>Approve</span>
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
