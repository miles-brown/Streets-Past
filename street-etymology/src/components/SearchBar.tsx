import { useState, useEffect, useRef } from 'react';
import { Search, MapPin, X, Loader2 } from 'lucide-react';
import { supabase, Street } from '../lib/supabase';
import { useNavigate } from 'react-router-dom';

interface SearchBarProps {
  large?: boolean;
  onSelect?: (street: Street) => void;
  placeholder?: string;
}

export function SearchBar({ large = false, onSelect, placeholder = "Search UK street names..." }: SearchBarProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Street[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  // Debounced search
  useEffect(() => {
    if (query.length < 2) {
      setResults([]);
      setIsOpen(false);
      return;
    }

    const timeoutId = setTimeout(async () => {
      setIsLoading(true);
      try {
        const { data, error } = await supabase
          .from('streets')
          .select('*')
          .ilike('name', `%${query}%`)
          .order('name')
          .limit(10);

        if (error) throw error;
        setResults(data || []);
        setIsOpen(true);
      } catch (error) {
        console.error('Search error:', error);
        setResults([]);
      } finally {
        setIsLoading(false);
      }
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [query]);

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (street: Street) => {
    if (onSelect) {
      onSelect(street);
    } else {
      navigate(`/street/${street.id}`);
    }
    setQuery('');
    setIsOpen(false);
  };

  const clearQuery = () => {
    setQuery('');
    setResults([]);
    setIsOpen(false);
    inputRef.current?.focus();
  };

  return (
    <div className="relative w-full">
      <div className={`relative ${large ? 'shadow-lg' : 'shadow-sm'}`}>
        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
          {isLoading ? (
            <Loader2 className={`${large ? 'w-6 h-6' : 'w-5 h-5'} text-amber-600 animate-spin`} />
          ) : (
            <Search className={`${large ? 'w-6 h-6' : 'w-5 h-5'} text-stone-400`} />
          )}
        </div>
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => query.length >= 2 && setIsOpen(true)}
          placeholder={placeholder}
          className={`block w-full bg-white border border-stone-200 rounded-xl focus:ring-2 focus:ring-amber-500 focus:border-transparent transition-all ${
            large 
              ? 'pl-14 pr-12 py-5 text-lg' 
              : 'pl-12 pr-10 py-3 text-base'
          }`}
        />
        {query && (
          <button
            onClick={clearQuery}
            className="absolute inset-y-0 right-0 pr-4 flex items-center"
          >
            <X className={`${large ? 'w-6 h-6' : 'w-5 h-5'} text-stone-400 hover:text-stone-600`} />
          </button>
        )}
      </div>

      {/* Dropdown Results */}
      {isOpen && results.length > 0 && (
        <div
          ref={dropdownRef}
          className="absolute z-50 w-full mt-2 bg-white rounded-xl shadow-xl border border-stone-200 overflow-hidden"
        >
          <ul className="max-h-96 overflow-y-auto">
            {results.map((street) => (
              <li key={street.id}>
                <button
                  onClick={() => handleSelect(street)}
                  className="w-full px-4 py-3 flex items-start space-x-3 hover:bg-amber-50 transition-colors text-left"
                >
                  <MapPin className="w-5 h-5 text-amber-600 mt-0.5 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-stone-900 truncate">{street.name}</p>
                    <p className="text-sm text-stone-500 truncate">
                      {[street.city, street.county, street.postcode_area].filter(Boolean).join(', ')}
                    </p>
                    {street.etymology_suggestion && (
                      <p className="text-xs text-stone-400 mt-1 line-clamp-1">
                        {street.etymology_suggestion}
                      </p>
                    )}
                  </div>
                  {street.etymology_verified && (
                    <span className="flex-shrink-0 px-2 py-0.5 text-xs font-medium bg-green-100 text-green-700 rounded-full">
                      Verified
                    </span>
                  )}
                </button>
              </li>
            ))}
          </ul>
          <div className="px-4 py-2 bg-stone-50 border-t border-stone-200">
            <p className="text-xs text-stone-500">
              {results.length} result{results.length !== 1 ? 's' : ''} found
            </p>
          </div>
        </div>
      )}

      {/* No Results */}
      {isOpen && query.length >= 2 && results.length === 0 && !isLoading && (
        <div
          ref={dropdownRef}
          className="absolute z-50 w-full mt-2 bg-white rounded-xl shadow-xl border border-stone-200 p-6 text-center"
        >
          <Search className="w-12 h-12 text-stone-300 mx-auto mb-3" />
          <p className="text-stone-600 font-medium">No streets found</p>
          <p className="text-sm text-stone-400 mt-1">Try a different search term</p>
        </div>
      )}
    </div>
  );
}
