import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { supabase, Contribution, Street } from '../lib/supabase';
import {
  Shield,
  CheckCircle,
  XCircle,
  Clock,
  Loader2,
  ChevronDown,
  Eye,
  MapPin,
  AlertTriangle
} from 'lucide-react';
import toast from 'react-hot-toast';

type ContributionWithStreet = Contribution & { street?: Street };

export function AdminPage() {
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
      let query = supabase
        .from('contributions')
        .select('*')
        .order('created_at', { ascending: false });

      if (filter !== 'all') {
        query = query.eq('status', filter);
      }

      const { data: contributionsData, error } = await query;

      if (error) throw error;

      // Fetch street names for each contribution
      if (contributionsData && contributionsData.length > 0) {
        const streetIds = [...new Set(contributionsData.map(c => c.street_id))];
        const { data: streets } = await supabase
          .from('streets')
          .select('id, name, city, county')
          .in('id', streetIds);

        const contributionsWithStreets = contributionsData.map(c => ({
          ...c,
          street: streets?.find(s => s.id === c.street_id)
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
      // Update contribution status
      const { error: updateError } = await supabase
        .from('contributions')
        .update({
          status: 'approved',
          reviewed_at: new Date().toISOString()
        })
        .eq('id', contribution.id);

      if (updateError) throw updateError;

      // Optionally update the street's etymology
      if (contribution.street_id) {
        await supabase
          .from('streets')
          .update({
            etymology_suggestion: contribution.etymology_suggestion,
            updated_at: new Date().toISOString()
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
          reviewed_at: new Date().toISOString()
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
    pending: contributions.filter(c => c.status === 'pending').length,
    approved: contributions.filter(c => c.status === 'approved').length,
    rejected: contributions.filter(c => c.status === 'rejected').length,
  };

  if (authLoading) {
    return (
      <div className="min-h-screen bg-stone-50 flex items-center justify-center">
        <Loader2 className="w-10 h-10 text-amber-600 animate-spin" />
      </div>
    );
  }

  if (!isAdmin) {
    return null;
  }

  return (
    <div className="min-h-screen bg-stone-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center space-x-3 mb-2">
            <Shield className="w-8 h-8 text-amber-600" />
            <h1 className="text-3xl font-serif font-bold text-stone-800">
              Admin Dashboard
            </h1>
          </div>
          <p className="text-stone-600">
            Review and moderate community contributions
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
          <div className="bg-white rounded-xl shadow-sm border border-stone-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-stone-600">Pending Review</p>
                <p className="text-3xl font-bold text-amber-600">{statusCounts.pending}</p>
              </div>
              <Clock className="w-10 h-10 text-amber-200" />
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-stone-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-stone-600">Approved</p>
                <p className="text-3xl font-bold text-green-600">{statusCounts.approved}</p>
              </div>
              <CheckCircle className="w-10 h-10 text-green-200" />
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-stone-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-stone-600">Rejected</p>
                <p className="text-3xl font-bold text-red-600">{statusCounts.rejected}</p>
              </div>
              <XCircle className="w-10 h-10 text-red-200" />
            </div>
          </div>
        </div>

        {/* Filter */}
        <div className="bg-white rounded-xl shadow-sm border border-stone-200 p-4 mb-6">
          <div className="flex items-center space-x-2">
            <span className="text-sm font-medium text-stone-700">Filter:</span>
            <div className="flex space-x-2">
              {(['pending', 'approved', 'rejected', 'all'] as const).map((status) => (
                <button
                  key={status}
                  onClick={() => setFilter(status)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    filter === status
                      ? 'bg-amber-100 text-amber-800'
                      : 'text-stone-600 hover:bg-stone-100'
                  }`}
                >
                  {status.charAt(0).toUpperCase() + status.slice(1)}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Contributions List */}
        {isLoading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-8 h-8 text-amber-600 animate-spin" />
          </div>
        ) : contributions.length === 0 ? (
          <div className="text-center py-20 bg-white rounded-xl border border-stone-200">
            <CheckCircle className="w-16 h-16 text-green-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-stone-800 mb-2">All caught up!</h3>
            <p className="text-stone-600">No contributions to review at the moment.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {contributions.map((contribution) => (
              <div
                key={contribution.id}
                className="bg-white rounded-xl shadow-sm border border-stone-200 p-6"
              >
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <div className="flex items-center space-x-2 text-sm text-stone-500 mb-1">
                      <MapPin className="w-4 h-4 text-amber-600" />
                      <span>{contribution.street?.name || 'Unknown Street'}</span>
                      {contribution.street?.city && (
                        <>
                          <span className="text-stone-300">|</span>
                          <span>{contribution.street.city}</span>
                        </>
                      )}
                    </div>
                    <p className="text-xs text-stone-400">
                      Submitted by {contribution.user_email} on{' '}
                      {new Date(contribution.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-medium ${
                      contribution.status === 'pending'
                        ? 'bg-amber-100 text-amber-700'
                        : contribution.status === 'approved'
                        ? 'bg-green-100 text-green-700'
                        : 'bg-red-100 text-red-700'
                    }`}
                  >
                    {contribution.status}
                  </span>
                </div>

                <div className="bg-stone-50 rounded-lg p-4 mb-4">
                  <h4 className="text-sm font-medium text-stone-700 mb-2">Etymology Suggestion:</h4>
                  <p className="text-stone-800 whitespace-pre-line">
                    {contribution.etymology_suggestion}
                  </p>
                  {contribution.sources && (
                    <div className="mt-3 pt-3 border-t border-stone-200">
                      <h4 className="text-sm font-medium text-stone-700 mb-1">Sources:</h4>
                      <p className="text-sm text-stone-600">{contribution.sources}</p>
                    </div>
                  )}
                </div>

                {contribution.status === 'pending' && (
                  <div className="flex items-center justify-end space-x-3">
                    <button
                      onClick={() => navigate(`/street/${contribution.street_id}`)}
                      className="flex items-center space-x-1 px-4 py-2 text-stone-600 hover:bg-stone-100 rounded-lg transition-colors"
                    >
                      <Eye className="w-4 h-4" />
                      <span>View Street</span>
                    </button>
                    <button
                      onClick={() => handleReject(contribution)}
                      disabled={processingId === contribution.id}
                      className="flex items-center space-x-1 px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
                    >
                      {processingId === contribution.id ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <XCircle className="w-4 h-4" />
                      )}
                      <span>Reject</span>
                    </button>
                    <button
                      onClick={() => handleApprove(contribution)}
                      disabled={processingId === contribution.id}
                      className="flex items-center space-x-1 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors disabled:opacity-50"
                    >
                      {processingId === contribution.id ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <CheckCircle className="w-4 h-4" />
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
