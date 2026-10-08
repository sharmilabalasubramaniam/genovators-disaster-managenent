import React, { useState } from 'react';
import { Marker, InfoWindow } from '@react-google-maps/api';
import placeholderImg from '../assets/placeholder.png'; // fallback image (ensure placeholder exists or use URL)

// Choose marker color based on status
const getMarkerIcon = (status) => {
  switch (status) {
    case 'Identified':
      return 'https://maps.google.com/mapfiles/ms/icons/blue-dot.png';
    case 'Reunited':
      return 'https://maps.google.com/mapfiles/ms/icons/green-dot.png';
    case 'Missing':
      return 'https://maps.google.com/mapfiles/ms/icons/red-dot.png';
    default:
      return 'https://maps.google.com/mapfiles/ms/icons/yellow-dot.png';
  }
};

export default function PersonMarker({ person }) {
  const [open, setOpen] = useState(false);

  // Guard against invalid coordinates
  const validCoord =
    typeof person.latitude === 'number' && typeof person.longitude === 'number';
  if (!validCoord) return null;

  const handleToggle = () => setOpen((prev) => !prev);

  const photoUrl = person.photo ? person.photo : 'https://via.placeholder.com/80?text=No+Photo';

  return (
    <>
      <Marker
        position={{ lat: person.latitude, lng: person.longitude }}
        icon={getMarkerIcon(person.status)}
        onClick={handleToggle}
      />
      {open && (
        <InfoWindow position={{ lat: person.latitude, lng: person.longitude }} onCloseClick={handleToggle}>
          <div className="flex flex-col items-center p-2 w-56">
            <img
              src={photoUrl}
              alt={person.name}
              className="w-16 h-16 rounded-full object-cover mb-2"
            />
            <h4 className="text-sm font-semibold text-gray-900">{person.name || person.id}</h4>
            <p className="text-xs text-gray-600">Status: {person.status}</p>
            <p className="text-xs text-gray-600">Location: {person.locationName}</p>
            <p className="text-xs text-gray-600">Identified: {new Date(person.identifiedAt).toLocaleString()}</p>
            <button
              className="mt-2 w-full bg-primary text-white text-xs py-1 rounded"
              onClick={() => alert('View profile for ' + person.id)}
            >
              View Profile
            </button>
          </div>
        </InfoWindow>
      )}
    </>
  );
}
