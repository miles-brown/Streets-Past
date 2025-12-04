import { Link } from 'react-router-dom';
import { NewsletterSignup } from '../components/NewsletterSignup';
import {
  MapPin,
  BookOpen,
  Users,
  Globe,
  Database,
  Github,
  Mail,
  ArrowRight
} from 'lucide-react';

export function AboutPage() {
  return (
    <div className="min-h-screen bg-stone-50">
      {/* Hero */}
      <section className="bg-gradient-to-br from-stone-800 to-stone-900 text-white py-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl sm:text-5xl font-serif font-bold mb-4">
            About Street Etymology UK
          </h1>
          <p className="text-lg text-stone-300 max-w-2xl mx-auto">
            Uncovering the linguistic heritage embedded in British street names, 
            connecting communities to their historical roots through language.
          </p>
        </div>
      </section>

      {/* Mission */}
      <section className="py-16">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-white rounded-2xl shadow-sm border border-stone-200 p-8 md:p-12">
            <h2 className="text-2xl font-serif font-bold text-stone-800 mb-6">
              Our Mission
            </h2>
            <div className="prose prose-stone max-w-none">
              <p className="text-stone-700 leading-relaxed mb-4">
                Street names are living historical documents, encoding centuries of linguistic 
                evolution, cultural change, and social history. Every street corner tells a story 
                - from the Old English 'gata' (road) surviving in northern 'gates' to Norman French 
                influences in 'close' and 'court'.
              </p>
              <p className="text-stone-700 leading-relaxed mb-4">
                Street Etymology UK was founded to make this rich heritage accessible to everyone. 
                Whether you are a historian researching local place names, a linguist studying 
                language evolution, or simply curious about the street where you live, our 
                database provides comprehensive etymological information.
              </p>
              <p className="text-stone-700 leading-relaxed">
                We combine academic research with community knowledge, building the most 
                comprehensive database of UK street name origins. Our platform draws on sources 
                ranging from the English Place-Name Society publications to local historical 
                societies and community contributions.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-2xl font-serif font-bold text-stone-800 text-center mb-12">
            What We Offer
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-amber-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Database className="w-8 h-8 text-amber-700" />
              </div>
              <h3 className="text-lg font-semibold text-stone-800 mb-2">
                Comprehensive Database
              </h3>
              <p className="text-stone-600 text-sm">
                Thousands of UK street names with verified etymologies, covering 
                major cities and towns across England, Scotland, Wales, and Northern Ireland.
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-amber-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Globe className="w-8 h-8 text-amber-700" />
              </div>
              <h3 className="text-lg font-semibold text-stone-800 mb-2">
                Interactive Mapping
              </h3>
              <p className="text-stone-600 text-sm">
                Explore street etymologies geographically with our interactive map. 
                Discover linguistic patterns across regions and trace historical influences.
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-amber-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Users className="w-8 h-8 text-amber-700" />
              </div>
              <h3 className="text-lg font-semibold text-stone-800 mb-2">
                Community Contributions
              </h3>
              <p className="text-stone-600 text-sm">
                Share your knowledge and help expand our database. Local historians 
                and etymology enthusiasts can submit and verify street name origins.
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-amber-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <BookOpen className="w-8 h-8 text-amber-700" />
              </div>
              <h3 className="text-lg font-semibold text-stone-800 mb-2">
                Academic Sources
              </h3>
              <p className="text-stone-600 text-sm">
                All etymologies are backed by academic sources including English Place-Name 
                Society publications, Oxford Dictionary of English Place-Names, and more.
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-amber-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <MapPin className="w-8 h-8 text-amber-700" />
              </div>
              <h3 className="text-lg font-semibold text-stone-800 mb-2">
                Search & Filter
              </h3>
              <p className="text-stone-600 text-sm">
                Find streets by name, location, or etymological origin. Filter by 
                county, city, language of origin, or historical period.
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-amber-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Github className="w-8 h-8 text-amber-700" />
              </div>
              <h3 className="text-lg font-semibold text-stone-800 mb-2">
                Open Data
              </h3>
              <p className="text-stone-600 text-sm">
                Export data for research purposes. We believe in open access to 
                linguistic and historical information for the public good.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Data Sources */}
      <section className="py-16 bg-stone-100">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-2xl font-serif font-bold text-stone-800 text-center mb-8">
            Our Data Sources
          </h2>
          
          <div className="bg-white rounded-xl shadow-sm border border-stone-200 p-8">
            <ul className="space-y-4">
              <li className="flex items-start space-x-3">
                <BookOpen className="w-5 h-5 text-amber-600 mt-1 flex-shrink-0" />
                <div>
                  <h4 className="font-semibold text-stone-800">English Place-Name Society</h4>
                  <p className="text-sm text-stone-600">
                    Academic publications on English county place names and etymologies.
                  </p>
                </div>
              </li>
              <li className="flex items-start space-x-3">
                <BookOpen className="w-5 h-5 text-amber-600 mt-1 flex-shrink-0" />
                <div>
                  <h4 className="font-semibold text-stone-800">Oxford Dictionary of English Place-Names</h4>
                  <p className="text-sm text-stone-600">
                    Authoritative reference work on the etymology of English place names.
                  </p>
                </div>
              </li>
              <li className="flex items-start space-x-3">
                <BookOpen className="w-5 h-5 text-amber-600 mt-1 flex-shrink-0" />
                <div>
                  <h4 className="font-semibold text-stone-800">Ordnance Survey Open Data</h4>
                  <p className="text-sm text-stone-600">
                    Geographic and street name data from the national mapping agency.
                  </p>
                </div>
              </li>
              <li className="flex items-start space-x-3">
                <BookOpen className="w-5 h-5 text-amber-600 mt-1 flex-shrink-0" />
                <div>
                  <h4 className="font-semibold text-stone-800">Local History Societies</h4>
                  <p className="text-sm text-stone-600">
                    Research and publications from regional historical societies.
                  </p>
                </div>
              </li>
              <li className="flex items-start space-x-3">
                <BookOpen className="w-5 h-5 text-amber-600 mt-1 flex-shrink-0" />
                <div>
                  <h4 className="font-semibold text-stone-800">Community Contributions</h4>
                  <p className="text-sm text-stone-600">
                    Verified submissions from local historians and etymology enthusiasts.
                  </p>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </section>

      {/* Contact */}
      <section className="py-16">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-gradient-to-br from-amber-50 to-orange-50 rounded-2xl border border-amber-200 p-8 md:p-12">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-serif font-bold text-stone-800 mb-2">
                Get Involved
              </h2>
              <p className="text-stone-600">
                Join our community of etymology researchers and local historians
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white rounded-xl p-6 shadow-sm">
                <Mail className="w-8 h-8 text-amber-600 mb-3" />
                <h3 className="font-semibold text-stone-800 mb-2">Contact Us</h3>
                <p className="text-sm text-stone-600 mb-3">
                  Have questions or suggestions? We would love to hear from you.
                </p>
                <a 
                  href="mailto:contact@streetetymology.co.uk"
                  className="text-amber-700 hover:text-amber-800 font-medium text-sm"
                >
                  contact@streetetymology.co.uk
                </a>
              </div>

              <div className="bg-white rounded-xl p-6 shadow-sm">
                <Users className="w-8 h-8 text-amber-600 mb-3" />
                <h3 className="font-semibold text-stone-800 mb-2">Contribute</h3>
                <p className="text-sm text-stone-600 mb-3">
                  Share your knowledge of local street name histories.
                </p>
                <Link 
                  to="/register"
                  className="inline-flex items-center space-x-1 text-amber-700 hover:text-amber-800 font-medium text-sm"
                >
                  <span>Create an account</span>
                  <ArrowRight className="w-4 h-4" />
                </Link>
              </div>
            </div>
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
