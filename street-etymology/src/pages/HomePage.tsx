import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { SearchBar } from '../components/SearchBar';
import { MapView } from '../components/MapView';
import { NewsletterSignup } from '../components/NewsletterSignup';
import { supabase, Street } from '../lib/supabase';
import { 
  MapPin, 
  BookOpen, 
  Users, 
  Clock, 
  ArrowRight, 
  ChevronRight,
  Landmark,
  Scroll
} from 'lucide-react';

export function HomePage() {
  const [featuredStreets, setFeaturedStreets] = useState<Street[]>([]);
  const [stats, setStats] = useState({ streets: 0, contributions: 0, cities: 0 });

  useEffect(() => {
    async function loadData() {
      // Load featured streets with verified etymology
      const { data: streets } = await supabase
        .from('streets')
        .select('*')
        .eq('etymology_verified', true)
        .not('etymology_suggestion', 'is', null)
        .limit(6);

      if (streets) setFeaturedStreets(streets);

      // Load stats
      const { count: streetCount } = await supabase
        .from('streets')
        .select('*', { count: 'exact', head: true });

      const { count: contributionCount } = await supabase
        .from('contributions')
        .select('*', { count: 'exact', head: true });

      const { data: cities } = await supabase
        .from('streets')
        .select('city')
        .not('city', 'is', null);

      const uniqueCities = new Set(cities?.map(c => c.city)).size;

      setStats({
        streets: streetCount || 0,
        contributions: contributionCount || 0,
        cities: uniqueCities,
      });
    }

    loadData();
  }, []);

  return (
    <div className="min-h-screen bg-stone-50">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-stone-900 via-stone-800 to-amber-900 text-white overflow-hidden">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PHBhdGggZD0iTTM2IDM0djItSDI0di0yaDEyek0zNiAyNHYySDI0di0yaDEyeiIvPjwvZz48L2c+PC9zdmc+')] opacity-40"></div>
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 lg:py-32">
          <div className="text-center max-w-4xl mx-auto">
            <div className="inline-flex items-center space-x-2 bg-amber-800/30 text-amber-200 px-4 py-2 rounded-full text-sm mb-6">
              <Scroll className="w-4 h-4" />
              <span>Exploring the etymology of British streets since 2024</span>
            </div>
            
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-serif font-bold mb-6 leading-tight">
              Discover the Stories
              <span className="block text-amber-400">Behind Every Street</span>
            </h1>
            
            <p className="text-lg sm:text-xl text-stone-300 mb-8 max-w-2xl mx-auto">
              Uncover the fascinating linguistic heritage embedded in UK street names. 
              From ancient Roman roads to Victorian terraces, explore the etymology that 
              connects us to our past.
            </p>

            <div className="max-w-2xl mx-auto mb-8">
              <SearchBar large placeholder="Search for a street name (e.g., Baker Street, Piccadilly)..." />
            </div>

            <div className="flex flex-wrap justify-center gap-4 text-sm">
              <Link 
                to="/search" 
                className="flex items-center space-x-2 px-6 py-3 bg-amber-600 hover:bg-amber-700 rounded-lg transition-colors font-medium"
              >
                <span>Browse All Streets</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link 
                to="/map" 
                className="flex items-center space-x-2 px-6 py-3 bg-white/10 hover:bg-white/20 rounded-lg transition-colors font-medium"
              >
                <MapPin className="w-4 h-4" />
                <span>Explore Map</span>
              </Link>
            </div>
          </div>
        </div>

        {/* Wave Divider */}
        <div className="absolute bottom-0 left-0 right-0">
          <svg viewBox="0 0 1440 80" fill="none" className="w-full h-20">
            <path fill="#fafaf9" d="M0,48L60,42.7C120,37,240,27,360,32C480,37,600,59,720,64C840,69,960,59,1080,48C1200,37,1320,27,1380,21.3L1440,16L1440,80L1380,80C1320,80,1200,80,1080,80C960,80,840,80,720,80C600,80,480,80,360,80C240,80,120,80,60,80L0,80Z"/>
          </svg>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-12 bg-stone-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-3 gap-8">
            <div className="text-center">
              <div className="text-3xl sm:text-4xl font-bold text-amber-700 mb-1">
                {stats.streets.toLocaleString()}
              </div>
              <div className="text-sm text-stone-600">Streets Catalogued</div>
            </div>
            <div className="text-center">
              <div className="text-3xl sm:text-4xl font-bold text-amber-700 mb-1">
                {stats.cities}
              </div>
              <div className="text-sm text-stone-600">UK Cities</div>
            </div>
            <div className="text-center">
              <div className="text-3xl sm:text-4xl font-bold text-amber-700 mb-1">
                {stats.contributions}
              </div>
              <div className="text-sm text-stone-600">Community Contributions</div>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Streets */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="text-2xl sm:text-3xl font-serif font-bold text-stone-800">
                Featured Etymologies
              </h2>
              <p className="text-stone-600 mt-1">
                Verified street name origins from across the UK
              </p>
            </div>
            <Link 
              to="/search" 
              className="hidden sm:flex items-center space-x-1 text-amber-700 hover:text-amber-800 font-medium"
            >
              <span>View all</span>
              <ChevronRight className="w-4 h-4" />
            </Link>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {featuredStreets.map((street) => (
              <Link
                key={street.id}
                to={`/street/${street.id}`}
                className="group bg-stone-50 rounded-xl p-6 hover:shadow-lg transition-all border border-stone-100 hover:border-amber-200"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <MapPin className="w-5 h-5 text-amber-600" />
                    <span className="text-sm text-stone-500">
                      {street.city}, {street.county}
                    </span>
                  </div>
                  <span className="px-2 py-0.5 text-xs font-medium bg-green-100 text-green-700 rounded-full">
                    Verified
                  </span>
                </div>
                
                <h3 className="text-xl font-semibold text-stone-800 mb-2 group-hover:text-amber-700 transition-colors">
                  {street.name}
                </h3>
                
                <p className="text-stone-600 text-sm line-clamp-3 mb-3">
                  {street.etymology_suggestion}
                </p>

                {street.first_recorded_date && (
                  <div className="flex items-center space-x-1 text-xs text-stone-500">
                    <Clock className="w-3 h-3" />
                    <span>First recorded: {street.first_recorded_date}</span>
                  </div>
                )}
              </Link>
            ))}
          </div>

          <div className="mt-8 text-center sm:hidden">
            <Link 
              to="/search" 
              className="inline-flex items-center space-x-2 px-6 py-3 bg-stone-100 hover:bg-stone-200 rounded-lg text-stone-700 font-medium transition-colors"
            >
              <span>View All Streets</span>
              <ChevronRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* Interactive Map Section */}
      <section className="py-16 bg-stone-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-8">
            <h2 className="text-2xl sm:text-3xl font-serif font-bold text-stone-800 mb-2">
              Explore the UK Map
            </h2>
            <p className="text-stone-600 max-w-2xl mx-auto">
              Navigate through British streets and discover their etymological origins. 
              Click on any marker to learn more about that street's history.
            </p>
          </div>

          <MapView height="500px" />
          
          <div className="mt-6 text-center">
            <Link 
              to="/map" 
              className="inline-flex items-center space-x-2 px-6 py-3 bg-amber-700 hover:bg-amber-800 text-white rounded-lg font-medium transition-colors"
            >
              <MapPin className="w-5 h-5" />
              <span>Open Full Map</span>
            </Link>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-2xl sm:text-3xl font-serif font-bold text-stone-800 mb-2">
              How It Works
            </h2>
            <p className="text-stone-600">
              Join our community of etymology enthusiasts
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-amber-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <BookOpen className="w-8 h-8 text-amber-700" />
              </div>
              <h3 className="text-lg font-semibold text-stone-800 mb-2">Research</h3>
              <p className="text-stone-600 text-sm">
                Explore our comprehensive database of UK street names, complete with historical 
                etymologies sourced from academic research and local archives.
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-amber-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Landmark className="w-8 h-8 text-amber-700" />
              </div>
              <h3 className="text-lg font-semibold text-stone-800 mb-2">Discover</h3>
              <p className="text-stone-600 text-sm">
                Use our interactive map to explore streets geographically. Click on any location 
                to reveal the linguistic heritage hiding in plain sight.
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-amber-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Users className="w-8 h-8 text-amber-700" />
              </div>
              <h3 className="text-lg font-semibold text-stone-800 mb-2">Contribute</h3>
              <p className="text-stone-600 text-sm">
                Share your knowledge with the community. Submit etymology suggestions for streets 
                and help us build the most comprehensive street name database.
              </p>
            </div>
          </div>

          <div className="mt-12 text-center">
            <Link 
              to="/contribute" 
              className="inline-flex items-center space-x-2 px-6 py-3 bg-stone-800 hover:bg-stone-900 text-white rounded-lg font-medium transition-colors"
            >
              <span>Start Contributing</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* Newsletter */}
      <section className="py-16 bg-stone-100">
        <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
          <NewsletterSignup />
        </div>
      </section>
    </div>
  );
}
