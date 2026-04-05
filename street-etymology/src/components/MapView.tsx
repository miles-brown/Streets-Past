import { useEffect, useRef, useState } from 'react';
import maplibregl from 'maplibre-gl';
import type { RasterTileSource } from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { useTheme } from 'next-themes';
import { supabase, Street } from '../lib/supabase';
import { Loader2 } from 'lucide-react';

interface MapViewProps {
  selectedStreet?: Street | null;
  onStreetSelect?: (street: Street) => void;
  height?: string;
}

const OSM_LIGHT_TILES = [
  'https://a.tile.openstreetmap.org/{z}/{x}/{y}.png',
  'https://b.tile.openstreetmap.org/{z}/{x}/{y}.png',
  'https://c.tile.openstreetmap.org/{z}/{x}/{y}.png',
];

/** Carto dark basemap — reads as “urban night” next to warm UI chrome */
const OSM_DARK_TILES = [
  'https://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png',
  'https://b.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png',
  'https://c.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png',
];

const ATTR_LIGHT =
  '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors';
const ATTR_DARK =
  '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>';

function escapeHtml(s: string | null | undefined) {
  const str = s == null ? '' : String(s);
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function buildPopupHtml(street: Street) {
  const title = escapeHtml(street.name ?? 'Unknown street');
  const meta = escapeHtml([street.city, street.county].filter(Boolean).join(', '));
  const rawEtym = street.etymology_suggestion;
  const etymText =
    rawEtym != null && String(rawEtym).length > 0
      ? String(rawEtym).substring(0, 150) + (String(rawEtym).length > 150 ? '…' : '')
      : '';
  const etym = etymText ? escapeHtml(etymText) : '';
  const etymBlock = etym
    ? `<p style="margin:0 0 8px 0;font-size:12px;line-height:1.4;color:hsl(var(--muted-foreground));">${etym}</p>`
    : '';
  return `
        <div style="font-family:system-ui,sans-serif;padding:8px;color:hsl(var(--foreground));">
          <h3 style="font-weight:600;color:hsl(var(--foreground));margin:0 0 4px 0;font-size:14px;">
            ${title}
          </h3>
          <p style="color:hsl(var(--muted-foreground));margin:0 0 8px 0;font-size:12px;">
            ${meta}
          </p>
          ${etymBlock}
          <a href="/street/${street.id}"
             style="display:inline-block;margin-top:4px;color:hsl(var(--primary));font-size:12px;font-weight:500;text-decoration:none;">
            View details
          </a>
        </div>
      `;
}

function markerStylesFromTheme() {
  const root = document.documentElement;
  const primary = getComputedStyle(root).getPropertyValue('--primary').trim() || '8 45% 38%';
  const card = getComputedStyle(root).getPropertyValue('--card').trim() || '30 40% 99%';
  return {
    background: `linear-gradient(135deg, hsl(${primary}) 0%, hsl(${primary} / 0.82) 100%)`,
    border: `2px solid hsl(${card})`,
    boxShadow: '0 2px 8px hsl(0 0% 0% / 0.25)',
  };
}

export function MapView({ selectedStreet, onStreetSelect, height = '500px' }: MapViewProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const markersRef = useRef<maplibregl.Marker[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [streets, setStreets] = useState<Street[]>([]);
  const { resolvedTheme } = useTheme();
  const mapTheme = resolvedTheme === 'dark' ? 'dark' : 'light';

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

  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    const tiles = OSM_LIGHT_TILES;
    const attribution = ATTR_LIGHT;

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: {
        version: 8,
        sources: {
          osm: {
            type: 'raster',
            tiles,
            tileSize: 256,
            attribution,
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
      center: [-2.5, 54.0],
      zoom: 5.5,
      maxBounds: [
        [-12, 49],
        [3, 61],
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

  useEffect(() => {
    if (!map.current || isLoading) return;
    const dark = mapTheme === 'dark';
    const tiles = dark ? OSM_DARK_TILES : OSM_LIGHT_TILES;
    const attribution = dark ? ATTR_DARK : ATTR_LIGHT;
    const source = map.current.getSource('osm') as RasterTileSource | undefined;
    if (source && source.type === 'raster') {
      source.setTiles(tiles);
    }
    const attrEl = mapContainer.current?.querySelector('.maplibregl-ctrl-attrib-inner');
    if (attrEl) {
      attrEl.innerHTML = attribution;
    }
  }, [mapTheme, isLoading]);

  useEffect(() => {
    if (!map.current || isLoading || streets.length === 0) return;

    markersRef.current.forEach((marker) => marker.remove());
    markersRef.current = [];

    const { background, border, boxShadow } = markerStylesFromTheme();

    streets.forEach((street) => {
      if (!street.latitude || !street.longitude) return;

      const el = document.createElement('div');
      el.className = 'street-marker';
      el.style.cssText = `
        width: 24px;
        height: 24px;
        background: ${background};
        border: ${border};
        border-radius: 50%;
        cursor: pointer;
        box-shadow: ${boxShadow};
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
      }).setHTML(buildPopupHtml(street));

      const marker = new maplibregl.Marker({ element: el })
        .setLngLat([street.longitude, street.latitude])
        .setPopup(popup)
        .addTo(map.current!);

      el.addEventListener('click', () => {
        onStreetSelect?.(street);
      });

      markersRef.current.push(marker);
    });
  }, [streets, isLoading, onStreetSelect, mapTheme]);

  useEffect(() => {
    if (!map.current || !selectedStreet?.latitude || !selectedStreet?.longitude) return;

    map.current.flyTo({
      center: [selectedStreet.longitude, selectedStreet.latitude],
      zoom: 14,
      duration: 1500,
    });

    const marker = markersRef.current.find((m) => {
      const lngLat = m.getLngLat();
      return lngLat.lng === selectedStreet.longitude && lngLat.lat === selectedStreet.latitude;
    });

    if (marker) {
      marker.togglePopup();
    }
  }, [selectedStreet]);

  const legendMarker = markerStylesFromTheme();

  return (
    <div className="relative overflow-hidden rounded-xl border border-border" style={{ height }}>
      {isLoading && (
        <div className="absolute inset-0 z-10 flex items-center justify-center bg-background/95 backdrop-blur-sm">
          <div className="flex flex-col items-center">
            <Loader2 className="mb-3 h-10 w-10 animate-spin text-primary" />
            <p className="font-medium text-muted-foreground">Loading map…</p>
          </div>
        </div>
      )}
      <div ref={mapContainer} className="h-full w-full" />

      <div className="surface-glass absolute bottom-4 right-4 rounded-lg p-3 text-sm shadow-paper dark:shadow-paper-dark">
        <div className="mb-2 flex items-center gap-2">
          <div
            className="h-4 w-4 rounded-full border-2 shadow-sm"
            style={{
              background: legendMarker.background,
              borderColor: 'hsl(var(--card))',
            }}
          />
          <span className="text-foreground">Street location</span>
        </div>
        <p className="font-mono text-xs text-muted-foreground">{streets.length} streets mapped</p>
      </div>
    </div>
  );
}
