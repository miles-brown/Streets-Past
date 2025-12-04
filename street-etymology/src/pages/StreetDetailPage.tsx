import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { supabase, Street, Contribution } from '../lib/supabase';
import { MapView } from '../components/MapView';
import { ContributionForm } from '../components/ContributionForm';
import { useAuth } from '../contexts/AuthContext';
import { 
  MapPin, 
  Clock, 
  BookOpen, 
  ChevronRight,
  Share2,
  Loader2,
  CheckCircle,
  XCircle,
  AlertCircle,
  Sparkles,
  Download
} from 'lucide-react';
import toast from 'react-hot-toast';

export function StreetDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const [street, setStreet] = useState<Street | null>(null);
  const [contributions, setContributions] = useState<Contribution[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isGeneratingAI, setIsGeneratingAI] = useState(false);
  const [aiSuggestion, setAiSuggestion] = useState<string | null>(null);

  useEffect(() => {
    async function loadStreet() {
      if (!id) return;

      setIsLoading(true);
      try {
        const { data: streetData, error: streetError } = await supabase
          .from('streets')
          .select('*')
          .eq('id', id)
          .maybeSingle();

        if (streetError) throw streetError;
        setStreet(streetData);

        // Load approved contributions
        const { data: contributionsData } = await supabase
          .from('contributions')
          .select('*')
          .eq('street_id', id)
          .eq('status', 'approved')
          .order('created_at', { ascending: false });

        setContributions(contributionsData || []);
      } catch (error) {
        console.error('Error loading street:', error);
        toast.error('Failed to load street details');
      } finally {
        setIsLoading(false);
      }
    }

    loadStreet();
  }, [id]);

  const generateAISuggestion = async () => {
    if (!street) return;

    setIsGeneratingAI(true);
    try {
      const { data, error } = await supabase.functions.invoke('suggest-etymology', {
        body: { streetName: street.street_name }
      });

      if (error) throw error;

      if (data?.data?.etymology) {
        setAiSuggestion(data.data.etymology);
        toast.success('AI suggestion generated');
      }
    } catch (error) {
      console.error('AI suggestion error:', error);
      toast.error('Failed to generate AI suggestion');
    } finally {
      setIsGeneratingAI(false);
    }
  };

  const shareStreet = async () => {
    const url = window.location.href;
    const text = `Discover the etymology of ${street?.street_name} in the UK`;

    if (navigator.share) {
      try {
        await navigator.share({ title: street?.name, text, url });
      } catch (error) {
        // User cancelled or error
      }
    } else {
      await navigator.clipboard.writeText(url);
      toast.success('Link copied to clipboard');
    }
  };

  const exportData = () => {
    if (!street) return;

    const data = {
      name: street.street_name,
      location: {
        city: street.post_town,
        county: street.county,
        postcode: street.postcode,
        coordinates: {
          latitude: street.latitude,
          longitude: street.longitude,
        },
      },
      street_type: street.street_type,
      local_authority_area: street.local_authority_area,
      verified: street.verified_status === 'Verified',
      first_recorded: street.year_first_recorded,
      description: street.brief_description,
      exported_at: new Date().toISOString(),
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${street.street_name.replace(/\s+/g, '_')}_etymology.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-stone-50 flex items-center justify-center">
        <Loader2 className="w-10 h-10 text-amber-600 animate-spin" />
      </div>
    );
  }

  if (!street) {
    return (
      <div className="min-h-screen bg-stone-50 flex items-center justify-center">
        <div className="text-center">
          <XCircle className="w-16 h-16 text-stone-300 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-stone-800 mb-2">Street Not Found</h2>
          <p className="text-stone-600 mb-4">The requested street could not be found.</p>
          <Link
            to="/search"
            className="inline-flex items-center space-x-2 px-4 py-2 bg-amber-700 text-white rounded-lg"
          >
            <span>Back to Search</span>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-stone-50">
      {/* Breadcrumb */}
      <div className="bg-white border-b border-stone-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
          <nav className="flex items-center space-x-2 text-sm">
            <Link to="/" className="text-stone-500 hover:text-stone-700">Home</Link>
            <ChevronRight className="w-4 h-4 text-stone-400" />
            <Link to="/search" className="text-stone-500 hover:text-stone-700">Search</Link>
            <ChevronRight className="w-4 h-4 text-stone-400" />
            <span className="text-stone-800 font-medium">{street.street_name}</span>
          </nav>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Header */}
            <div className="bg-white rounded-xl shadow-sm border border-stone-200 p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <div className="flex items-center space-x-2 text-sm text-stone-500 mb-2">
                    <MapPin className="w-4 h-4 text-amber-600" />
                    <span>{[street.post_town, street.county].filter(Boolean).join(', ')}</span>
                    {street.postcode && (
                      <span className="px-2 py-0.5 bg-stone-100 rounded text-xs">
                        {street.postcode}
                      </span>
                    )}
                  </div>
                  <h1 className="text-3xl font-serif font-bold text-stone-800">
                    {street.street_name}
                  </h1>
                </div>
                
                <div className="flex items-center space-x-2">
                  {street.verified_status === 'Verified' ? (
                    <span className="flex items-center space-x-1 px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
                      <CheckCircle className="w-4 h-4" />
                      <span>Verified</span>
                    </span>
                  ) : (
                    <span className="flex items-center space-x-1 px-3 py-1 bg-amber-100 text-amber-700 rounded-full text-sm font-medium">
                      <AlertCircle className="w-4 h-4" />
                      <span>{street.verified_status || 'Unverified'}</span>
                    </span>
                  )}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={shareStreet}
                  className="flex items-center space-x-1 px-3 py-2 text-sm text-stone-600 hover:bg-stone-100 rounded-lg transition-colors"
                >
                  <Share2 className="w-4 h-4" />
                  <span>Share</span>
                </button>
                <button
                  onClick={exportData}
                  className="flex items-center space-x-1 px-3 py-2 text-sm text-stone-600 hover:bg-stone-100 rounded-lg transition-colors"
                >
                  <Download className="w-4 h-4" />
                  <span>Export</span>
                </button>
              </div>
            </div>

            {/* Etymology */}
            <div className="bg-white rounded-xl shadow-sm border border-stone-200 p-6">
              <div className="flex items-center space-x-2 mb-4">
                <BookOpen className="w-5 h-5 text-amber-600" />
                <h2 className="text-xl font-semibold text-stone-800">Etymology</h2>
              </div>

              {street.brief_description ? (
                <div className="prose prose-stone max-w-none">
                  <p className="text-stone-700 leading-relaxed whitespace-pre-line">
                    {street.brief_description}
                  </p>
                </div>
              ) : (
                <div className="bg-stone-50 rounded-lg p-4 text-center">
                  <p className="text-stone-600 mb-4">
                    The etymology of this street has not yet been researched.
                  </p>
                  <button
                    onClick={generateAISuggestion}
                    disabled={isGeneratingAI}
                    className="inline-flex items-center space-x-2 px-4 py-2 bg-amber-700 hover:bg-amber-800 disabled:bg-amber-400 text-white rounded-lg transition-colors"
                  >
                    {isGeneratingAI ? (
                      <Loader2 className="w-5 h-5 animate-spin" />
                    ) : (
                      <Sparkles className="w-5 h-5" />
                    )}
                    <span>Generate AI Suggestion</span>
                  </button>
                </div>
              )}

              {street.charles_booth_reference && (
                <div className="mt-4 pt-4 border-t border-stone-200">
                  <p className="text-sm text-stone-500">
                    <span className="font-medium">Historical Reference:</span> {street.charles_booth_reference}
                  </p>
                </div>
              )}
            </div>

            {/* AI Suggestion */}
            {aiSuggestion && (
              <div className="bg-gradient-to-br from-amber-50 to-orange-50 rounded-xl border border-amber-200 p-6">
                <div className="flex items-center space-x-2 mb-4">
                  <Sparkles className="w-5 h-5 text-amber-600" />
                  <h3 className="text-lg font-semibold text-stone-800">AI-Generated Etymology</h3>
                </div>
                <p className="text-stone-700 leading-relaxed whitespace-pre-line">
                  {aiSuggestion}
                </p>
                <p className="mt-4 text-xs text-stone-500">
                  This suggestion was generated by AI and may require verification.
                </p>
              </div>
            )}

            {/* Historical Notes */}
            {street.building_description && (
              <div className="bg-white rounded-xl shadow-sm border border-stone-200 p-6">
                <h2 className="text-xl font-semibold text-stone-800 mb-4">Building Description</h2>
                <p className="text-stone-700 leading-relaxed">
                  {street.building_description}
                </p>
              </div>
            )}

            {/* Date Information */}
            {street.year_first_recorded && (
              <div className="bg-white rounded-xl shadow-sm border border-stone-200 p-6">
                <div className="flex items-center space-x-2">
                  <Clock className="w-5 h-5 text-amber-600" />
                  <span className="text-stone-700">
                    <span className="font-medium">First Recorded:</span> {street.year_first_recorded}
                  </span>
                </div>
              </div>
            )}

            {/* Community Contributions */}
            {contributions.length > 0 && (
              <div className="bg-white rounded-xl shadow-sm border border-stone-200 p-6">
                <h2 className="text-xl font-semibold text-stone-800 mb-4">
                  Community Contributions
                </h2>
                <div className="space-y-4">
                  {contributions.map((contribution) => (
                    <div
                      key={contribution.id}
                      className="bg-stone-50 rounded-lg p-4"
                    >
                      <p className="text-stone-700 mb-2">
                        {contribution.etymology_suggestion}
                      </p>
                      {contribution.sources && (
                        <p className="text-sm text-stone-500">
                          <span className="font-medium">Sources:</span> {contribution.sources}
                        </p>
                      )}
                      <p className="text-xs text-stone-400 mt-2">
                        Contributed on {new Date(contribution.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Map */}
            {street.latitude && street.longitude && (
              <div className="bg-white rounded-xl shadow-sm border border-stone-200 overflow-hidden">
                <MapView selectedStreet={street} height="300px" />
                <div className="p-4 border-t border-stone-200">
                  <p className="text-sm text-stone-600">
                    <span className="font-medium">Coordinates:</span>{' '}
                    {street.latitude.toFixed(4)}, {street.longitude.toFixed(4)}
                  </p>
                </div>
              </div>
            )}

            {/* Contribute */}
            <div className="bg-white rounded-xl shadow-sm border border-stone-200 p-6">
              <h3 className="text-lg font-semibold text-stone-800 mb-4">
                Contribute Etymology
              </h3>
              <p className="text-sm text-stone-600 mb-4">
                Share your knowledge about the origin of this street name.
                {!user && ' Sign in for faster submissions.'}
              </p>
              <ContributionForm
                streetId={street.id}
                streetName={street.street_name}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
