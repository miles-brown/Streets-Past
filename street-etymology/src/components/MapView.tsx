import { useEffect, useRef, useState } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { supabase, Street } from '../lib/supabase';
import { Loader2 } from 'lucide-react';

interface MapViewProps {
  selectedStreet?: Street | null;
  onStreetSelect?: (street: Street) => void;
  height?: string;
}

export function MapView({ selectedStreet, onStreetSelect, height = '500px' }: MapViewProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const markersRef = useRef<maplibregl.Marker[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [streets, setStreets] = useState<Street[]>([]);

  // Load streets data
  useEffect(() => {
    async function loadStreets() {
      try {
        const { data, error } = await supabase
          .from('streets')
          .select('*')
          .not('latitude', 'is', null)
          .not('longitude', 'is', null);

        if (error) throw error;
        setStreets(data || []);
      } catch (error) {
        console.error('Error loading streets:', error);
      }
    }

    loadStreets();
  }, []);

  // Initialize map
  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: {
        version: 8,
        sources: {
          osm: {
            type: 'raster',
            tiles: [
              'https://a.tile.openstreetmap.org/{z}/{x}/{y}.png',
              'https://b.tile.openstreetmap.org/{z}/{x}/{y}.png',
              'https://c.tile.openstreetmap.org/{z}/{x}/{y}.png',
            ],
            tileSize: 256,
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
          },
        },
        layers: [
          {
            id: 'osm-tiles',
            type: 'raster',
            source: 'osm',
            minzoom: 0,
            maxzoom: 19,
          },
        ],
      },
      center: [-2.5, 54.0], // Center of UK
      zoom: 5.5,
      maxBounds: [
        [-12, 49], // Southwest corner of UK bounds
        [3, 61],   // Northeast corner of UK bounds
      ],
    });

    map.current.addControl(new maplibregl.NavigationControl(), 'top-right');
    map.current.addControl(new maplibregl.ScaleControl(), 'bottom-left');

    map.current.on('load', () => {
      setIsLoading(false);
    });

    return () => {
      if (map.current) {
        map.current.remove();
        map.current = null;
      }
    };
  }, []);

  // Add markers when streets data changes
  useEffect(() => {
    if (!map.current || isLoading || streets.length === 0) return;

    // Clear existing markers
    markersRef.current.forEach(marker => marker.remove());
    markersRef.current = [];

    // Add new markers
    streets.forEach((street) => {
      if (!street.latitude || !street.longitude) return;

      const el = document.createElement('div');
      el.className = 'street-marker';
      el.style.cssText = `
        width: 24px;
        height: 24px;
        background: linear-gradient(135deg, #b45309 0%, #92400e 100%);
        border: 2px solid white;
        border-radius: 50%;
        cursor: pointer;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        transition: transform 0.2s;
      `;
      el.addEventListener('mouseenter', () => {
        el.style.transform = 'scale(1.2)';
      });
      el.addEventListener('mouseleave', () => {
        el.style.transform = 'scale(1)';
      });

      const popup = new maplibregl.Popup({
        offset: 25,
        closeButton: true,
        maxWidth: '300px',
      }).setHTML(`
        <div style="font-family: system-ui, sans-serif; padding: 8px;">
          <h3 style="font-weight: 600; color: #292524; margin: 0 0 4px 0; font-size: 14px;">
            ${street.name}
          </h3>
          <p style="color: #78716c; margin: 0 0 8px 0; font-size: 12px;">
            ${[street.city, street.county].filter(Boolean).join(', ')}
          </p>
          ${street.etymology_suggestion ? `
            <p style="color: #57534e; margin: 0; font-size: 12px; line-height: 1.4;">
              ${street.etymology_suggestion.substring(0, 150)}${street.etymology_suggestion.length > 150 ? '...' : ''}
            </p>
          ` : ''}
          <a href="/street/${street.id}" 
             style="display: inline-block; margin-top: 8px; color: #b45309; font-size: 12px; font-weight: 500; text-decoration: none;">
            View Details
          </a>
        </div>
      `);

      const marker = new maplibregl.Marker({ element: el })
        .setLngLat([street.longitude, street.latitude])
        .setPopup(popup)
        .addTo(map.current!);

      el.addEventListener('click', () => {
        if (onStreetSelect) {
          onStreetSelect(street);
        }
      });

      markersRef.current.push(marker);
    });
  }, [streets, isLoading, onStreetSelect]);

  // Fly to selected street
  useEffect(() => {
    if (!map.current || !selectedStreet?.latitude || !selectedStreet?.longitude) return;

    map.current.flyTo({
      center: [selectedStreet.longitude, selectedStreet.latitude],
      zoom: 14,
      duration: 1500,
    });

    // Open popup for selected street
    const marker = markersRef.current.find((m) => {
      const lngLat = m.getLngLat();
      return lngLat.lng === selectedStreet.longitude && lngLat.lat === selectedStreet.latitude;
    });

    if (marker) {
      marker.togglePopup();
    }
  }, [selectedStreet]);

  return (
    <div className="relative rounded-xl overflow-hidden border border-stone-200" style={{ height }}>
      {isLoading && (
        <div className="absolute inset-0 bg-stone-100 flex items-center justify-center z-10">
          <div className="flex flex-col items-center">
            <Loader2 className="w-10 h-10 text-amber-600 animate-spin mb-3" />
            <p className="text-stone-600 font-medium">Loading map...</p>
          </div>
        </div>
      )}
      <div ref={mapContainer} className="w-full h-full" />
      
      {/* Legend */}
      <div className="absolute bottom-4 right-4 bg-white rounded-lg shadow-lg p-3 text-sm">
        <div className="flex items-center space-x-2 mb-2">
          <div className="w-4 h-4 rounded-full bg-gradient-to-br from-amber-600 to-amber-800 border border-white shadow"></div>
          <span className="text-stone-700">Street Location</span>
        </div>
        <p className="text-xs text-stone-500">{streets.length} streets mapped</p>
      </div>
    </div>
  );
}
