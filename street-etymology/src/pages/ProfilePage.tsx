import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { supabase, Contribution, Street } from '../lib/supabase';
import { usePageMeta } from '../hooks/usePageMeta';
import { User, Mail, Calendar, Edit2, Loader2, CheckCircle, Clock, XCircle, MapPin, Bookmark } from 'lucide-react';
import toast from 'react-hot-toast';

type ContributionWithStreet = Contribution & { street?: Street };

type SavedStreetRow = { savedId: string; street: Pick<Street, 'id' | 'name' | 'city' | 'county'> };

export function ProfilePage() {
  usePageMeta({
    title: 'Profile',
    description: 'Your Street Etymology UK profile, saved streets, and contribution status.',
    noIndex: true,
  });

  const { user, profile, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  const [contributions, setContributions] = useState<ContributionWithStreet[]>([]);
  const [savedStreets, setSavedStreets] = useState<SavedStreetRow[]>([]);
  const [savedLoading, setSavedLoading] = useState(true);
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

  useEffect(() => {
    async function loadSaved() {
      if (!user) {
        setSavedStreets([]);
        setSavedLoading(false);
        return;
      }

      setSavedLoading(true);
      try {
        const { data: saves, error } = await supabase
          .from('saved_streets')
          .select('id, street_id, created_at')
          .eq('user_id', user.id)
          .order('created_at', { ascending: false });

        if (error) throw error;
        if (!saves?.length) {
          setSavedStreets([]);
          return;
        }

        const ids = saves.map((s) => s.street_id);
        const { data: streets, error: stErr } = await supabase
          .from('streets')
          .select('id, name, city, county')
          .in('id', ids);

        if (stErr) throw stErr;

        const list: SavedStreetRow[] = saves
          .map((s) => {
            const street = streets?.find((t) => t.id === s.street_id);
            return street ? { savedId: s.id, street } : null;
          })
          .filter((x): x is SavedStreetRow => x !== null);

        setSavedStreets(list);
      } catch (e) {
        console.error('Error loading saved streets:', e);
        setSavedStreets([]);
      } finally {
        setSavedLoading(false);
      }
    }

    loadSaved();
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

        <div className="surface-glass mb-8 rounded-2xl p-6 md:p-8">
          <div className="mb-6 flex items-center gap-2">
            <Bookmark className="h-6 w-6 text-primary" />
            <h2 className="font-display text-xl font-bold text-foreground">My atlas</h2>
          </div>
          <p className="mb-6 text-sm text-muted-foreground">
            Streets you have saved from detail pages appear here for quick return visits.
          </p>

          {savedLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          ) : savedStreets.length === 0 ? (
            <div className="rounded-xl border border-dashed border-border py-10 text-center">
              <p className="mb-4 text-muted-foreground">No saved streets yet.</p>
              <Link
                to="/explore"
                className="font-medium text-primary transition-opacity hover:opacity-90"
              >
                Explore streets
              </Link>
            </div>
          ) : (
            <div className="space-y-3">
              {savedStreets.map(({ savedId, street }) => (
                <Link
                  key={savedId}
                  to={`/street/${street.id}`}
                  className="flex items-center justify-between gap-3 rounded-xl border border-border bg-muted/30 p-4 transition-colors hover:bg-muted/50"
                >
                  <div className="min-w-0">
                    <div className="mb-0.5 flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
                      <MapPin className="h-4 w-4 shrink-0 text-primary" />
                      <span className="truncate">{[street.city, street.county].filter(Boolean).join(', ') || 'UK'}</span>
                    </div>
                    <div className="truncate font-medium text-foreground">{street.name}</div>
                  </div>
                  <span className="shrink-0 text-xs text-muted-foreground">View</span>
                </Link>
              ))}
            </div>
          )}
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
