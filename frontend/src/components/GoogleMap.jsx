import React, { useState, useMemo, useCallback } from 'react';
import { GoogleMap, LoadScript, Marker, MarkerClusterer, InfoWindow } from '@react-google-maps/api';
import { getMockPeople } from '../mock/peopleMock';

// Container style ensures the map fills its parent
const containerStyle = {
  width: '100%',
  height: '100%'
};

// Default centre – safe demo location (San Francisco)
const defaultCenter = { lat: 37.7749, lng: -122.4194 };

/**
 * ReunificationGoogleMap – enhanced Google Maps wrapper.
 * Features:
 *   • Marker clustering via @react-google-maps/api's MarkerClusterer
 *   • Search (name, ID, location)
 *   • Status filters (All, Identified, Reunited, Missing)
 *   • Side panel list with lazy‑loaded avatars
 *   • InfoWindow pop‑up for selected person
 *   • Graceful handling of missing/invalid coordinates & photos
 */
export default function ReunificationGoogleMap({ center, markers = [], onLoad }) {
  // Load mock data – adjustable count for testing (e.g., 1, 10, 50, 100)
  const allPeople = useMemo(() => getMockPeople(100), []);

  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  const [selectedId, setSelectedId] = useState(null);
  const [mapInstance, setMapInstance] = useState(null);

  const mapCenter = center || defaultCenter;
  const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;

  // Filter people based on search term and status filter
  const filteredPeople = useMemo(() => {
    return allPeople.filter(p => {
      // Discard records with invalid coordinates
      if (typeof p.latitude !== 'number' || typeof p.longitude !== 'number') return false;

      // Apply status filter
      if (statusFilter !== 'All' && p.status !== statusFilter) return false;

      // Search term matching (case‑insensitive)
      if (!searchTerm) return true;
      const term = searchTerm.toLowerCase();
      return (
        (p.name && p.name.toLowerCase().includes(term)) ||
        String(p.id).includes(term) ||
        (p.locationName && p.locationName.toLowerCase().includes(term))
      );
    });
  }, [allPeople, searchTerm, statusFilter]);

  // Transform filtered people into marker objects
  const markerData = filteredPeople.map(p => ({
    id: p.id,
    position: { lat: p.latitude, lng: p.longitude },
    person: p
  }));

  // Map load handler – keep a reference for programmatic actions
  const handleMapLoad = useCallback(map => {
    setMapInstance(map);
    if (onLoad) onLoad(map);
  }, [onLoad]);

  // When a list entry is clicked, centre map and open its InfoWindow
  const handleSelectPerson = (person) => {
    setSelectedId(person.id);
    if (mapInstance) {
      mapInstance.panTo({ lat: person.latitude, lng: person.longitude });
      mapInstance.setZoom(15);
    }
  };

  // Render fallback UI when API key is missing
  if (!apiKey) {
    return (
      <div className="flex items-center justify-center h-full text-sm text-gray-600">
        Google Maps API key not configured. Set VITE_GOOGLE_MAPS_API_KEY in your .env file.
      </div>
    );
  }

  return (
    <div className="flex flex-col md:flex-row h-[500px] md:h-[600px]">
      {/* Side panel with search, filters, and list */}
      <aside className="w-full md:w-64 bg-white border-r border-gray-200 overflow-y-auto p-2">
        <input
          type="text"
          placeholder="Search name, ID, location"
          className="w-full rounded border px-2 py-1 text-sm mb-2"
          value={searchTerm}
          onChange={e => setSearchTerm(e.target.value)}
        />
        <div className="flex space-x-1 mb-2 text-sm">
          {['All', 'Identified', 'Reunited', 'Missing'].map(f => (
            <button
              key={f}
              className={`px-2 py-1 rounded ${statusFilter === f ? 'bg-primary text-white' : 'bg-gray-100'}`}
              onClick={() => setStatusFilter(f)}
            >
              {f}
            </button>
          ))}
        </div>
        <ul className="space-y-2 max-h-[calc(100vh-180px)] overflow-y-auto">
          {filteredPeople.map(p => (
            <li
              key={p.id}
              className="flex items-center space-x-2 p-1 hover:bg-gray-50 cursor-pointer"
              onClick={() => handleSelectPerson(p)}
            >
              <img
                src={p.photo || 'https://via.placeholder.com/40?text=No+Img'}
                alt={p.name}
                className="w-8 h-8 rounded-full object-cover"
                loading="lazy"
              />
              <div className="flex-1 min-w-0">
                <p className="text-xs font-medium truncate" title={p.name}>{p.name}</p>
                <p className="text-xs text-gray-500">{p.status}</p>
              </div>
            </li>
          ))}
        </ul>
      </aside>

      {/* Map container */}
      <div className="flex-1 relative">
        <LoadScript googleMapsApiKey={apiKey}>
          <GoogleMap
            mapContainerStyle={containerStyle}
            center={mapCenter}
            zoom={13}
            onLoad={handleMapLoad}
            options={{
              fullscreenControl: false,
              mapTypeControl: false,
              streetViewControl: false,
            }}
          >
            <MarkerClusterer>
              {(clusterer) =>
                markerData.map(m => (
                  <Marker
                    key={m.id}
                    position={m.position}
                    clusterer={clusterer}
                    onClick={() => setSelectedId(m.id)}
                  />
                ))
              }
            </MarkerClusterer>

            {markerData.map(m => {
              if (m.id !== selectedId) return null;
              const p = m.person;
              return (
                <InfoWindow
                  key={m.id}
                  position={m.position}
                  onCloseClick={() => setSelectedId(null)}
                >
                  <div className="flex flex-col items-center">
                    <img
                      src={p.photo || 'https://via.placeholder.com/80?text=No+Img'}
                      alt={p.name}
                      className="w-16 h-16 rounded-full object-cover mb-2"
                      loading="lazy"
                    />
                    <p className="font-medium text-sm">{p.name}</p>
                    <p className="text-xs text-gray-600">{p.status}</p>
                    <p className="text-xs text-gray-5 0">{p.locationName}</p>
                  </div>
                </InfoWindow>
              );
            })}
          </GoogleMap>
        </LoadScript>
      </div>
    </div>
  );
}
