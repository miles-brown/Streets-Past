import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { supabase, Contribution, Street } from '../lib/supabase';
import {
  User,
  Mail,
  Calendar,
  Edit2,
  Loader2,
  CheckCircle,
  Clock,
  XCircle,
  MapPin
} from 'lucide-react';
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

        // Fetch street names
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
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'rejected':
        return <XCircle className="w-5 h-5 text-red-600" />;
      default:
        return <Clock className="w-5 h-5 text-amber-600" />;
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'approved':
        return 'Approved';
      case 'rejected':
        return 'Rejected';
      default:
        return 'Pending Review';
    }
  };

  if (authLoading) {
    return (
      <div className="min-h-screen bg-stone-50 flex items-center justify-center">
        <Loader2 className="w-10 h-10 text-amber-600 animate-spin" />
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-stone-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Profile Card */}
        <div className="bg-white rounded-2xl shadow-sm border border-stone-200 p-6 md:p-8 mb-8">
          <div className="flex items-start justify-between mb-6">
            <h1 className="text-2xl font-serif font-bold text-stone-800">My Profile</h1>
            {!isEditing && (
              <button
                onClick={() => setIsEditing(true)}
                className="flex items-center space-x-1 px-3 py-2 text-stone-600 hover:bg-stone-100 rounded-lg transition-colors text-sm"
              >
                <Edit2 className="w-4 h-4" />
                <span>Edit</span>
              </button>
            )}
          </div>

          <div className="space-y-4">
            <div className="flex items-center space-x-4">
              <div className="w-16 h-16 bg-gradient-to-br from-amber-600 to-amber-800 rounded-full flex items-center justify-center">
                <User className="w-8 h-8 text-white" />
              </div>
              <div>
                {isEditing ? (
                  <input
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="Your name"
                    className="text-xl font-semibold text-stone-800 px-3 py-1 border border-stone-200 rounded-lg focus:ring-2 focus:ring-amber-500"
                  />
                ) : (
                  <h2 className="text-xl font-semibold text-stone-800">
                    {profile?.full_name || 'Anonymous User'}
                  </h2>
                )}
                <div className="flex items-center space-x-1 text-stone-500 mt-1">
                  <Mail className="w-4 h-4" />
                  <span className="text-sm">{user.email}</span>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-6 pt-4 border-t border-stone-200">
              <div className="flex items-center space-x-2 text-sm text-stone-600">
                <Calendar className="w-4 h-4" />
                <span>
                  Joined {new Date(user.created_at).toLocaleDateString('en-GB', {
                    month: 'long',
                    year: 'numeric'
                  })}
                </span>
              </div>
              <div className="text-sm text-stone-600">
                <span className="font-semibold text-amber-700">{contributions.length}</span> contributions
              </div>
            </div>

            {isEditing && (
              <div className="flex items-center justify-end space-x-3 pt-4 border-t border-stone-200">
                <button
                  onClick={() => {
                    setIsEditing(false);
                    setFullName(profile?.full_name || '');
                  }}
                  className="px-4 py-2 text-stone-600 hover:bg-stone-100 rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSaveProfile}
                  disabled={isSaving}
                  className="flex items-center space-x-2 px-4 py-2 bg-amber-700 hover:bg-amber-800 disabled:bg-amber-400 text-white rounded-lg transition-colors"
                >
                  {isSaving ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <span>Save Changes</span>
                  )}
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Contributions */}
        <div className="bg-white rounded-2xl shadow-sm border border-stone-200 p-6 md:p-8">
          <h2 className="text-xl font-serif font-bold text-stone-800 mb-6">
            My Contributions
          </h2>

          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 text-amber-600 animate-spin" />
            </div>
          ) : contributions.length === 0 ? (
            <div className="text-center py-12">
              <MapPin className="w-16 h-16 text-stone-300 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-stone-800 mb-2">
                No contributions yet
              </h3>
              <p className="text-stone-600 mb-4">
                Start contributing by researching street etymologies
              </p>
              <button
                onClick={() => navigate('/search')}
                className="px-4 py-2 bg-amber-700 hover:bg-amber-800 text-white rounded-lg transition-colors"
              >
                Explore Streets
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {contributions.map((contribution) => (
                <div
                  key={contribution.id}
                  className="bg-stone-50 rounded-xl p-4 hover:bg-stone-100 transition-colors cursor-pointer"
                  onClick={() => navigate(`/street/${contribution.street_id}`)}
                >
                  <div className="flex items-start justify-between mb-2">
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
                        Submitted {new Date(contribution.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(contribution.status)}
                      <span className={`text-sm font-medium ${
                        contribution.status === 'approved' ? 'text-green-600' :
                        contribution.status === 'rejected' ? 'text-red-600' :
                        'text-amber-600'
                      }`}>
                        {getStatusLabel(contribution.status)}
                      </span>
                    </div>
                  </div>

                  <p className="text-stone-700 text-sm line-clamp-2">
                    {contribution.etymology_suggestion}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
