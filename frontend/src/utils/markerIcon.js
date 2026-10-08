// src/utils/markerIcon.js
// Helper to generate a circular photo marker with status border for Google Maps
// Returns an object compatible with @react-google-maps/api Marker `icon` prop.

/**
 * Map status strings to border colors.
 */
const STATUS_COLORS = {
  Identified: '#3b82f6', // blue-500
  Reunited: '#10b981',   // green-500
  Missing: '#ef4444',    // red-500
  default: '#9ca3af'     // gray-400
};

/**
 * Encode an SVG string as a data‑URI.
 * @param {string} svg
 * @returns {string}
 */
function svgToDataUrl(svg) {
  const encoded = encodeURIComponent(svg)
    .replace(/'/g, "%27")
    .replace(/"/g, "%22");
  return `data:image/svg+xml;charset=UTF-8,${encoded}`;
}

/**
 * Generate a custom marker icon.
 *
 * @param {Object} params
 * @param {string} params.photo   URL of the person's photo (or placeholder).
 * @param {string} params.status Person status string.
 * @param {number} [params.size=48]  Desired icon size in pixels (square).
 * @returns {Object} Google Maps Icon configuration.
 */
export function createMarkerIcon({ photo, status, size = 48 }) {
  const borderColor = STATUS_COLORS[status] || STATUS_COLORS.default;
  const imgUrl = photo || 'https://via.placeholder.com/40?text=No+Img';
  const radius = size / 2 - 4; // inner circle radius
  const borderWidth = 4;

  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size + 10}">
      <defs>
        <clipPath id="clip">
          <circle cx="${size / 2}" cy="${size / 2}" r="${radius}" />
        </clipPath>
      </defs>
      <circle cx="${size / 2}" cy="${size / 2}" r="${radius + borderWidth}" fill="${borderColor}" />
      <image href="${imgUrl}" x="${borderWidth}" y="${borderWidth}" width="${radius * 2}" height="${radius * 2}" clip-path="url(#clip)" preserveAspectRatio="xMidYMid slice" />
      <path d="M${size / 2} ${size + 2} L${size / 2 - 4} ${size} L${size / 2 + 4} ${size}" fill="${borderColor}" />
    </svg>
  `;

  return {
    url: svgToDataUrl(svg),
    scaledSize: new window.google.maps.Size(size, size + 10),
    anchor: new window.google.maps.Point(size / 2, size + 10)
  };
}
