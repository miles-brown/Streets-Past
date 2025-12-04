import { Link } from 'react-router-dom';
import { MapPin, Mail, BookOpen, Github, Twitter } from 'lucide-react';

export function Footer() {
  return (
    <footer className="bg-stone-900 text-stone-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center space-x-2 mb-4">
              <div className="w-10 h-10 bg-gradient-to-br from-amber-600 to-amber-800 rounded-lg flex items-center justify-center">
                <MapPin className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="text-lg font-serif font-bold text-white">Street Etymology UK</h2>
                <p className="text-xs text-stone-400">Uncovering the stories behind our streets</p>
              </div>
            </div>
            <p className="text-sm text-stone-400 max-w-md mb-4">
              Exploring the rich linguistic heritage embedded in British street names. 
              From Roman roads to Victorian terraces, discover the etymology that connects 
              us to our past.
            </p>
            <div className="flex space-x-4">
              <a href="#" className="text-stone-400 hover:text-amber-500 transition-colors">
                <Twitter className="w-5 h-5" />
              </a>
              <a href="#" className="text-stone-400 hover:text-amber-500 transition-colors">
                <Github className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">
              Explore
            </h3>
            <ul className="space-y-2">
              <li>
                <Link to="/search" className="text-sm text-stone-400 hover:text-amber-500 transition-colors">
                  Search Streets
                </Link>
              </li>
              <li>
                <Link to="/map" className="text-sm text-stone-400 hover:text-amber-500 transition-colors">
                  Interactive Map
                </Link>
              </li>
              <li>
                <Link to="/about" className="text-sm text-stone-400 hover:text-amber-500 transition-colors">
                  About the Project
                </Link>
              </li>
              <li>
                <Link to="/contribute" className="text-sm text-stone-400 hover:text-amber-500 transition-colors">
                  Contribute
                </Link>
              </li>
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">
              Legal
            </h3>
            <ul className="space-y-2">
              <li>
                <Link to="/privacy" className="text-sm text-stone-400 hover:text-amber-500 transition-colors">
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link to="/terms" className="text-sm text-stone-400 hover:text-amber-500 transition-colors">
                  Terms of Service
                </Link>
              </li>
              <li>
                <a 
                  href="mailto:contact@streetetymology.co.uk" 
                  className="text-sm text-stone-400 hover:text-amber-500 transition-colors flex items-center space-x-1"
                >
                  <Mail className="w-4 h-4" />
                  <span>Contact</span>
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="mt-12 pt-8 border-t border-stone-800">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
            <p className="text-xs text-stone-500">
              2024 Street Etymology UK. Built with data from Ordnance Survey Open Data.
            </p>
            <div className="flex items-center space-x-2 text-xs text-stone-500">
              <BookOpen className="w-4 h-4" />
              <span>Open source project for etymological research</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
