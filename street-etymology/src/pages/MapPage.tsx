import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { MapView } from '../components/MapView';
import { SearchBar } from '../components/SearchBar';
import { Street } from '../lib/supabase';
import { 
  MapPin, 
  List, 
  Grid,
  X,
  Clock,
  ChevronRight,
  CheckCircle
} from 'lucide-react';

export function MapPage() {
  const navigate = useNavigate();
  const [selectedStreet, setSelectedStreet] = useState<Street | null>(null);
  const [showSidebar, setShowSidebar] = useState(true);

  const handleStreetSelect = (street: Street) => {
    setSelectedStreet(street);
    setShowSidebar(true);
  };

  return (
    <div className="h-screen flex flex-col">
      {/* Top Bar */}
      <div className="bg-white border-b border-stone-200 p-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
          <div className="flex items-center space-x-2">
            <MapPin className="w-6 h-6 text-amber-600" />
            <h1 className="text-xl font-serif font-bold text-stone-800">
              UK Street Map
            </h1>
          </div>
          
          <div className="flex-1 max-w-xl">
            <SearchBar 
              onSelect={handleStreetSelect} 
              placeholder="Search for a street..."
            />
          </div>

          <div className="hidden md:flex items-center space-x-2">
            <button
              onClick={() => setShowSidebar(!showSidebar)}
              className={`p-2 rounded-lg transition-colors ${
                showSidebar 
                  ? 'bg-amber-100 text-amber-700' 
                  : 'text-stone-600 hover:bg-stone-100'
              }`}
              title={showSidebar ? 'Hide sidebar' : 'Show sidebar'}
            >
              <List className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Map and Sidebar */}
      <div className="flex-1 flex overflow-hidden">
        {/* Map */}
        <div className="flex-1 relative">
          <MapView 
            selectedStreet={selectedStreet}
            onStreetSelect={handleStreetSelect}
            height="100%"
          />

          {/* Mobile Selected Street Card */}
          {selectedStreet && (
            <div className="absolute bottom-4 left-4 right-4 md:hidden bg-white rounded-xl shadow-xl border border-stone-200 p-4">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 text-sm text-stone-500 mb-1">
                    <MapPin className="w-4 h-4 text-amber-600" />
                    <span>{selectedStreet.city}, {selectedStreet.county}</span>
                  </div>
                  <h3 className="text-lg font-semibold text-stone-800">
                    {selectedStreet.name}
                  </h3>
                  {selectedStreet.etymology_suggestion && (
                    <p className="text-sm text-stone-600 mt-1 line-clamp-2">
                      {selectedStreet.etymology_suggestion}
                    </p>
                  )}
                  <button
                    onClick={() => navigate(`/street/${selectedStreet.id}`)}
                    className="mt-3 flex items-center space-x-1 text-amber-700 font-medium text-sm"
                  >
                    <span>View Details</span>
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
                <button
                  onClick={() => setSelectedStreet(null)}
                  className="p-1 text-stone-400 hover:text-stone-600"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Sidebar */}
        {showSidebar && (
          <div className="hidden md:block w-96 bg-white border-l border-stone-200 overflow-y-auto">
            {selectedStreet ? (
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-2">
                    {selectedStreet.etymology_verified ? (
                      <span className="flex items-center space-x-1 px-2 py-0.5 bg-green-100 text-green-700 rounded-full text-xs font-medium">
                        <CheckCircle className="w-3 h-3" />
                        <span>Verified</span>
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 bg-amber-100 text-amber-700 rounded-full text-xs font-medium">
                        Unverified
                      </span>
                    )}
                  </div>
                  <button
                    onClick={() => setSelectedStreet(null)}
                    className="p-1 text-stone-400 hover:text-stone-600"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>

                <div className="flex items-center space-x-2 text-sm text-stone-500 mb-2">
                  <MapPin className="w-4 h-4 text-amber-600" />
                  <span>{[selectedStreet.city, selectedStreet.county].filter(Boolean).join(', ')}</span>
                </div>

                <h2 className="text-2xl font-serif font-bold text-stone-800 mb-4">
                  {selectedStreet.name}
                </h2>

                {selectedStreet.etymology_suggestion ? (
                  <div className="prose prose-stone prose-sm max-w-none mb-4">
                    <p className="text-stone-700 leading-relaxed">
                      {selectedStreet.etymology_suggestion}
                    </p>
                  </div>
                ) : (
                  <p className="text-stone-500 italic mb-4">
                    Etymology not yet researched
                  </p>
                )}

                {selectedStreet.first_recorded_date && (
                  <div className="flex items-center space-x-2 text-sm text-stone-600 mb-4 pb-4 border-b border-stone-200">
                    <Clock className="w-4 h-4" />
                    <span>First recorded: {selectedStreet.first_recorded_date}</span>
                  </div>
                )}

                {selectedStreet.latitude && selectedStreet.longitude && (
                  <div className="text-sm text-stone-500 mb-6">
                    <span className="font-medium">Coordinates:</span>{' '}
                    {selectedStreet.latitude.toFixed(5)}, {selectedStreet.longitude.toFixed(5)}
                  </div>
                )}

                <button
                  onClick={() => navigate(`/street/${selectedStreet.id}`)}
                  className="w-full flex items-center justify-center space-x-2 px-4 py-3 bg-amber-700 hover:bg-amber-800 text-white rounded-lg transition-colors font-medium"
                >
                  <span>View Full Details</span>
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div className="p-6">
                <div className="text-center py-12">
                  <div className="w-16 h-16 bg-stone-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <Grid className="w-8 h-8 text-stone-400" />
                  </div>
                  <h3 className="text-lg font-semibold text-stone-800 mb-2">
                    Select a Street
                  </h3>
                  <p className="text-stone-600 text-sm">
                    Click on any marker on the map or use the search bar to select a street 
                    and view its etymology.
                  </p>
                </div>

                <div className="mt-8">
                  <h4 className="text-sm font-semibold text-stone-800 uppercase tracking-wider mb-3">
                    Quick Tips
                  </h4>
                  <ul className="space-y-3 text-sm text-stone-600">
                    <li className="flex items-start space-x-2">
                      <MapPin className="w-4 h-4 text-amber-600 mt-0.5 flex-shrink-0" />
                      <span>Click on any marker to see street details</span>
                    </li>
                    <li className="flex items-start space-x-2">
                      <MapPin className="w-4 h-4 text-amber-600 mt-0.5 flex-shrink-0" />
                      <span>Use scroll wheel to zoom in and out</span>
                    </li>
                    <li className="flex items-start space-x-2">
                      <MapPin className="w-4 h-4 text-amber-600 mt-0.5 flex-shrink-0" />
                      <span>Drag the map to explore different areas</span>
                    </li>
                  </ul>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
