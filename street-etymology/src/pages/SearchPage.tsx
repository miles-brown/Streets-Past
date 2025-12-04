import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { supabase, Street } from '../lib/supabase';
import { 
  Search, 
  MapPin, 
  Filter, 
  Clock, 
  ChevronDown,
  Loader2,
  ArrowUpDown,
  CheckCircle
} from 'lucide-react';

export function SearchPage() {
  const [streets, setStreets] = useState<Street[]>([]);
  const [filteredStreets, setFilteredStreets] = useState<Street[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCounty, setSelectedCounty] = useState('');
  const [selectedCity, setSelectedCity] = useState('');
  const [verifiedOnly, setVerifiedOnly] = useState(false);
  const [sortBy, setSortBy] = useState<'name' | 'city' | 'date'>('name');
  const [counties, setCounties] = useState<string[]>([]);
  const [cities, setCities] = useState<string[]>([]);
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    async function loadStreets() {
      setIsLoading(true);
      try {
        const { data, error } = await supabase
          .from('streets')
          .select('*')
          .order('name');

        if (error) throw error;

        setStreets(data || []);
        setFilteredStreets(data || []);

        // Extract unique counties and cities
        const uniqueCounties = [...new Set(data?.map(s => s.county).filter(Boolean))] as string[];
        const uniqueCities = [...new Set(data?.map(s => s.city).filter(Boolean))] as string[];
        
        setCounties(uniqueCounties.sort());
        setCities(uniqueCities.sort());
      } catch (error) {
        console.error('Error loading streets:', error);
      } finally {
        setIsLoading(false);
      }
    }

    loadStreets();
  }, []);

  // Filter and sort streets
  useEffect(() => {
    let result = [...streets];

    // Filter by search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      result = result.filter(s => 
        s.name.toLowerCase().includes(query) ||
        s.etymology_suggestion?.toLowerCase().includes(query)
      );
    }

    // Filter by county
    if (selectedCounty) {
      result = result.filter(s => s.county === selectedCounty);
    }

    // Filter by city
    if (selectedCity) {
      result = result.filter(s => s.city === selectedCity);
    }

    // Filter by verified
    if (verifiedOnly) {
      result = result.filter(s => s.etymology_verified);
    }

    // Sort
    result.sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'city':
          return (a.city || '').localeCompare(b.city || '');
        case 'date':
          return (a.first_recorded_date || '').localeCompare(b.first_recorded_date || '');
        default:
          return 0;
      }
    });

    setFilteredStreets(result);
  }, [streets, searchQuery, selectedCounty, selectedCity, verifiedOnly, sortBy]);

  const clearFilters = () => {
    setSearchQuery('');
    setSelectedCounty('');
    setSelectedCity('');
    setVerifiedOnly(false);
    setSortBy('name');
  };

  const activeFilterCount = [selectedCounty, selectedCity, verifiedOnly].filter(Boolean).length;

  return (
    <div className="min-h-screen bg-stone-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-serif font-bold text-stone-800 mb-2">
            Search UK Streets
          </h1>
          <p className="text-stone-600">
            Browse and filter through our database of UK street names and their etymologies
          </p>
        </div>

        {/* Search and Filters */}
        <div className="bg-white rounded-xl shadow-sm border border-stone-200 p-4 mb-6">
          <div className="flex flex-col lg:flex-row gap-4">
            {/* Search Input */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-stone-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by street name or etymology..."
                className="w-full pl-10 pr-4 py-3 border border-stone-200 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
              />
            </div>

            {/* Filter Toggle */}
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`flex items-center space-x-2 px-4 py-3 rounded-lg border transition-colors ${
                showFilters || activeFilterCount > 0
                  ? 'bg-amber-50 border-amber-200 text-amber-700'
                  : 'border-stone-200 text-stone-600 hover:bg-stone-50'
              }`}
            >
              <Filter className="w-5 h-5" />
              <span>Filters</span>
              {activeFilterCount > 0 && (
                <span className="w-5 h-5 bg-amber-600 text-white text-xs rounded-full flex items-center justify-center">
                  {activeFilterCount}
                </span>
              )}
              <ChevronDown className={`w-4 h-4 transition-transform ${showFilters ? 'rotate-180' : ''}`} />
            </button>

            {/* Sort */}
            <div className="relative">
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
                className="appearance-none w-full lg:w-auto pl-10 pr-10 py-3 border border-stone-200 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent bg-white"
              >
                <option value="name">Sort by Name</option>
                <option value="city">Sort by City</option>
                <option value="date">Sort by Date</option>
              </select>
              <ArrowUpDown className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-stone-400" />
            </div>
          </div>

          {/* Expanded Filters */}
          {showFilters && (
            <div className="mt-4 pt-4 border-t border-stone-200 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-stone-700 mb-1">County</label>
                <select
                  value={selectedCounty}
                  onChange={(e) => setSelectedCounty(e.target.value)}
                  className="w-full px-3 py-2 border border-stone-200 rounded-lg focus:ring-2 focus:ring-amber-500"
                >
                  <option value="">All Counties</option>
                  {counties.map(county => (
                    <option key={county} value={county}>{county}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-stone-700 mb-1">City</label>
                <select
                  value={selectedCity}
                  onChange={(e) => setSelectedCity(e.target.value)}
                  className="w-full px-3 py-2 border border-stone-200 rounded-lg focus:ring-2 focus:ring-amber-500"
                >
                  <option value="">All Cities</option>
                  {cities.map(city => (
                    <option key={city} value={city}>{city}</option>
                  ))}
                </select>
              </div>

              <div className="flex items-end">
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={verifiedOnly}
                    onChange={(e) => setVerifiedOnly(e.target.checked)}
                    className="w-5 h-5 rounded border-stone-300 text-amber-600 focus:ring-amber-500"
                  />
                  <span className="text-sm text-stone-700">Verified only</span>
                </label>
              </div>

              <div className="flex items-end">
                <button
                  onClick={clearFilters}
                  className="w-full px-4 py-2 text-sm text-stone-600 hover:text-stone-800 hover:bg-stone-100 rounded-lg transition-colors"
                >
                  Clear all filters
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Results Count */}
        <div className="flex items-center justify-between mb-4">
          <p className="text-sm text-stone-600">
            Showing {filteredStreets.length} of {streets.length} streets
          </p>
        </div>

        {/* Results */}
        {isLoading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-8 h-8 text-amber-600 animate-spin" />
          </div>
        ) : filteredStreets.length === 0 ? (
          <div className="text-center py-20 bg-white rounded-xl border border-stone-200">
            <Search className="w-16 h-16 text-stone-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-stone-800 mb-2">No streets found</h3>
            <p className="text-stone-600 mb-4">Try adjusting your search or filters</p>
            <button
              onClick={clearFilters}
              className="px-4 py-2 text-amber-700 hover:text-amber-800 font-medium"
            >
              Clear all filters
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredStreets.map((street) => (
              <Link
                key={street.id}
                to={`/street/${street.id}`}
                className="bg-white rounded-xl p-5 border border-stone-200 hover:border-amber-200 hover:shadow-md transition-all group"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center space-x-2 text-sm text-stone-500">
                    <MapPin className="w-4 h-4 text-amber-600" />
                    <span>{street.city || street.county}</span>
                  </div>
                  {street.etymology_verified && (
                    <CheckCircle className="w-5 h-5 text-green-600" />
                  )}
                </div>

                <h3 className="text-lg font-semibold text-stone-800 group-hover:text-amber-700 transition-colors mb-2">
                  {street.name}
                </h3>

                {street.etymology_suggestion ? (
                  <p className="text-sm text-stone-600 line-clamp-2 mb-3">
                    {street.etymology_suggestion}
                  </p>
                ) : (
                  <p className="text-sm text-stone-400 italic mb-3">
                    Etymology not yet researched
                  </p>
                )}

                <div className="flex items-center justify-between text-xs text-stone-500">
                  {street.first_recorded_date && (
                    <div className="flex items-center space-x-1">
                      <Clock className="w-3 h-3" />
                      <span>{street.first_recorded_date}</span>
                    </div>
                  )}
                  {street.postcode_area && (
                    <span className="px-2 py-0.5 bg-stone-100 rounded">
                      {street.postcode_area}
                    </span>
                  )}
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
