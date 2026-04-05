import { useState, useEffect, useRef } from 'react';
import { Search, MapPin, X, Loader2 } from 'lucide-react';
import { supabase, Street } from '../lib/supabase';
import { useNavigate } from 'react-router-dom';

interface SearchBarProps {
  large?: boolean;
  onSelect?: (street: Street) => void;
  placeholder?: string;
}

export function SearchBar({
  large = false,
  onSelect,
  placeholder = 'Search UK street names…',
}: SearchBarProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Street[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

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

  const inputClass = `block w-full rounded-xl border border-border bg-card text-foreground placeholder:text-muted-foreground transition-all focus:border-primary/50 focus:outline-none focus:ring-2 focus:ring-ring/40 ${
    large ? 'py-5 pl-14 pr-12 text-lg shadow-paper dark:shadow-paper-dark' : 'py-3 pl-12 pr-10 text-base'
  }`;

  return (
    <div className="relative w-full">
      <div className={`relative ${large ? '' : ''}`}>
        <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-4">
          {isLoading ? (
            <Loader2 className={`${large ? 'h-6 w-6' : 'h-5 w-5'} animate-spin text-primary`} />
          ) : (
            <Search className={`${large ? 'h-6 w-6' : 'h-5 w-5'} text-muted-foreground`} />
          )}
        </div>
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => query.length >= 2 && setIsOpen(true)}
          placeholder={placeholder}
          className={inputClass}
        />
        {query && (
          <button type="button" onClick={clearQuery} className="absolute inset-y-0 right-0 flex items-center pr-4">
            <X className={`${large ? 'h-6 w-6' : 'h-5 w-5'} text-muted-foreground hover:text-foreground`} />
          </button>
        )}
      </div>

      {isOpen && results.length > 0 && (
        <div
          ref={dropdownRef}
          className="absolute z-50 mt-2 w-full overflow-hidden rounded-xl border border-border bg-popover text-popover-foreground shadow-paper dark:shadow-paper-dark"
        >
          <ul className="max-h-96 overflow-y-auto">
            {results.map((street) => (
              <li key={street.id}>
                <button
                  type="button"
                  onClick={() => handleSelect(street)}
                  className="flex w-full items-start gap-3 px-4 py-3 text-left transition-colors hover:bg-muted/80"
                >
                  <MapPin className="mt-0.5 h-5 w-5 shrink-0 text-primary" />
                  <div className="min-w-0 flex-1">
                    <p className="truncate font-medium text-foreground">{street.name}</p>
                    <p className="truncate text-sm text-muted-foreground">
                      {[street.city, street.county, street.postcode_area].filter(Boolean).join(', ')}
                    </p>
                    {street.etymology_suggestion && (
                      <p className="mt-1 line-clamp-1 text-xs text-muted-foreground">{street.etymology_suggestion}</p>
                    )}
                  </div>
                  {street.etymology_verified && (
                    <span className="shrink-0 rounded-full bg-emerald-500/15 px-2 py-0.5 text-xs font-medium text-emerald-800 dark:bg-emerald-500/20 dark:text-emerald-300">
                      Verified
                    </span>
                  )}
                </button>
              </li>
            ))}
          </ul>
          <div className="border-t border-border bg-muted/40 px-4 py-2">
            <p className="text-xs text-muted-foreground">
              {results.length} result{results.length !== 1 ? 's' : ''}
            </p>
          </div>
        </div>
      )}

      {isOpen && query.length >= 2 && results.length === 0 && !isLoading && (
        <div
          ref={dropdownRef}
          className="absolute z-50 mt-2 w-full rounded-xl border border-border bg-popover p-6 text-center shadow-paper dark:shadow-paper-dark"
        >
          <Search className="mx-auto mb-3 h-12 w-12 text-muted-foreground/50" />
          <p className="font-medium text-foreground">No streets found</p>
          <p className="mt-1 text-sm text-muted-foreground">Try another spelling or place name.</p>
        </div>
      )}
    </div>
  );
}
