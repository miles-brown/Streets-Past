import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { supabase, Contribution, Street } from '../lib/supabase';
import { User, Mail, Calendar, Edit2, Loader2, CheckCircle, Clock, XCircle, MapPin } from 'lucide-react';
import toast from 'react-hot-toast';

type ContributionWithStreet = Contribution & { street?: Street };

export function ProfilePage() {
  const { user, profile, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  const [contributions, setContributions] = useState<ContributionWithStreet[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [fullName, setFullName] = useState(profile?.full_name || '');
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (!authLoading && !user) {
      navigate('/login');
    }
  }, [user, authLoading, navigate]);

  useEffect(() => {
    if (profile?.full_name) {
      setFullName(profile.full_name);
    }
  }, [profile]);

  useEffect(() => {
    async function loadContributions() {
      if (!user) return;

      setIsLoading(true);
      try {
        const { data: contributionsData, error } = await supabase
          .from('contributions')
          .select('*')
          .eq('user_email', user.email)
          .order('created_at', { ascending: false });

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
      } finally {
        setIsLoading(false);
      }
    }

    loadContributions();
  }, [user]);

  const handleSaveProfile = async () => {
    if (!user) return;

    setIsSaving(true);
    try {
      const { error } = await supabase
        .from('profiles')
        .update({ full_name: fullName, updated_at: new Date().toISOString() })
        .eq('user_id', user.id);

      if (error) throw error;

      toast.success('Profile updated');
      setIsEditing(false);
    } catch (error) {
      console.error('Error updating profile:', error);
      toast.error('Failed to update profile');
    } finally {
      setIsSaving(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'approved':
        return <CheckCircle className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />;
      case 'rejected':
        return <XCircle className="h-5 w-5 text-red-600 dark:text-red-400" />;
      default:
        return <Clock className="h-5 w-5 text-primary" />;
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'approved':
        return 'Approved';
      case 'rejected':
        return 'Rejected';
      default:
        return 'Pending review';
    }
  };

  if (authLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <Loader2 className="h-10 w-10 animate-spin text-primary" />
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-background py-8">
      <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
        <div className="surface-glass mb-8 rounded-2xl p-6 md:p-8">
          <div className="mb-6 flex items-start justify-between">
            <h1 className="font-display text-2xl font-bold text-foreground">My profile</h1>
            {!isEditing && (
              <button
                type="button"
                onClick={() => setIsEditing(true)}
                className="flex items-center gap-1 rounded-lg px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
              >
                <Edit2 className="h-4 w-4" />
                <span>Edit</span>
              </button>
            )}
          </div>

          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-primary to-primary/85 text-primary-foreground">
                <User className="h-8 w-8" />
              </div>
              <div>
                {isEditing ? (
                  <input
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="Your name"
                    className="rounded-lg border border-border bg-background px-3 py-1 text-xl font-semibold text-foreground focus:border-primary/40 focus:outline-none focus:ring-2 focus:ring-ring/30"
                  />
                ) : (
                  <h2 className="text-xl font-semibold text-foreground">{profile?.full_name || 'Anonymous user'}</h2>
                )}
                <div className="mt-1 flex items-center gap-1 text-muted-foreground">
                  <Mail className="h-4 w-4" />
                  <span className="text-sm">{user.email}</span>
                </div>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-6 border-t border-border pt-4">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Calendar className="h-4 w-4" />
                <span>
                  Joined{' '}
                  {new Date(user.created_at).toLocaleDateString('en-GB', {
                    month: 'long',
                    year: 'numeric',
                  })}
                </span>
              </div>
              <div className="text-sm text-muted-foreground">
                <span className="font-semibold text-primary">{contributions.length}</span> contributions
              </div>
            </div>

            {isEditing && (
              <div className="flex items-center justify-end gap-3 border-t border-border pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setIsEditing(false);
                    setFullName(profile?.full_name || '');
                  }}
                  className="rounded-lg px-4 py-2 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={handleSaveProfile}
                  disabled={isSaving}
                  className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2 font-medium text-primary-foreground transition-opacity disabled:opacity-50"
                >
                  {isSaving ? <Loader2 className="h-4 w-4 animate-spin" /> : <span>Save changes</span>}
                </button>
              </div>
            )}
          </div>
        </div>

        <div className="surface-glass rounded-2xl p-6 md:p-8">
          <h2 className="mb-6 font-display text-xl font-bold text-foreground">My contributions</h2>

          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          ) : contributions.length === 0 ? (
            <div className="py-12 text-center">
              <MapPin className="mx-auto mb-4 h-16 w-16 text-muted-foreground/40" />
              <h3 className="mb-2 text-lg font-semibold text-foreground">No contributions yet</h3>
              <p className="mb-4 text-muted-foreground">Start by researching street etymologies.</p>
              <button
                type="button"
                onClick={() => navigate('/search')}
                className="rounded-lg bg-primary px-4 py-2 font-medium text-primary-foreground transition-opacity hover:opacity-90"
              >
                Explore streets
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {contributions.map((contribution) => (
                <div
                  key={contribution.id}
                  className="cursor-pointer rounded-xl border border-border bg-muted/30 p-4 transition-colors hover:bg-muted/50"
                  onClick={() => navigate(`/street/${contribution.street_id}`)}
                >
                  <div className="mb-2 flex items-start justify-between">
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
                        Submitted {new Date(contribution.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      {getStatusIcon(contribution.status)}
                      <span
                        className={`text-sm font-medium ${
                          contribution.status === 'approved'
                            ? 'text-emerald-600 dark:text-emerald-400'
                            : contribution.status === 'rejected'
                              ? 'text-red-600 dark:text-red-400'
                              : 'text-primary'
                        }`}
                      >
                        {getStatusLabel(contribution.status)}
                      </span>
                    </div>
                  </div>

                  <p className="line-clamp-2 text-sm text-muted-foreground">{contribution.etymology_suggestion}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
